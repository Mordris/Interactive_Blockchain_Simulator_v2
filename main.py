# main.py

import os
import json
import time # For delays or timing if needed

from blockchain import Blockchain
from transaction import Transaction
from utils.crypto_utils import generate_key_pair, sign_data, get_data_to_sign

# --- Wallet Configuration ---
WALLET_FILE = "cli_wallet.json"
currentUserKeys = {
    "private_key_pem": None,
    "public_key_pem": None,
    "name": "Default User" # Optional user-friendly name
}

def save_wallet():
    """Saves the current user's keys to the wallet file."""
    try:
        with open(WALLET_FILE, 'w') as f:
            json.dump(currentUserKeys, f, indent=4)
        print(f"Wallet saved to {WALLET_FILE}")
    except IOError:
        print(f"Error: Could not save wallet to {WALLET_FILE}")

def load_wallet():
    """Loads user keys from the wallet file if it exists."""
    global currentUserKeys
    if os.path.exists(WALLET_FILE):
        try:
            with open(WALLET_FILE, 'r') as f:
                data = json.load(f)
                # Basic validation of loaded data
                if "private_key_pem" in data and "public_key_pem" in data:
                    currentUserKeys = data
                    print(f"Wallet loaded for '{currentUserKeys.get('name', 'Unknown User')}' from {WALLET_FILE}")
                    return True
                else:
                    print(f"Error: Wallet file {WALLET_FILE} is malformed. Missing key data.")
                    return False
        except (IOError, json.JSONDecodeError):
            print(f"Error: Could not read or parse wallet file {WALLET_FILE}.")
            return False
    else:
        print(f"No wallet file found at {WALLET_FILE}. You'll need to generate keys.")
        return False

def generate_new_wallet():
    """Generates a new key pair and sets it as the current user's keys."""
    global currentUserKeys
    name = input("Enter a name for this new wallet (e.g., Alice, Bob): ").strip()
    if not name:
        name = f"User_{int(time.time())}" # Default name if empty

    priv_key, pub_key = generate_key_pair()
    currentUserKeys = {
        "private_key_pem": priv_key,
        "public_key_pem": pub_key,
        "name": name
    }
    print("\n--- New Key Pair Generated ---")
    print(f"Wallet Name: {currentUserKeys['name']}")
    print("Your NEW Public Key (Share this to receive funds):")
    print(currentUserKeys['public_key_pem'])
    print("\nIMPORTANT: Your NEW Private Key (Keep this SECRET and SAFE):")
    print(currentUserKeys['private_key_pem'])
    print("-----------------------------")
    save_wallet() # Auto-save the newly generated wallet

def display_current_wallet_info(chain_instance: Blockchain):
    if currentUserKeys["public_key_pem"]:
        print("\n--- Current Wallet Status ---")
        print(f"Wallet Name: {currentUserKeys.get('name', 'N/A')}")
        print(f"Your Public Key (Address):\n{currentUserKeys['public_key_pem']}")
        balance = chain_instance.get_balance(currentUserKeys['public_key_pem'])
        print(f"Your Current Balance: {balance:.4f} coins")
        print("-----------------------------")
    else:
        print("\nNo active wallet. Please generate or load one.")

def print_blockchain_details_cli(chain_instance: Blockchain):
    """Helper function to print blockchain state for CLI."""
    print("\n" + "="*10 + " Current Blockchain State (CLI) " + "="*10)
    if not chain_instance.chain:
        print("Blockchain is empty.")
        return

    print(f"Total blocks: {len(chain_instance.chain)}")
    print(f"Difficulty: {chain_instance.difficulty}")
    print(f"Mining Reward: {chain_instance.mining_reward}")

    for block in chain_instance.chain:
        print(f"\n--- Block #{block.index} ---")
        print(f"  Timestamp: {time.ctime(block.timestamp)}")
        print(f"  Nonce: {block.nonce}")
        print(f"  Hash: {block.hash[:40]}...")
        print(f"  Prev. Hash: {block.previous_hash[:40] if block.previous_hash != '0' else '0'}...")
        print(f"  Transactions ({len(block.transactions)}):")
        if block.transactions:
            for i, tx_dict in enumerate(block.transactions):
                tx = Transaction.from_dict(tx_dict) # Recreate Transaction object
                sender_display = "NETWORK (Reward)" if tx.sender_public_key == "network" else f"From: {tx.sender_public_key[:20]}..."
                recipient_display = f"To: {tx.recipient_public_key[:20]}..."
                sig_display = "Signed" if tx.signature else "N/A (Network)"
                print(f"    {i+1}. {sender_display}, {recipient_display}, Amount: {tx.amount}, Sig: {sig_display}")
        else:
            print("    - No transactions.")
    print("="*10 + " End of Blockchain State " + "="*10)


