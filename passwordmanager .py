import os
import json
from cryptography.fernet import Fernet
import customtkinter as ctk
from tkinter import messagebox
import pyperclip

class PasswordManager:
    def __init__(self, key_file='key.key', data_file='passwords.json'):
        self.key_file = key_file
        self.data_file = data_file
        self.load_key()

    def load_key(self):
        if not os.path.exists(self.key_file):
            print("Errore: File chiave 'key.key' non trovato. Si prega di generare un file chiave.")
            exit()

        with open(self.key_file, 'rb') as key_file:
            self.key = key_file.read()

        self.cipher_suite = Fernet(self.key)

    def encrypt_data(self, data):
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
        return decrypted_data

    def save_password(self, service, username, password):
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            data = {}

        data[service] = {
            'username': self.encrypt_data(username).decode(),
            'password': self.encrypt_data(password).decode()
        }

        with open(self.data_file, 'w') as file:
            json.dump(data, file)

    def retrieve_password(self, service):
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                if service in data:
                    username = self.decrypt_data(data[service]['username'])
                    password = self.decrypt_data(data[service]['password'])
                    return username, password
                else:
                    return None
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def delete_password(self, service):
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                if service in data:
                    data.pop(service)
                    with open(self.data_file, 'w') as file:
                        json.dump(data, file)
                    return True
                else:
                    return False
        except (json.JSONDecodeError, FileNotFoundError):
            return False

class PasswordManagerGUI(ctk.CTk):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.title("Gestore Password")
        self.geometry("400x300")

        self.create_widgets()

    def create_widgets(self):
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=20)

        actions = [("Salva una password", self.save_password),
                   ("Recupera una password", self.retrieve_password),
                   ("Cancella una password", self.delete_password),
                   ("Chiudi", self.quit)]

        for text, command in actions:
            button = ctk.CTkButton(self.button_frame, text=text, command=command, width=200)
            button.pack(pady=5)

    def save_password(self):
        self.new_window = SavePasswordWindow(self.manager)
        self.new_window.grab_set()

    def retrieve_password(self):
        self.new_window = RetrievePasswordWindow(self.manager)
        self.new_window.grab_set()

    def delete_password(self):
        self.new_window = DeletePasswordWindow(self.manager)
        self.new_window.grab_set()

class SavePasswordWindow(ctk.CTkToplevel):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.title("Salva una Password")
        self.geometry("400x300")

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Nome del servizio:").pack(pady=5)
        self.service_entry = ctk.CTkEntry(self)
        self.service_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Nome utente:").pack(pady=5)
        self.username_entry = ctk.CTkEntry(self)
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Password:").pack(pady=5)
        self.password_entry = ctk.CTkEntry(self, show="*")
        self.password_entry.pack(pady=5)

        ctk.CTkButton(self, text="Salva", command=self.save).pack(pady=10)

    def save(self):
        service = self.service_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        if service and username and password:
            self.manager.save_password(service, username, password)
            messagebox.showinfo("Successo", "Password salvata con successo!")
            self.destroy()
        else:
            messagebox.showerror("Errore", "Compila tutti i campi!")

class RetrievePasswordWindow(ctk.CTkToplevel):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.title("Recupera una Password")
        self.geometry("400x300")

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Nome del servizio:").pack(pady=5)
        self.service_entry = ctk.CTkEntry(self)
        self.service_entry.pack(pady=5)

        ctk.CTkButton(self, text="Recupera", command=self.retrieve).pack(pady=5)

        self.result_frame = ctk.CTkFrame(self)
        self.result_frame.pack(pady=10)

        self.username_label = ctk.CTkLabel(self.result_frame, text="")
        self.username_label.pack(pady=5)
        self.password_label = ctk.CTkLabel(self.result_frame, text="")
        self.password_label.pack(pady=5)
        self.copy_username_button = ctk.CTkButton(self.result_frame, text="Copia Nome Utente", command=self.copy_username)
        self.copy_username_button.pack(pady=5)
        self.copy_password_button = ctk.CTkButton(self.result_frame, text="Copia Password", command=self.copy_password)
        self.copy_password_button.pack(pady=5)

    def retrieve(self):
        service = self.service_entry.get()
        if service:
            result = self.manager.retrieve_password(service)
            if result:
                username, password = result
                self.username_label.configure(text=f"Nome utente: {username}")
                self.password_label.configure(text=f"Password: {password}")
                self.username = username
                self.password = password
            else:
                messagebox.showerror("Errore", "Password non trovata.")
                self.username_label.configure(text="")
                self.password_label.configure(text="")
        else:
            messagebox.showerror("Errore", "Inserisci il nome del servizio!")

    def copy_username(self):
        pyperclip.copy(self.username)

    def copy_password(self):
        pyperclip.copy(self.password)

class DeletePasswordWindow(ctk.CTkToplevel):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.title("Cancella una Password")
        self.geometry("400x200")

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Nome del servizio:").pack(pady=5)
        self.service_entry = ctk.CTkEntry(self)
        self.service_entry.pack(pady=5)

        ctk.CTkButton(self, text="Cancella", command=self.delete).pack(pady=5)

    def delete(self):
        service = self.service_entry.get()
        if service:
            if self.manager.delete_password(service):
                messagebox.showinfo("Successo", "Password cancellata con successo!")
            else:
                messagebox.showerror("Errore", "Password non trovata o non cancellabile.")
            self.destroy()
        else:
            messagebox.showerror("Errore", "Inserisci il nome del servizio!")

if __name__ == "__main__":
    manager = PasswordManager()
    app = PasswordManagerGUI(manager)
    app.mainloop()
