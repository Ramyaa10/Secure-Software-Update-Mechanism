
from flask import Flask, jsonify, send_file 
from Crypto.PublicKey import RSA 
from Crypto.Signature import pkcs1_15 
from Crypto.Cipher import PKCS1_OAEP, AES 
from Crypto.Hash import SHA256 
from Crypto.Random import get_random_bytes 
import os 
 
app = Flask(__name__) 
 
# Load the server's private key for signing 
def load_private_key(): 
    with open("private_key.pem", "rb") as key_file: 
        return RSA.import_key(key_file.read()) 
 
# Load the client's public key for encrypting the AES key 
def load_client_public_key(): 
    with open("client_public_key.pem", "rb") as key_file: 
        return RSA.import_key(key_file.read()) 
 
private_key = load_private_key() 
client_public_key = load_client_public_key() 
 
# Endpoint for providing the latest update 
@app.route("/latest-update", methods=["GET"]) 
def latest_update(): 
    version = "1.0.1" 
    file_path = "update_v1.0.1.zip"  # The file to be sent to the client 
 
    # Read the update file 
    with open(file_path, "rb") as f: 
        file_data = f.read() 
 
    # Generate a random AES key and encrypt the file with AES 
    aes_key = get_random_bytes(16)  # 128-bit AES key 
    cipher_aes = AES.new(aes_key, AES.MODE_EAX) 
    ciphertext, tag = cipher_aes.encrypt_and_digest(file_data) 
 
    # Encrypt the AES key with the client's public RSA key 
    cipher_rsa = PKCS1_OAEP.new(client_public_key) 
    encrypted_aes_key = cipher_rsa.encrypt(aes_key) 
 
    # Sign the original file data 
    file_hash = SHA256.new(file_data) 
    signature = pkcs1_15.new(private_key).sign(file_hash) 
 
    # Save the encrypted file data 
    encrypted_file_path = "encrypted_update.bin" 
    with open(encrypted_file_path, "wb") as f: 
        f.write(cipher_aes.nonce)  # Write AES nonce 
        f.write(tag)               # Write AES tag 
        f.write(ciphertext)        # Write encrypted file data 
 
    # Respond with metadata and encrypted AES key 
    return jsonify({ 
        "version": version, 
        "signature": signature.hex(), 
        "file_name": encrypted_file_path, 
        "encrypted_aes_key": encrypted_aes_key.hex() 
    }) 
 
# Endpoint to download the encrypted update file 
@app.route("/download/<file_name>", methods=["GET"]) 
def download_update(file_name): 
    file_path = os.path.join(os.getcwd(), file_name) 
    if os.path.exists(file_path): 
        return send_file(file_path, as_attachment=True) 
    else: 
        return "File not found", 404 
 
if __name__ == "__main__": 
    app.run(port=5000) 