def main_cli():
    print("--- Simple Blockchain CLI (with Wallet) ---")
    
    blockchain_data_filename = "blockchain_data.json" # From app.py
    my_blockchain = Blockchain.load_from_file(blockchain_data_filename)

    if my_blockchain is None:
        print("\nNo existing blockchain found or error loading.")
        while True:
            try:
                difficulty_str = input("Enter difficulty for new blockchain (e.g., 2): ").strip()
                difficulty = int(difficulty_str) if difficulty_str else 2
                if difficulty < 1:
                    print("Difficulty must be at least 1.")
                else:
                    break
            except ValueError:
                print("Invalid input for difficulty.")
        my_blockchain = Blockchain(difficulty=difficulty)
        my_blockchain.create_genesis_block()
        print(f"\nNew blockchain initialized with difficulty {my_blockchain.difficulty}.")
    else:
        print(f"\nBlockchain loaded. State: {my_blockchain}")

    # Wallet Operations
    if not load_wallet(): # Try to load existing wallet
        print("No existing wallet found or failed to load.")
        if input("Do you want to generate a new wallet? (y/n): ").lower() == 'y':
            generate_new_wallet()
        else:
            print("Exiting. A wallet is required to use the CLI fully.")
            return

    while True:
        display_current_wallet_info(my_blockchain) # Show wallet status at each menu
        print("\n" + "-"*15 + " Blockchain CLI Menu " + "-"*15)
        print("1. Add a new transaction")
        print("2. Mine pending transactions")
        print("3. Display the full blockchain")
        print("4. Validate the blockchain")
        print("5. View pending transactions")
        print("6. Save blockchain to file")
        print("7. Manage Wallet (Generate/Load/View Keys)")
        print("8. Get balance for any public key")
        print("9. Exit")
        print("-"*47)

        choice = input("Enter your choice (1-9): ").strip()

        if choice == '1': # Add Transaction
            if not currentUserKeys["private_key_pem"]:
                print("Cannot add transaction: No private key loaded. Please manage your wallet.")
                continue
            try:
                print("\n--- Add New Transaction ---")
                recipient_public_key_pem = input("  Enter RECIPIENT'S Full Public Key (PEM format):\n").strip()
                # Basic check for PEM format (very naive)
                if not recipient_public_key_pem.startswith("-----BEGIN PUBLIC KEY-----") or \
                   not recipient_public_key_pem.endswith("-----END PUBLIC KEY-----"):
                    print("  Error: Recipient public key does not look like a valid PEM format.")
                    continue

                amount_str = input(f"  Enter transaction amount to send to {recipient_public_key_pem[:20]}...: ").strip()
                amount = float(amount_str)

                # Prepare data for signing (sender is current user)
                data_to_sign_str = get_data_to_sign(
                    currentUserKeys["public_key_pem"],
                    recipient_public_key_pem,
                    amount
                )
                # Sign the transaction data
                signature_hex = sign_data(currentUserKeys["private_key_pem"], data_to_sign_str)
                
                transaction = Transaction(
                    sender_public_key=currentUserKeys["public_key_pem"],
                    recipient_public_key=recipient_public_key_pem,
                    amount=amount,
                    signature=signature_hex
                )
                
                success, message, next_block_idx = my_blockchain.add_transaction(transaction)
                if success:
                    print(f"  Transaction successfully added: {message}")
                    my_blockchain.save_to_file(blockchain_data_filename) # Persist pending
                else:
                    print(f"  Error adding transaction: {message}")

            except ValueError as ve:
                print(f"  Error: Invalid transaction input - {ve}")
            except Exception as e:
                print(f"  An unexpected error occurred: {e}")

        elif choice == '2': # Mine
            if not currentUserKeys["public_key_pem"]:
                print("Cannot mine: No public key loaded for rewards. Please manage your wallet.")
                continue
            print(f"\n--- Mine Pending Transactions ---")
            print(f"Mining rewards will go to your address: {currentUserKeys['public_key_pem'][:30]}...")
            
            mined_block, mining_duration, mine_message = my_blockchain.mine_pending_transactions(
                mining_reward_address_public_key=currentUserKeys["public_key_pem"]
            )
            if mined_block:
                print(f"  {mine_message}")
                print(f"    Hash: {mined_block.hash}")
                print(f"    Nonce: {mined_block.nonce}")
                if mining_duration is not None:
                    print(f"    Mining Time: {mining_duration:.4f} seconds")
                my_blockchain.save_to_file(blockchain_data_filename) # Persist mined block
            else:
                print(f"  Could not mine: {mine_message}")

        elif choice == '3':
            print_blockchain_details_cli(my_blockchain)

        elif choice == '4':
            print("\n--- Validate Blockchain ---")
            is_valid = my_blockchain.is_chain_valid()
            print(f"Blockchain integrity check result: {'VALID' if is_valid else 'INVALID'}")

        elif choice == '5':
            print("\n--- Current Pending Transactions ---")
            if my_blockchain.pending_transactions:
                for i, tx in enumerate(my_blockchain.pending_transactions):
                    print(f"  {i+1}. {tx}") # Uses Transaction.__repr__
            else:
                print("  No transactions currently pending.")
            print("----------------------------------")
        
        elif choice == '6':
            print("\n--- Save Blockchain ---")
            my_blockchain.save_to_file(blockchain_data_filename)

        elif choice == '7': # Manage Wallet
            print("\n--- Wallet Management ---")
            print("  a. View Current Wallet Keys")
            print("  b. Generate New Wallet (will overwrite current if not saved separately)")
            # print("  c. Load Wallet from File (Not implemented yet for multiple wallets)")
            # print("  d. Save Current Wallet (if changes made and not auto-saved)")
            wallet_choice = input("  Choose an option (or any other key to go back): ").lower()
            if wallet_choice == 'a':
                if currentUserKeys["public_key_pem"]:
                    print("\n  Your Current Public Key:")
                    print(currentUserKeys["public_key_pem"])
                    if input("  Show private key? (y/n - CAUTION, VERY SENSITIVE): ").lower() == 'y':
                        print("\n  Your Current Private Key (KEEP SECRET):")
                        print(currentUserKeys["private_key_pem"])
                else:
                    print("  No keys currently loaded.")
            elif wallet_choice == 'b':
                if input("  This will generate a new key pair. Current keys (if any and unsaved elsewhere) might be lost. Continue? (y/n): ").lower() == 'y':
                    generate_new_wallet()
            # elif wallet_choice == 'd':
            # save_wallet() # Already auto-saves on generation

        elif choice == '8': # Get balance for any public key
            print("\n--- Get Balance for Public Key ---")
            pub_key_to_check = input("Enter the Public Key (PEM format) to check balance for:\n").strip()
            if pub_key_to_check:
                try:
                    # Basic check for PEM format (very naive)
                    if not pub_key_to_check.startswith("-----BEGIN PUBLIC KEY-----") or \
                       not pub_key_to_check.endswith("-----END PUBLIC KEY-----"):
                        print("  Error: Input does not look like a valid PEM public key.")
                    else:
                        balance = my_blockchain.get_balance(pub_key_to_check)
                        print(f"  Balance for {pub_key_to_check[:30]}... is: {balance:.4f} coins")
                except Exception as e:
                    print(f"  Error getting balance: {e}")
            else:
                print("  No public key entered.")


        elif choice == '9':
            print("\n--- Exit Application ---")
            save_on_exit = input("Save current blockchain state before exiting? (y/n, default: n): ").strip().lower()
            if save_on_exit == 'y':
                my_blockchain.save_to_file(blockchain_data_filename)
            print("Exiting Simple Blockchain CLI. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main_cli()