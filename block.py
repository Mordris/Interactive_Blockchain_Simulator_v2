# block.py

import hashlib 
import json    
import time    

class Block:
    """
    Represents a single block in our blockchain.
    A block contains an index, a list of transactions (stored as dictionaries),
    a timestamp, the hash of the preceding block, a nonce (for Proof-of-Work),
    and its own calculated hash.
    """
    def __init__(self, index: int, transactions: list[dict], timestamp: float, previous_hash: str, nonce: int = 0):
        """
        Initializes a new block.

        Args:
            index (int): The position of the block in the chain.
            transactions (list[dict]): A list of transactions included in this block.
                                       Each transaction should be a dictionary (from Transaction.to_dict()).
            timestamp (float): The time the block was created (Unix timestamp).
            previous_hash (str): The hash of the preceding block in the chain.
            nonce (int, optional): The nonce value found during Proof-of-Work. Defaults to 0.
        """
        self.index: int = index
        # Ensure transactions are stored as a list of dictionaries.
        # If Transaction objects were passed, they should be converted to dicts before Block init.
        if not all(isinstance(tx, dict) for tx in transactions):
            raise TypeError("Block transactions must be a list of dictionaries.")
        self.transactions: list[dict] = transactions 
        self.timestamp: float = timestamp
        self.previous_hash: str = previous_hash
        self.nonce: int = nonce
        # The hash of the block is calculated based on its content, including the nonce.
        # It's calculated upon initialization and will be recalculated during mining if nonce changes.
        self.hash: str = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculates the SHA-256 hash of the block's content.
        The content includes index, transactions (as sorted JSON string),
        timestamp, previous_hash, and nonce.
        """
        block_content = {
            'index': self.index,
            # Transactions are already dicts. sort_keys=True in json.dumps
            # handles sorting keys *within* each transaction dictionary.
            # The order of transactions in the list self.transactions is preserved as is,
            # which is important for deterministic hashing.
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }

        # Serialize the entire block content dictionary to a JSON string.
        # `sort_keys=True` ensures dictionary keys are always in alphabetical order within the JSON structure.
        # `.encode('utf-8')` converts the string to bytes for hashlib.
        block_string = json.dumps(block_content, sort_keys=True).encode('utf-8')
        sha256_hasher = hashlib.sha256()
        sha256_hasher.update(block_string)
        return sha256_hasher.hexdigest()

    def __repr__(self) -> str:
        # Truncate hash for display if it's too long
        hash_display = self.hash[:10] + "..." if len(self.hash) > 20 else self.hash
        prev_hash_display = self.previous_hash[:10] + "..." if self.previous_hash != "0" and len(self.previous_hash) > 20 else self.previous_hash
        
        return (f"Block(index={self.index}, "
                f"tx_count={len(self.transactions)}, "
                f"prev_hash='{prev_hash_display}', "
                f"nonce={self.nonce}, "
                f"hash='{hash_display}')")

if __name__ == '__main__':
    print("--- Testing Block Class ---")
    sample_tx_dicts = [
        {'sender_public_key': 'AlicePEM', 'recipient_public_key': 'BobPEM', 'amount': 50.0, 'signature': 'sig123'},
        {'sender_public_key': 'BobPEM', 'recipient_public_key': 'CharliePEM', 'amount': 20.0, 'signature': 'sig456'}
    ]

    genesis_block = Block(
        index=0,
        transactions=[],
        timestamp=time.time(),
        previous_hash="0"
    )
    print(f"Genesis Block: {genesis_block}")
    assert genesis_block.hash == genesis_block.calculate_hash()

    block_one = Block(
        index=1,
        transactions=sample_tx_dicts,
        timestamp=time.time(),
        previous_hash=genesis_block.hash,
        nonce=101
    )
    print(f"Block One: {block_one}")
    original_hash_b1 = block_one.hash
    assert original_hash_b1 == block_one.calculate_hash()

    # Test if changing nonce changes the hash
    block_one.nonce = 102
    new_hash_b1 = block_one.calculate_hash() # Manually recalculate for test comparison
    assert original_hash_b1 != new_hash_b1, "Changing nonce should change hash."
    block_one.hash = new_hash_b1 # Update the stored hash after changing nonce (as PoW would do)
    print(f"Block One (nonce changed): {block_one}")

    # Test if changing transactions changes the hash
    block_two_data_A = Block(2, [{'tx':'A'}], time.time(), block_one.hash, 0)
    block_two_data_B = Block(2, [{'tx':'B'}], block_two_data_A.timestamp, block_one.hash, 0) # Same timestamp and index for direct tx comparison
    assert block_two_data_A.hash != block_two_data_B.hash, "Changing transactions should change hash."
    
    print("\nAll Block class self-tests passed!")