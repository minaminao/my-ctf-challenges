use sol_ctf_framework::ChallengeBuilder;

use solana_sdk::{
    account::Account,
    pubkey::Pubkey,
    signature::{Keypair, Signer},
};

use solana_program::system_program;

use std::{
    error::Error,
    fs,
    io::Write,
    net::{TcpListener, TcpStream},
};

use soltoss::{find_vault_pda, initialize_vault};

/// Main entry point for the CTF server
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let listener = TcpListener::bind("0.0.0.0:5001")?;

    loop {
        let (stream, _) = listener.accept()?;

        tokio::spawn(async move {
            if let Err(e) = handle_connection(stream).await {
                eprintln!("handler error: {e}");
            }
        });
    }
}

/// Handle an individual client connection
async fn handle_connection(mut socket: TcpStream) -> Result<(), Box<dyn Error>> {
    let mut builder = ChallengeBuilder::try_from(socket.try_clone().unwrap()).unwrap();

    // === PROGRAM LOADING PHASE ===

    // Load the player's solve program from their submission
    let solve_pubkey = match builder.input_program() {
        Ok(pubkey) => pubkey,
        Err(e) => {
            writeln!(socket, "Error: cannot add solve program → {e}")?;
            return Ok(());
        }
    };

    // Load the main challenge program (soltoss.so)
    let challenge_program_key = Pubkey::new_unique();
    let challenge_program_pubkey = builder
        .add_program(&"soltoss.so", Some(challenge_program_key))
        .expect("Duplicate pubkey supplied");

    // === USER SETUP PHASE ===

    let player = Keypair::new();
    let deployer = Keypair::new();

    writeln!(
        socket,
        "challenge program address: {}",
        challenge_program_pubkey
    )?;
    writeln!(socket, "player address: {}", player.pubkey())?;

    // === ACCOUNT SETUP PHASE ===

    const INITIAL_DEPLOYER_BALANCE: u64 = 1_001_000_000_000; // 1001 SOL
    const INITIAL_PLAYER_BALANCE: u64 = 1_000_000_000; // 1 SOL

    builder.builder.add_account(
        deployer.pubkey(),
        Account::new(INITIAL_DEPLOYER_BALANCE, 0, &system_program::ID),
    );
    builder.builder.add_account(
        player.pubkey(),
        Account::new(INITIAL_PLAYER_BALANCE, 0, &system_program::ID),
    );

    // === CHALLENGE EXECUTION PHASE ===

    let mut challenge = builder.build().await;

    // Find the vault PDA
    let (vault_pda, _bump) = find_vault_pda(&challenge_program_pubkey);
    writeln!(socket, "vault PDA address: {}", vault_pda)?;

    // Initialize the vault PDA
    challenge
        .run_ixs_full(
            &[initialize_vault(
                challenge_program_pubkey,
                deployer.pubkey(),
                vault_pda,
            )],
            &[&deployer],
            &deployer.pubkey(),
        )
        .await?;

    // Fund the vault with some initial balance for payouts
    const VAULT_INITIAL_FUNDING: u64 = 1_000_000_000_000; // 1000 SOL
    challenge
        .run_ixs_full(
            &[solana_sdk::system_instruction::transfer(
                &deployer.pubkey(),
                &vault_pda,
                VAULT_INITIAL_FUNDING,
            )],
            &[&deployer],
            &deployer.pubkey(),
        )
        .await?;

    writeln!(
        socket,
        "Vault funded with {} lamports",
        VAULT_INITIAL_FUNDING
    )?;

    // Execute the player's solve program
    writeln!(
        socket,
        "You can execute your program up to 10 times to try to win at least 1000 SOL. Good luck!"
    )?;
    for _ in 0..10 {
        let ixs = challenge.read_instruction(solve_pubkey).unwrap();
        challenge
            .run_ixs_full(&[ixs], &[&player], &player.pubkey())
            .await?;
    }

    // === SOLUTION VALIDATION PHASE ===

    let balance = challenge
        .ctx
        .banks_client
        .get_account(player.pubkey())
        .await?
        .unwrap()
        .lamports;
    writeln!(socket, "lamports: {:?}", balance)?;

    let is_solved = balance >= 1_000_000_000_000; // 1000 SOL
    if is_solved {
        let flag = fs::read_to_string("flag.txt").unwrap();
        writeln!(socket, "\nFlag: {}", flag)?;
    } else {
        writeln!(
            socket,
            "Not solved. Need at least 1000 SOL, but have {} lamports ({:.9} SOL)",
            balance,
            balance as f64 / 1_000_000_000.0
        )?;
    }

    Ok(())
}
