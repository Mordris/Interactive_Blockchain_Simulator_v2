# blockchain.py

import time
import json
import traceback # For more detailed error logging if needed
from block import Block
from transaction import Transaction
from utils.crypto_utils import get_data_to_sign, verify_signature

class Blockchain:
    """
    Manages a chain of blocks, handles pending transactions with signature verification
    and balance checks, implements Proof-of-Work, and provides save/load functionality.
    """
    def __init__(self, difficulty: int = 2, mining_reward: float = 100.0):
        self.chain: list[Block] = []
        self.pending_transactions: list[Transaction] = [] # Stores Transaction objects
        self.difficulty: int = int(difficulty)
        self.mining_reward: float = float(mining_reward)
        # Genesis block handled by create_genesis_block or load_from_file

    def create_genesis_block(self):
        """Creates the first block in the chain (the "genesis block")."""
        print("Creating Genesis Block...")
        genesis_block = Block(
            index=0,
            transactions=[], # Genesis block has no user transactions
            timestamp=time.time(),
            previous_hash="0", # Conventional placeholder
            nonce=0 # Genesis block typically doesn't require PoW
        )
        self.chain.append(genesis_block)
        print(f"Genesis Block created: {genesis_block}")

    def get_latest_block(self) -> Block | None:
        """Returns the most recently added block in the chain."""
        return self.chain[-1] if self.chain else None

    def get_balance(self, address_public_key: str) -> float:
        """
        Calculates the balance of a given address by iterating through all
        transactions in the blockchain and currently pending transactions.
        """
        balance = 0.0
        # Calculate balance from confirmed transactions in the chain
        for block_obj in self.chain:
            for tx_dict in block_obj.transactions:
                try:
                    tx = Transaction.from_dict(tx_dict)
                    if tx.recipient_public_key == address_public_key:
                        balance += tx.amount
                    if tx.sender_public_key == address_public_key:
                        balance -= tx.amount
                except ValueError as e:
                    print(f"Warning: Skipping malformed transaction in block {block_obj.index} during balance calculation: {e}")
        
        # Adjust balance based on pending transactions (for spendable balance estimate)
        for tx in self.pending_transactions:
            if tx.recipient_public_key == address_public_key:
                balance += tx.amount
            if tx.sender_public_key == address_public_key:
                balance -= tx.amount
                
        return balance

    def add_transaction(self, transaction: Transaction) -> tuple[bool, str, int | None]:
        """
        Adds a new transaction to the pending pool after validation.
        Validations: Signature verification and sender balance.
        """
        # 1. Validate signature (unless it's a system transaction)
        if transaction.sender_public_key not in ["network", "welcome_faucet"]:
            if not transaction.signature:
                return False, "Transaction is missing a signature.", None
            
            is_signature_valid = verify_signature(
                public_key_pem=transaction.sender_public_key,
                data=transaction.get_data_for_signing(),
                signature_hex=transaction.signature
            )
            if not is_signature_valid:
                return False, "Invalid transaction signature.", None
        
        # 2. Validate sender's balance (unless it's a system transaction)
        if transaction.sender_public_key not in ["network", "welcome_faucet"]:
            # Get balance *excluding* this potential new pending transaction for the check
            # This is tricky. For simplicity, current get_balance includes all pending.
            # A more robust check might calculate balance *before* this tx.
            # For now, the current get_balance should work if it subtracts pending.
            sender_balance = self.get_balance(transaction.sender_public_key)
            # If we subtract this pending tx from balance calculation:
            # effective_spendable_balance = sender_balance - transaction.amount (if it were already pending)
            # But it's not pending yet. So sender_balance as calculated is correct *before* this tx.
            
            if sender_balance < transaction.amount:
                return False, f"Insufficient balance for sender. Has {sender_balance:.4f}, needs {transaction.amount:.4f}.", None

        self.pending_transactions.append(transaction)
        
        latest_block = self.get_latest_block()
        next_block_idx = latest_block.index + 1 if latest_block else 0 # Should always have genesis
        
        if transaction.sender_public_key in ["network", "welcome_faucet"]:
            msg = f"System transaction ({transaction.sender_public_key}) for {transaction.amount:.2f} to {transaction.recipient_public_key[:15]}... staged."
        else:
            msg = f"Transaction from {transaction.sender_public_key[:15]}... for {transaction.amount:.2f} to {transaction.recipient_public_key[:15]}... added to pending pool."
        
        return True, msg, next_block_idx

    def proof_of_work(self, block: Block) -> tuple[str, float]:
        """Implements Proof-of-Work to find a valid nonce for the block."""
        print(f"Mining block #{block.index} with difficulty {self.difficulty} (target prefix: '{'0'*self.difficulty}')...")
        block.nonce = 0 # Reset nonce before starting
        start_time = time.time()
        computed_hash = block.calculate_hash() # Initial hash
        target_prefix = '0' * self.difficulty

        while not computed_hash.startswith(target_prefix):
            block.nonce += 1
            computed_hash = block.calculate_hash() # Recalculate with new nonce

        end_time = time.time()
        mining_duration = end_time - start_time
        block.hash = computed_hash # CRITICAL: Update block's actual hash attribute
        print(f"Block successfully mined! Nonce: {block.nonce}, Hash: {block.hash[:15]}..., Time: {mining_duration:.4f} seconds")
        return computed_hash, mining_duration

    def mine_pending_transactions(self, miner_reward_address_public_key: str) -> tuple[Block | None, float | None, str]:
        """
        Mines a new block with all current pending transactions.
        The specified miner_reward_address_public_key receives the mining reward.
        """
        # Check if there are any actual user-submittable transactions or specific system transactions
        # that warrant mining a block.
        has_mineable_transactions = False
        if self.pending_transactions:
            # We consider it mineable if there's any transaction.
            # System transactions like "welcome_faucet" or "GENESIS_ALLOCATION" are also mineable.
            has_mineable_transactions = True
        
        if not has_mineable_transactions:
            # If difficulty is 0, one might allow mining empty blocks for PoW testing,
            # but for a typical simulation with PoW, we don't mine truly empty blocks.
            if self.difficulty > 0:
                return None, None, "No transactions (user or system) currently pending to be mined."
            # If difficulty is 0, we might allow it, but still issue a warning.
            # For this simulation, let's stick to requiring some transaction.
            # else:
            #     print("Warning: Mining an empty block as difficulty is 0.")

        print(f"\nAttempting to mine new block for {len(self.pending_transactions)} pending transactions. Miner: {miner_reward_address_public_key[:15]}...")

        reward_tx = Transaction(
            sender_public_key="network",
            recipient_public_key=miner_reward_address_public_key,
            amount=self.mining_reward,
            signature=None 
        )
        
        # If pending_transactions was empty but we decided to proceed (e.g. for difficulty 0),
        # then transactions_to_include_in_block will only have the reward_tx.
        transactions_to_include_in_block = [reward_tx] + self.pending_transactions

        latest_block = self.get_latest_block()
        if not latest_block:
            return None, None, "CRITICAL ERROR: Cannot mine without a genesis block."

        new_block = Block(
            index=latest_block.index + 1,
            transactions=[tx.to_dict() for tx in transactions_to_include_in_block],
            timestamp=time.time(),
            previous_hash=latest_block.hash
        )

        _actual_hash, mining_duration = self.proof_of_work(new_block)

        self.chain.append(new_block)
        print(f"Block #{new_block.index} added to chain. Contains {len(new_block.transactions)} transactions (incl. reward).")
        
        self.pending_transactions = [] # Clear after successful mining

        return new_block, mining_duration, f"Block #{new_block.index} successfully mined by {miner_reward_address_public_key[:15]}..."

    def is_chain_valid(self) -> bool:
        """Validates the integrity of the entire blockchain."""
        print("\nValidating blockchain integrity...")
        if not self.chain:
            print("Blockchain is empty. Considered valid by default.")
            return True

        # Validate Genesis Block
        genesis_block = self.chain[0]
        if not (genesis_block.index == 0 and genesis_block.previous_hash == "0"):
            print(f"Genesis block (Index {genesis_block.index}) is malformed.")
            return False
        # Re-calculate genesis block hash to check for tampering (it has no PoW in this sim).
        temp_genesis = Block(genesis_block.index, genesis_block.transactions, genesis_block.timestamp, 
                             genesis_block.previous_hash, genesis_block.nonce)
        if genesis_block.hash != temp_genesis.calculate_hash():
            print(f"Genesis Block data integrity compromised!")
            return False

        # Validate the rest of the chain
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check current block's hash integrity
            temp_current = Block(current_block.index, current_block.transactions, current_block.timestamp,
                                 current_block.previous_hash, current_block.nonce)
            if current_block.hash != temp_current.calculate_hash():
                print(f"Data integrity compromised at Block #{current_block.index}.")
                return False

            # Check the chain link integrity
            if current_block.previous_hash != previous_block.hash:
                print(f"Chain broken: Previous hash mismatch at Block #{current_block.index}.")
                return False

            # Check Proof-of-Work
            if self.difficulty > 0: 
                target_prefix = '0' * self.difficulty
                if not current_block.hash.startswith(target_prefix):
                    print(f"Proof of Work invalid for Block #{current_block.index}.")
                    return False
            
            # Check transaction validity within the block (signatures)
            for tx_dict in current_block.transactions:
                try:
                    tx = Transaction.from_dict(tx_dict)
                    # MODIFIED: Define a list of system senders that don't require signatures
                    system_senders = ["network", "welcome_faucet", "GENESIS_ALLOCATION"]
                    if tx.sender_public_key not in system_senders: 
                        if not tx.signature:
                            print(f"User transaction in Block #{current_block.index} is missing signature: {tx}")
                            return False
                        if not verify_signature(tx.sender_public_key, tx.get_data_for_signing(), tx.signature):
                            print(f"Invalid signature for user transaction in Block #{current_block.index}: {tx}")
                            return False
                    elif tx.signature is not None: # System transactions should NOT have signatures
                        print(f"System transaction in Block #{current_block.index} unexpectedly has a signature: {tx}")
                        return False
                except ValueError as e: 
                    print(f"Malformed transaction in Block #{current_block.index} during validation: {e}")
                    return False
        
        print("Blockchain is valid.")
        return True

    def to_json_serializable(self) -> dict:
        """Converts blockchain state to a JSON-serializable dictionary."""
        return {
            "chain": [block_obj.__dict__ for block_obj in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward
        }

    @classmethod
    def from_json_serializable(cls, data: dict) -> 'Blockchain':
        """Creates a Blockchain instance from a JSON-serializable dictionary."""
        blockchain_instance = cls(
            difficulty=data.get('difficulty', 2),
            mining_reward=data.get('mining_reward', 100.0)
        )
        
        for tx_data in data.get('pending_transactions', []):
            try:
                blockchain_instance.pending_transactions.append(Transaction.from_dict(tx_data))
            except ValueError as e:
                print(f"Warning: Skipping malformed pending transaction during load: {e}")

        blockchain_instance.chain = []
        for block_data in data.get('chain', []):
            try:
                # Transactions in block_data are already dicts from to_dict()
                block = Block(
                    index=block_data['index'],
                    transactions=block_data['transactions'], 
                    timestamp=block_data['timestamp'],
                    previous_hash=block_data['previous_hash'],
                    nonce=block_data['nonce']
                )
                # Crucially, use the hash stored in the file, not recalculate (unless missing)
                block.hash = block_data.get('hash', block.calculate_hash()) 
                blockchain_instance.chain.append(block)
            except (KeyError, TypeError, ValueError) as e:
                 print(f"Warning: Skipping malformed block (index {block_data.get('index', 'Unknown')}) during load: {e}")

        if not blockchain_instance.chain: # If chain is empty after loading (e.g. corrupt file)
            print("Warning: Loaded chain was empty or invalid. A new genesis block will be created.")
            blockchain_instance.create_genesis_block()
            
        return blockchain_instance

    def save_to_file(self, filename: str = "blockchain_data.json"):
        """Saves the current blockchain state to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.to_json_serializable(), f, indent=4)
            print(f"Blockchain state successfully saved to {filename}")
        except IOError as e:
            print(f"Error: Could not save blockchain to file '{filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving blockchain: {e}")
            traceback.print_exc()

    @classmethod
    def load_from_file(cls, filename: str = "blockchain_data.json") -> 'Blockchain | None':
        """Loads blockchain state from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"Blockchain data successfully loaded from {filename}")
            return cls.from_json_serializable(data)
        except FileNotFoundError:
            print(f"Info: No saved blockchain found at '{filename}'.")
            return None
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading or decoding JSON from '{filename}': {e}. A new blockchain may be initialized.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during loading from '{filename}': {e}. A new blockchain may be initialized.")
            traceback.print_exc()
            return None

    def __repr__(self) -> str:
        """Provides a concise string representation of the Blockchain."""
        return (f"Blockchain(blocks={len(self.chain)}, "
                f"pending_tx={len(self.pending_transactions)}, "
                f"difficulty={self.difficulty})")

