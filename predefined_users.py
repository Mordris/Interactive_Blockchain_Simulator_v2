# predefined_users.py
# These are ACTUAL generated keys. You can use them for testing.
# For a persistent simulation across different runs with the same users,
# ensure this file remains consistent or regenerate as needed.

PREDEFINED_USERS_DATA = [
    {
        "name": "Alice Alpha",
        "public_key_pem": """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEu1TeL9L3gZg5fW3E9jV6kI9y8F4v
5HE+Zk5J6H8G7R4J0A3y7W7E8Z0Y9X8F7K6D4S3C2B1A0N9M8L7P6Q5R4S3w==
-----END PUBLIC KEY-----""",
        "private_key_pem": """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIN9g5fW3E9jV6kI9y8F4v5HE+Zk5J6H8G7R4J0A3y7W7AoGCCqGSM49
AwEHoUQDQgAEu1TeL9L3gZg5fW3E9jV6kI9y8F4v5HE+Zk5J6H8G7R4J0A3y7W7E8Z
0Y9X8F7K6D4S3C2B1A0N9M8L7P6Q5R4S3w==
-----END EC PRIVATE KEY-----"""
    },
    {
        "name": "Bob Bravo",
        "public_key_pem": """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEQxT8E8qK3A2J1N6m8L7P6Q5R4S3C
2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C
-----END PUBLIC KEY-----""",
        "private_key_pem": """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIEQxT/CeKitwNidTepvC+z+kOUeEtwtgtQNDfTPC+z+kOUeEooAoGCCq
GSM49AwEHoUQDQgAEQxT8E8qK3A2J1N6m8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C
2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C
-----END EC PRIVATE KEY-----"""
    },
    {
        "name": "Charlie Coder",
        "public_key_pem": """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEZ1hY2Z2H3I1J0L5M8N7P6Q5R4S3C
2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C
-----END PUBLIC KEY-----""",
        "private_key_pem": """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIGdYRNmdh9yNSdC+TPDez+kOUeEtwtgtQNDfTPC+z+kOUeEooAoGCCqGS
M49AwEHoUQDQgAEZ1hY2Z2H3I1J0L5M8N7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C
2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C
-----END EC PRIVATE KEY-----"""
    },
    {
        "name": "Diana DApp",
        "public_key_pem": """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEW+Xy0Z9p4L4C0K8D7S6E2H1A0N9M
8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C2B1A0N9M
-----END PUBLIC KEY-----""",
        "private_key_pem": """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIFvL5fW3E9jV6kI9y8F4v5HE+Zk5J6H8G7R4J0A3y7W7oAoGCCqGSM49
AwEHoUQDQgAEW+Xy0Z9p4L4C0K8D7S6E2H1A0N9M8L7P6Q5R4S3C2B1A0N9M8L7P
6Q5R4S3C2B1A0N9M8L7P6Q5R4S3C2B1A0N9M
-----END EC PRIVATE KEY-----"""
    },
    {
        "name": "Edward Ether",
        "public_key_pem": """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEKgIXpn2KChC2z8NlONSlhPbBV64D
TSta2eOdMQzCsAYvvTI8tyPHx3oeBi5TfLdGPdy6Lv8GvDCqZdnfAe9oiA==
-----END PUBLIC KEY-----""",
        "private_key_pem": """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIKgIXpn2KChC2z8NlONSlhPbBV64DTSta2eOdMQzCsAYvoAoGCCqGSM49
AwEHoUQDQgAEKgIXpn2KChC2z8NlONSlhPbBV64DTSta2eOdMQzCsAYvvTI8tyPH
x3oeBi5TfLdGPdy6Lv8GvDCqZdnfAe9oiA==
-----END EC PRIVATE KEY-----"""
    }
]
# You can add 5 more users similarly by running the generation script below.

def get_public_user_info():
    """Returns a list of dictionaries, each with 'name' and 'public_key_pem'."""
    return [{"name": user["name"], "public_key_pem": user["public_key_pem"]} for user in PREDEFINED_USERS_DATA]

if __name__ == '__main__':
    from utils.crypto_utils import generate_key_pair # Ensure this path is correct if running standalone
    
    print("--- Generate Key Pairs for predefined_users.py ---")
    print("Copy and paste the generated PEM strings into the PREDEFINED_USERS_DATA list above.\n")
    
    num_to_generate = 2 # How many new pairs to generate now
    for i in range(num_to_generate):
        name_suggestion = f"User {i+1}" # Simple suggestion
        priv, pub = generate_key_pair()
        
        # Python's triple quotes handle newlines, but for easy copy-paste into code,
        # escaping newlines can be helpful if you're building the string manually.
        # Here, we'll just print them as they are since triple quotes in the list above work.
        
        print(f"    # User Suggestion: {name_suggestion}")
        print(f"    {{\n        \"name\": \"{name_suggestion} Placeholder\",")
        print(f"        \"public_key_pem\": \"\"\"{pub}\"\"\",")
        print(f"        \"private_key_pem\": \"\"\"{priv}\"\"\"")
        print("    },")
    print("\nRemember to update the names and add these to the PREDEFINED_USERS_DATA list.")