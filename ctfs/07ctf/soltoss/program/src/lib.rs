mod entrypoint;
pub mod processor;

use borsh::{to_vec, BorshDeserialize, BorshSerialize};

use solana_program::{
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
};

#[derive(BorshDeserialize, BorshSerialize)]
pub enum TimestampInstruction {
    InitializeVault,
    CoinToss { bet_amount: u64 },
}

#[derive(BorshDeserialize, BorshSerialize)]
pub struct VaultState {
    pub balance: u64,
    pub bump: u8,
    pub rand: u64,
}

pub fn initialize_vault(program: Pubkey, payer: Pubkey, vault: Pubkey) -> Instruction {
    Instruction {
        program_id: program,
        accounts: vec![
            AccountMeta::new(payer, true),
            AccountMeta::new(vault, false),
            AccountMeta::new_readonly(solana_program::system_program::id(), false),
        ],
        data: to_vec(&TimestampInstruction::InitializeVault).unwrap(),
    }
}

pub fn coin_toss(program: Pubkey, player: Pubkey, vault: Pubkey, bet_amount: u64) -> Instruction {
    Instruction {
        program_id: program,
        accounts: vec![
            AccountMeta::new_readonly(solana_program::sysvar::clock::id(), false),
            AccountMeta::new(player, true),
            AccountMeta::new(vault, false),
            AccountMeta::new_readonly(solana_program::system_program::id(), false),
        ],
        data: to_vec(&TimestampInstruction::CoinToss { bet_amount }).unwrap(),
    }
}

pub fn find_vault_pda(program_id: &Pubkey) -> (Pubkey, u8) {
    Pubkey::find_program_address(&[b"vault"], program_id)
}
