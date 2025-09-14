from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from cryptography.fernet import Fernet
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
KEY_FILE = "secret.key"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Generate or load key
if not os.path.exists(KEY_FILE):
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(Fernet.generate_key())

with open(KEY_FILE, "rb") as key_file:
    key = key_file.read()

fernet = Fernet(key)

@app.route("/")
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template("index.html", files=files)

@app.route("/encrypt", methods=["POST"])
def encrypt_file():
    if "file" not in request.files:
        return "No file uploaded"
    file = request.files["file"]
    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, "rb") as f:
        data = f.read()

    encrypted_data = fernet.encrypt(data)
    encrypted_path = filepath + ".enc"

    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    os.remove(filepath)  # remove original

    print(f"[LOG] File {file.filename} encrypted successfully.")
    return redirect(url_for("index"))

@app.route("/decrypt", methods=["POST"])
def decrypt_file():
    if "file" not in request.files:
        return "No file uploaded"
    file = request.files["file"]
    if file.filename == "":
        return "No file selected"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = fernet.decrypt(encrypted_data)
    decrypted_path = filepath.replace(".enc", "")

    with open(decrypted_path, "wb") as f:
        f.write(decrypted_data)

    print(f"[LOG] File {file.filename} decrypted successfully.")
    return redirect(url_for("index"))

@app.route("/download/<filename>")
def download_file(filename):
    print(f"[LOG] File {filename} downloaded.")
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