if __name__ == '__main__':
    # Basic self-test functionality
    print("\n--- Blockchain Class Self-Test ---")
    from utils.crypto_utils import generate_key_pair, sign_data
    
    # Create users for testing
    miner_priv, miner_pub = generate_key_pair()
    alice_priv, alice_pub = generate_key_pair()
    bob_priv, bob_pub = generate_key_pair()

    # Test 1: Initialize and Genesis
    bc = Blockchain(difficulty=1)
    bc.create_genesis_block()
    assert len(bc.chain) == 1, "Test 1.1 Failed: Genesis block not created."
    assert bc.is_chain_valid(), "Test 1.2 Failed: Initial chain invalid."
    print("Test 1 Passed: Initialization and Genesis.")

    # Test 2: Mining reward and balance
    block1, duration1, msg1 = bc.mine_pending_transactions(miner_pub)
    assert block1 is not None, f"Test 2.1 Failed: Mining failed - {msg1}"
    assert len(bc.chain) == 2, "Test 2.2 Failed: Block not added after mining."
    assert bc.get_balance(miner_pub) == bc.mining_reward, "Test 2.3 Failed: Miner reward incorrect."
    assert bc.is_chain_valid(), "Test 2.4 Failed: Chain invalid after first mine."
    print("Test 2 Passed: Mining Reward and Balance.")

    # Test 3: Add valid transaction
    amount_alice_to_bob = 10.0
    # Alice needs funds first - let's give them via the miner (who has funds)
    if bc.get_balance(miner_pub) >= amount_alice_to_bob:
        tx_miner_to_alice_data = get_data_to_sign(miner_pub, alice_pub, amount_alice_to_bob * 2) # Give Alice enough
        tx_miner_to_alice_sig = sign_data(miner_priv, tx_miner_to_alice_data)
        tx_miner_to_alice = Transaction(miner_pub, alice_pub, amount_alice_to_bob * 2, tx_miner_to_alice_sig)
        ok, msg, _ = bc.add_transaction(tx_miner_to_alice)
        assert ok, f"Test 3.0 Failed: Could not add priming transaction - {msg}"
        bc.mine_pending_transactions(miner_pub) # Mine this priming transaction
    
    assert bc.get_balance(alice_pub) >= amount_alice_to_bob, f"Test 3.0.1 Failed: Alice does not have enough funds after priming. Has: {bc.get_balance(alice_pub)}"

    tx_data_alice_to_bob = get_data_to_sign(alice_pub, bob_pub, amount_alice_to_bob)
    tx_sig_alice_to_bob = sign_data(alice_priv, tx_data_alice_to_bob)
    valid_tx = Transaction(alice_pub, bob_pub, amount_alice_to_bob, tx_sig_alice_to_bob)
    
    ok, msg, _ = bc.add_transaction(valid_tx)
    assert ok, f"Test 3.1 Failed: Valid transaction rejected - {msg}"
    assert len(bc.pending_transactions) == 1, "Test 3.2 Failed: Transaction not in pending."
    print("Test 3 Passed: Add Valid Transaction.")

    # Test 4: Mine transaction
    block2, duration2, msg2 = bc.mine_pending_transactions(miner_pub)
    assert block2 is not None, f"Test 4.1 Failed: Mining transaction failed - {msg2}"
    assert len(bc.pending_transactions) == 0, "Test 4.2 Failed: Pending transactions not cleared."
    assert bc.get_balance(bob_pub) == amount_alice_to_bob, "Test 4.3 Failed: Bob's balance incorrect."
    # Alice's balance would be (initial_prime - sent_amount)
    # Miner's balance would be (initial_reward + reward_for_prime_block - sent_prime_amount + reward_for_tx_block)
    assert bc.is_chain_valid(), "Test 4.4 Failed: Chain invalid after mining transaction."
    print("Test 4 Passed: Mine Transaction and Balance Update.")

    # Test 5: Add transaction with insufficient funds
    tx_insufficient_data = get_data_to_sign(bob_pub, alice_pub, bc.get_balance(bob_pub) + 1.0) # Bob tries to send more than he has
    tx_insufficient_sig = sign_data(bob_priv, tx_insufficient_data)
    insufficient_tx = Transaction(bob_pub, alice_pub, bc.get_balance(bob_pub) + 1.0, tx_insufficient_sig)
    ok, msg, _ = bc.add_transaction(insufficient_tx)
    assert not ok, "Test 5.1 Failed: Insufficient funds transaction accepted."
    print(f"Test 5 Passed: Insufficient Funds Transaction Rejected (Message: {msg}).")

    # Test 6: Save and Load
    bc.save_to_file("test_blockchain_temp.json")
    loaded_bc = Blockchain.load_from_file("test_blockchain_temp.json")
    assert loaded_bc is not None, "Test 6.1 Failed: Blockchain did not load."
    assert len(bc.chain) == len(loaded_bc.chain), "Test 6.2 Failed: Loaded chain length mismatch."
    if bc.chain and loaded_bc.chain : # Check if chains are not empty
        assert bc.chain[-1].hash == loaded_bc.chain[-1].hash, "Test 6.3 Failed: Last block hash mismatch after load."
    assert loaded_bc.is_chain_valid(), "Test 6.4 Failed: Loaded blockchain is not valid."
    print("Test 6 Passed: Save and Load.")

    # Clean up test file
    import os
    if os.path.exists("test_blockchain_temp.json"):
        os.remove("test_blockchain_temp.json")

    print("\nAll Blockchain class self-tests passed!")