use borsh::{BorshDeserialize, BorshSerialize};

use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint::ProgramResult,
    msg,
    program::{invoke, invoke_signed},
    program_error::ProgramError,
    pubkey::Pubkey,
    rent::Rent,
    system_instruction,
    sysvar::{clock::Clock, Sysvar},
};

use crate::{TimestampInstruction, VaultState};

pub fn process_instruction(
    program: &Pubkey,
    accounts: &[AccountInfo],
    mut data: &[u8],
) -> ProgramResult {
    match TimestampInstruction::deserialize(&mut data)? {
        TimestampInstruction::InitializeVault => initialize_vault(program, accounts),
        TimestampInstruction::CoinToss { bet_amount } => coin_toss(program, accounts, bet_amount),
    }
}

fn initialize_vault(program_id: &Pubkey, accounts: &[AccountInfo]) -> ProgramResult {
    let account_iter = &mut accounts.iter();
    let payer_account = next_account_info(account_iter)?;
    let vault_account = next_account_info(account_iter)?;
    let system_program = next_account_info(account_iter)?;

    if !payer_account.is_signer {
        msg!("Payer must sign the transaction");
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (vault_pda, bump) = Pubkey::find_program_address(&[b"vault"], program_id);

    if vault_pda != *vault_account.key {
        msg!("Invalid vault PDA");
        return Err(ProgramError::InvalidAccountData);
    }

    let rent = Rent::get()?;
    let vault_size = std::mem::size_of::<VaultState>();
    let rent_lamports = rent.minimum_balance(vault_size);

    let create_account_instruction = system_instruction::create_account(
        payer_account.key,
        vault_account.key,
        rent_lamports,
        vault_size as u64,
        program_id,
    );

    invoke_signed(
        &create_account_instruction,
        &[
            payer_account.clone(),
            vault_account.clone(),
            system_program.clone(),
        ],
        &[&[b"vault", &[bump]]],
    )?;

    let vault_state = VaultState {
        balance: 0,
        bump,
        rand: 0,
    };

    vault_state.serialize(&mut &mut vault_account.data.borrow_mut()[..])?;

    msg!("Vault initialized with PDA: {}", vault_pda);

    Ok(())
}

fn xorshift(mut x: u64) -> u64 {
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    x *= 0x2545F4914F6CDD1D;
    return x;
}

fn coin_toss(program_id: &Pubkey, accounts: &[AccountInfo], bet_amount: u64) -> ProgramResult {
    let account_iter = &mut accounts.iter();
    let clock_account = next_account_info(account_iter)?;
    let player_account = next_account_info(account_iter)?;
    let vault_account = next_account_info(account_iter)?;
    let system_program = next_account_info(account_iter)?;

    assert_eq!(*clock_account.key, solana_program::sysvar::clock::id());

    if !player_account.is_signer {
        msg!("Player must sign the transaction");
        return Err(ProgramError::MissingRequiredSignature);
    }

    let (vault_pda, _bump) = Pubkey::find_program_address(&[b"vault"], program_id);
    if vault_pda != *vault_account.key {
        msg!("Invalid vault PDA");
        return Err(ProgramError::InvalidAccountData);
    }

    if bet_amount == 0 {
        msg!("Bet amount must be greater than zero");
        return Err(ProgramError::InvalidArgument);
    }

    let mut vault_state = VaultState::deserialize(&mut &vault_account.data.borrow()[..])?;

    let clock = Clock::from_account_info(clock_account)?;
    vault_state.rand = vault_state.rand.wrapping_add(clock.unix_timestamp as u64);
    vault_state.rand = xorshift(vault_state.rand);
    let is_heads = vault_state.rand % 10 == 0;

    msg!("Bet amount: {} lamports", bet_amount);
    msg!("Vault balance before: {} lamports", vault_state.balance);

    if is_heads {
        msg!("Result: HEADS! Player wins {} lamports", bet_amount);

        if vault_account.lamports() < bet_amount {
            msg!("Vault has insufficient funds for payout");
            return Err(ProgramError::InsufficientFunds);
        }

        **vault_account.try_borrow_mut_lamports()? -= bet_amount;
        **player_account.try_borrow_mut_lamports()? += bet_amount;

        vault_state.balance = vault_account.lamports();
    } else {
        msg!("Result: TAILS! Player loses {} lamports", bet_amount);

        let transfer_instruction =
            system_instruction::transfer(player_account.key, vault_account.key, bet_amount);

        invoke(
            &transfer_instruction,
            &[
                player_account.clone(),
                vault_account.clone(),
                system_program.clone(),
            ],
        )?;

        vault_state.balance = vault_account.lamports();
    }

    vault_state.serialize(&mut &mut vault_account.data.borrow_mut()[..])?;

    msg!("Vault balance after: {} lamports", vault_state.balance);

    Ok(())
}
