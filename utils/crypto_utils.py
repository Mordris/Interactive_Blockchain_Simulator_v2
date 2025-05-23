# utils/crypto_utils.py

from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import DSS
from Cryptodome.Hash import SHA256
import binascii # For converting bytes to hex and vice-versa

# Use a common elliptic curve (e.g., NIST P-256)
CURVE = 'P-256'

def generate_key_pair() -> tuple[str, str]:
    """
    Generates an ECDSA key pair (private and public).

    Returns:
        tuple[str, str]: A tuple containing the private key (PEM format)
                         and public key (PEM format).
    """
    private_key = ECC.generate(curve=CURVE)
    public_key = private_key.public_key()

    private_key_pem = private_key.export_key(format='PEM')
    public_key_pem = public_key.export_key(format='PEM')

    return private_key_pem, public_key_pem

def sign_data(private_key_pem: str, data: str) -> str:
    """
    Signs data using the provided private key.
    """
    try:
        private_key = ECC.import_key(private_key_pem)
        data_hash = SHA256.new(data.encode('utf-8'))
        signer = DSS.new(private_key, 'fips-186-3') # Deterministic signatures
        signature = signer.sign(data_hash)
        return binascii.hexlify(signature).decode('ascii')
    except Exception as e:
        print(f"Error during signing: {e}")
        raise ValueError("Failed to sign data. Invalid private key or data.")


def verify_signature(public_key_pem: str, data: str, signature_hex: str) -> bool:
    """
    Verifies a signature against the given data and public key.
    """
    try:
        public_key = ECC.import_key(public_key_pem)
        data_hash = SHA256.new(data.encode('utf-8'))
        signature_bytes = binascii.unhexlify(signature_hex)
        verifier = DSS.new(public_key, 'fips-186-3')
        verifier.verify(data_hash, signature_bytes)
        return True
    except (ValueError, TypeError): # Catches errors from unhexlify or DSS.verify
        return False
    except Exception as e:
        print(f"Unexpected error during verification: {e}")
        return False

def get_data_to_sign(sender_public_key: str, recipient_public_key: str, amount: float) -> str:
    """
    Creates a consistent string representation of transaction data for signing.
    """
    return f"{sender_public_key}{recipient_public_key}{amount:.8f}" # Fixed precision for float


if __name__ == '__main__':
    # Test the functions
    priv_key, pub_key = generate_key_pair()
    print("--- Sample Key Pair ---")
    print("Private Key (PEM):\n", priv_key)
    print("\nPublic Key (PEM):\n", pub_key)

    message_data = get_data_to_sign(pub_key, "recipient_pub_key_test", 123.456)
    print(f"\nData to sign: {message_data}")

    try:
        signature = sign_data(priv_key, message_data)
        print("\nSignature (hex):\n", signature)

        is_valid = verify_signature(pub_key, message_data, signature)
        print("\nIs signature valid (with correct key)?", is_valid)
        assert is_valid

        _priv_key2, pub_key2 = generate_key_pair()
        is_valid_wrong_key = verify_signature(pub_key2, message_data, signature)
        print("Is signature valid (with wrong public key)?", is_valid_wrong_key)
        assert not is_valid_wrong_key

        tampered_data = get_data_to_sign(pub_key, "recipient_pub_key_test", 123.457)
        is_valid_tampered_data = verify_signature(pub_key, tampered_data, signature)
        print("Is signature valid (with tampered data)?", is_valid_tampered_data)
        assert not is_valid_tampered_data
        
        print("\nCrypto utils self-tests passed!")
    except Exception as e:
        print(f"\nError during self-test: {e}")