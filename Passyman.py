# =======================================
# Imports
# =======================================

import json 
import base64
import os
import sys

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from getpass import getpass

# =======================================
# Encryption
# =======================================
def encrypt_credential(data, key):
    fernet = Fernet(key)
    json_data = json.dumps(data)
    encrypted_data = fernet.encrypt(json_data.encode())
    return encrypted_data
def decrypt_credential(data, key):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(data)
    json_data = decrypted_data.decode()
    credentials = json.loads(json_data)
    return credentials

# =======================================
# Authentication
# =======================================
def verify_master_password():        
    while True:
        master_pass = getpass("Enter Master Password: ")
        salt = load_salt()
        key = derive_key(master_pass, salt)
            
        try:
            credentials = load_credential(key)
            return True, key, credentials
        
        except FileNotFoundError:
            credentials = []
            print("No saved credentials found. Creating new save...")
            return True, key, credentials 
    
        except InvalidToken:
            print("Incorrect Password")
            choice2 = input("Try again? Y/N: ").lower().strip()
            if choice2 not in ['y', 'yes']:
                return False, None, None
def generate_key():
    if os.path.exists("key.key"):
        with open("key.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)
    return key
def derive_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm= hashes.SHA256(),
        length= 32,
        salt= salt,
        iterations= 600_000
    )
    key = kdf.derive(password.encode())
    key = base64.urlsafe_b64encode(key)
    return key
def generate_salt():
    salt = os.urandom(16)
    with open("salt.bin", "wb") as salt_file:
        salt_file.write(salt)
        return salt
def load_salt():
    if os.path.exists("salt.bin"):
        with open("salt.bin", "rb") as salt_file:
            salt = salt_file.read()
            return salt
    else:
        salt = generate_salt()
        return salt

# =======================================
# Credential Management
# =======================================
def add_credential(credentials, accname, website, username, password):
    credential = {
        "account_name": accname,
        "website": website,
        "username": username,
        "password": password
    }
    credentials.append(credential)
    print(f"Credential for {accname} added successfully.")
def save_credential(credentials, key):
    encrypted_accounts = encrypt_credential(credentials, key)
    with open("credentials.enc", "wb") as accounts:
        accounts.write(encrypted_accounts)   
def display_credential(credentials):
    count = 1
    print("Which account would you like to view? ")
    print("0: Exit")
    for cred in credentials:        
        print(f"{count}:" ,cred["account_name"])
        count += 1

    while True:
        try:
            choice = int(input("Enter account number: "))

            if choice == 0:
                print("Goodbye")
                print("=" * 20)
                return None
            selection = credentials[choice - 1]

            print("=" * 20)
            print("Account: ", selection["account_name"])
            print("Website: ", selection["website"])
            print("Username: ", selection["username"])
            print("Password: ", "****************")
            print("=" * 20)

            return selection
        except ValueError:
            print("Not a valid number. Try again.")
            print("=" * 20)

        except IndexError:
            print("Account does not exist")
            print("=" * 20)                
def reveal_password(credentials):
   credential = display_credential(credentials)

   if credential is None:
       return
   
   yesno = input("Reveal password? (Y/N): ").lower().strip()
   if yesno not in ['y' ,'yes']:
        print("=" * 20)
        print("Password remaining hidden for privacy")
        print("=" * 20)
   else:
        print("=" * 20)
        print("Password: ", credential["password"])
        print("=" * 20)
def edit_credential(credentials):
    print("Which account would you like to edit?: ")
    print("=" * 20)
    credential = display_credential(credentials)

    if credential is None:
        return
    
    while True: 
        print("1. Account Name")
        print("2. Website Name")
        print("3. Username")  
        print("4. Account's Password")
        print("0. Exit")

        choice = input("What part of the credential do you want to edit?: ")
        
        if choice == "0":
            print("Goodbye")
            return
            
        elif choice == "1":
            rename = input("What would you like to rename the account to? ")
            save_choice = input("Save changes? Y/N: ").lower().strip()
            
            if save_choice not in ['y', 'yes']:
                return 
            
            credential.update({"account_name": rename})
            save_credential(credentials, key)
            return
                     
        elif choice == "2":
            rename = input("What would you like to rename the website to? ")
            save_choice = input("Save changes? Y/N: ").lower().strip()

            if save_choice not in ['y', 'yes']:
                return
            
            credential.update({"website": rename})
            save_credential(credentials, key)
            return
            
        elif choice == "3":
            rename = input("What would you like to rename the username to? ")
            save_choice = input("Save changes? Y/N: ").lower().strip()

            if save_choice not in ['y', 'yes']:
                return
            
            credential.update({"username": rename})    
            save_credential(credentials, key)    
            return


        elif choice == "4":
            rename = input("What would you like to rename the password to? ")   
            save_choice = input("Save changes? Y/N: ").lower().strip()

            if save_choice not in ['y', 'yes']:
                return
            
            credential.update({"password": rename})
            save_credential(credentials, key)    
            return
        else:
            print("Not a valid choice. Try again.")
def delete_credential(credentials):
    print("Which account would you like to delete?: ")
    print("=" * 20)
    credential = display_credential(credentials)

    if credential is None:
        return

    while True:
        choice = input(f"Delete account {credential['account_name']} Y/N?: " ).lower().strip()
        if choice not in ['y', 'yes']:
            return
        
        print("WARNING:")
        print("This will delete the entry and cannot be restored.")
        print("Please enter master password to confirm")
        authenticated, key, _ = verify_master_password()
        if not authenticated:
            return
        credentials.remove(credential)
        save_credential(credentials, key)
        print("Account deleted")
        print("=" * 20)
        return        
def load_credential(key):
    with open("credentials.enc", "rb") as accounts:
        encrypted_accounts = accounts.read()
        credentials = decrypt_credential(encrypted_accounts, key)
        return credentials

if __name__ == "__main__":
    print("Welcome to Passy")   
    authenticated, key, credentials = verify_master_password()

    if not authenticated:
        print("Goodbye")
        sys.exit()        

    while True:
        print("1: Add Credential")
        print("2: View Credentials")
        print("3: Edit a Credential")
        print("4: Delete a Credential")
        print("5: Exit")

        choice = input("What would you like to do? ")
        if choice == "1":
            while True:
                accname = input("What is the name of the account: ")
                website = input("Name of website for account: ")
                username = input("Username for account: ")
                password = input("Password for account: ")

                add_credential(credentials, accname, website, username, password)
                repeat = input("Add another account? (Y/N): ").lower().strip()
                if repeat not in ['y', 'yes']:
                    print("Done!")
                    break
            save_credential(credentials, key)

        elif choice == "2":
            try:
                reveal_password(credentials)
                
            except FileNotFoundError:
                print("No credentials found.")

        elif choice == "3":
            edit_credential(credentials)

        elif choice == "4":
            delete_credential(credentials)
                
        elif choice == "5":
            break

        else:
           again = input("Sorry! Invalid response! Try again? Y/N ").lower().strip()
           if again not in ['y', 'yes']:
               print("Goodbye")
               break