from cryptography.fernet import Fernet

def generate_key():
    """
    Generates a key and saves it into a file named 'key.key'.
    """
    key = Fernet.generate_key()
    with open('key.key', 'wb') as key_file:
        key_file.write(key)
    print("Encryption key generated and saved as 'key.key'.")

if __name__ == "__main__":
    generate_key()
