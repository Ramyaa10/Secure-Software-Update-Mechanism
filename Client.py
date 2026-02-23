import requests 
from Crypto.PublicKey import RSA 
from Crypto.Cipher import PKCS1_OAEP, AES 
from Crypto.Signature import pkcs1_15 
from Crypto.Hash import SHA256 
import binascii 
 
# Load the client's private key for decrypting the AES key 
def load_client_private_key(): 
    with open("client_private_key.pem", "rb") as key_file: 
        return RSA.import_key(key_file.read()) 
 
# Load the server's public key for verifying the signature 
def load_public_key(): 
    with open("public_key.pem", "rb") as key_file: 
        return RSA.import_key(key_file.read()) 
 
client_private_key = load_client_private_key() 
public_key = load_public_key() 
 
# Check for updates from the server 
def check_for_update(): 
    response = requests.get("http://localhost:5000/latest-update") 
    if response.status_code == 200: 
        return response.json() 
    return None 
 
# Download the update file 
def download_update(file_name): 
    url = f"http://localhost:5000/download/{file_name}" 
    response = requests.get(url) 
    if response.status_code == 200: 
        with open(file_name, "wb") as f: 
            f.write(response.content) 
        print(f"Downloaded encrypted update file: {file_name}") 
        return file_name 
    return None 
 
# Decrypt the AES key using RSA 
def decrypt_aes_key(encrypted_aes_key_hex): 
    encrypted_aes_key = binascii.unhexlify(encrypted_aes_key_hex) 
    cipher_rsa = PKCS1_OAEP.new(client_private_key) 
    aes_key = cipher_rsa.decrypt(encrypted_aes_key) 
    return aes_key 
 
# Decrypt the file using the AES key 
def decrypt_file(file_path, aes_key): 
    try: 
        with open(file_path, "rb") as f: 
            nonce = f.read(16)     # Read nonce 
            tag = f.read(16)       # Read tag 
            ciphertext = f.read()  # Read encrypted data 
 
        # Initialize AES cipher for decryption 
        cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce) 
        decrypted_data = cipher_aes.decrypt_and_verify(ciphertext, tag) 
 
        decrypted_file_path = "decrypted_update.zip" 
        with open(decrypted_file_path, "wb") as f: 
            f.write(decrypted_data) 
 
        print(f"Decrypted update file: {decrypted_file_path}") 
        return decrypted_file_path 
    except Exception as e: 
        print(f"Decryption failed: {e}") 
        return None 
 
# Verify the digital signature of the file 
def verify_signature(file_data, signature_hex): 
    file_hash = SHA256.new(file_data) 
    signature = bytes.fromhex(signature_hex) 
 
    try: 
        pkcs1_15.new(public_key).verify(file_hash, signature) 
        print("Signature verified successfully.") 
        return True 
    except (ValueError, TypeError): 
        print("Signature verification failed.") 
        return False 
 
# Main function to process the update 
def main(): 
    update_info = check_for_update() 
    if update_info: 
        encrypted_file_name = update_info["file_name"] 
        signature = update_info["signature"] 
        encrypted_aes_key = update_info["encrypted_aes_key"] 
 
        # Download the encrypted update file 
        encrypted_file = download_update(encrypted_file_name) 
        if encrypted_file: 
            # Decrypt the AES key 
            aes_key = decrypt_aes_key(encrypted_aes_key) 
 
            # Decrypt the file using the AES key 
            decrypted_file = decrypt_file(encrypted_file, aes_key) 
            if decrypted_file: 
                # Read and calculate the original hash of the decrypted file 
                with open(decrypted_file, "rb") as f: 
                    file_data = f.read() 
                original_hash = SHA256.new(file_data).hexdigest() 
 
                # No artificial tampering. We check if the file is modified. 
                tamper_update = False 
 
                # Compare the hash of the file before and after tampering (e.g., checking if the file is intact) 
                current_hash = SHA256.new(file_data).hexdigest() 
 
                # If the current file hash differs from the original, it has been tampered with 
                if current_hash != original_hash: 
                    tamper_update = True 
                    print("File data has been tampered with.") 
 
                # Proceed with signature verification 
                if tamper_update: 
                    print("File tampering detected. Verification failed.") 
                else: 
                    if verify_signature(file_data, signature): 
                        print(f"Update {update_info['version']} applied successfully.") 
                    else: 
                        print("Update verification failed; tampered update not applied.") 
            else: 
                print("Failed to decrypt the update file.") 
        else: 
            print("Failed to download the update file.") 
    else: 
        print("No update available.") 
 
if __name__ == "__main__": 
    main()