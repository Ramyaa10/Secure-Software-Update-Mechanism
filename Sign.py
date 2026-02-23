 
from Crypto.PublicKey import RSA 
from Crypto.Signature import pkcs1_15 
from Crypto.Hash import SHA256 
 
# Load the private key 
def load_private_key(): 
    with open("private_key.pem", "rb") as key_file: 
        return RSA.import_key(key_file.read()) 
 
private_key = load_private_key() 
 
# Specify the update file to sign 
file_path = "update_v1.0.1.zip"  # The original update file 
 
# Read the file and compute its hash 
with open(file_path, "rb") as f: 
    file_data = f.read() 
file_hash = SHA256.new(file_data) 
 
# Sign the hash with the private key 
signature = pkcs1_15.new(private_key).sign(file_hash) 
 
# Save the signature to a file 
with open(f"{file_path}.sig", "wb") as sig_file: 
    sig_file.write(signature) 
 
print(f"Signature for {file_path} created and saved as {file_path}.sig")