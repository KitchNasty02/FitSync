from cryptography.fernet import Fernet


# load local key
def load_key(key_path="config/key.key"):
    with open(key_path, "rb") as file:
        return file.read()
    

# generate a new key
def generate_key(key_path="config/key.key"):
    key = Fernet.generate_key()
    with open(key_path, "wb") as file:
        file.write(key)
    print("New key generated")


def encrypt_password(password, key):
    fernet = Fernet(key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()


def decrypt_password(encrypted_password, key):
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()


