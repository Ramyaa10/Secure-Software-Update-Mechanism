from Crypto.PublicKey import RSA 
 
# Generate a 2048-bit RSA key pair for the server (for signing) 
server_key = RSA.generate(2048) 
with open("private_key.pem", "wb") as f: 
    f.write(server_key.export_key("PEM")) 
with open("public_key.pem", "wb") as f: 
    f.write(server_key.publickey().export_key("PEM")) 
 
# Generate a 2048-bit RSA key pair for the client (for encryption) 
client_key = RSA.generate(2048) 
with open("client_private_key.pem", "wb") as f: 
    f.write(client_key.export_key("PEM")) 
with open("client_public_key.pem", "wb") as f: 
    f.write(client_key.publickey().export_key("PEM"))