import sqlite3
from cryptography.fernet import Fernet, InvalidToken
import secrets
import string
import os
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama
init(autoreset=True)

DB_FILE = "password_manager.db"
KEY_FILE = "encryption.key"

# Load or generate encryption key
def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
    with open(KEY_FILE, "rb") as key_file:
        key = key_file.read()
    try:
        Fernet(key)  # Check if key is valid
        return key
    except ValueError:
        print(Fore.RED + "❌ Invalid encryption key! Regenerating...")
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        return key

# Encrypt and decrypt functions
def encrypt(text, cipher):
    try:
        return cipher.encrypt(text.encode()).decode()
    except Exception as e:
        print(Fore.RED + f"Encryption error: {e}")
        return None

def decrypt(text, cipher):
    try:
        return cipher.decrypt(text.encode()).decode()
    except InvalidToken:
        return "❌ Decryption failed (Invalid token)"
    except Exception as e:
        return f"❌ Decryption error: {e}"

# Generate random password
def generate_password(length=10):
    if length < 4:
        return "❌ Password length too short!"
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

# Initialize database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS passwords (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            service TEXT,
                            username TEXT,
                            password TEXT)''')

# Add a password
def add_password(service, username, password, cipher):
    encrypted_password = encrypt(password, cipher)
    if encrypted_password:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)',
                         (service, username, encrypted_password))

# Retrieve password
def retrieve_password(service, cipher):
    with sqlite3.connect(DB_FILE) as conn:
        rows = conn.execute('SELECT username, password FROM passwords WHERE service = ?', (service,)).fetchall()
    return [(row[0], decrypt(row[1], cipher)) for row in rows] if rows else []

# Clear terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Main Program
def main():
    cipher = Fernet(load_key())
    init_db()
    clear_screen()

    banner = pyfiglet.figlet_format("Password Manager")
    print(Fore.CYAN + banner)
    print(Fore.YELLOW + "🔐 Welcome to your secure password vault!")

    while True:
        print(Fore.GREEN + "\n📋 Menu:")
        print(Fore.CYAN + "1️⃣ Add Password")
        print(Fore.CYAN + "2️⃣ Retrieve Password")
        print(Fore.CYAN + "3️⃣ Generate Strong Password")
        print(Fore.CYAN + "4️⃣ Exit")

        choice = input(Fore.YELLOW + "\n👉 Select an option (1-4): ").strip()

        if choice == "1":
            clear_screen()
            print(Fore.MAGENTA + "🔑 Add New Password")
            service = input("📝 Service Name: ").strip()
            username = input("👤 Username: ").strip()
            password = input("🔐 Password: ").strip()
            if service and username and password:
                add_password(service, username, password, cipher)
                print(Fore.GREEN + "✅ Password added successfully!")
            else:
                print(Fore.RED + "❌ All fields are required!")

        elif choice == "2":
            clear_screen()
            print(Fore.MAGENTA + "🔍 Retrieve Password")
            service = input("📝 Enter the service name: ").strip()
            if service:
                results = retrieve_password(service, cipher)
                if results:
                    print(Fore.YELLOW + f"\n🔓 Passwords for '{service}':")
                    for username, password in results:
                        print(f"👤 {username} | 🔑 {password}")
                else:
                    print(Fore.RED + "❌ No passwords found for this service.")
            else:
                print(Fore.RED + "❌ Service name cannot be empty.")

        elif choice == "3":
            clear_screen()
            print(Fore.MAGENTA + "🛠️ Password Generator")
            try:
                length = int(input("🔢 Enter desired length: "))
                generated = generate_password(length)
                print(Fore.GREEN + f"🔐 Your password: {generated}")
            except ValueError:
                print(Fore.RED + "❌ Invalid number!")

        elif choice == "4":
            print(Fore.BLUE + "👋 Goodbye! Stay secure 💙")
            break

        else:
            print(Fore.RED + "❗ Invalid choice. Please try again.")

        input(Fore.LIGHTBLACK_EX + "\nPress Enter to continue...")
        clear_screen()
        print(Fore.CYAN + banner)

if __name__ == "__main__":
    main()
