import sys
import threading
import time
import uuid
import customtkinter as ctk
import pyperclip
from password_generator import PasswordGenerator
from data_access import DataAccess

# Initialize UI aesthetics
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

VAULT_FILE = "vault.enc"
CLIPBOARD_TIMEOUT = 30

class PasswordManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Secure Local Vault - Antigravity Password Manager")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        self.master_password = None
        self.vault_data = None
        
        # Track the last copied value to only clear it if the user hasn't copied something else
        self.last_copied_password = None
        
        # Configure grid system
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        self.show_login_screen()

    def show_login_screen(self):
        self.clear_main_container()
        frame = ctk.CTkFrame(self, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        
        vault_exists = DataAccess.vault_exists(VAULT_FILE)
        
        title_text = "Login to Vault" if vault_exists else "Create New Vault"
        title_label = ctk.CTkLabel(frame, text=title_text, font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(30, 20), padx=40)
        
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Master Password", show="*", width=250)
        self.password_entry.pack(pady=10, padx=40)
        
        self.error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.error_label.pack(pady=5)
        
        if vault_exists:
            btn_text = "Unlock"
            action = self.unlock_vault
        else:
            self.confirm_password_entry = ctk.CTkEntry(frame, placeholder_text="Confirm Master Password", show="*", width=250)
            self.confirm_password_entry.pack(pady=(0, 10), padx=40)
            btn_text = "Create Vault"
            action = self.create_vault
            
        action_btn = ctk.CTkButton(frame, text=btn_text, command=action, width=250)
        action_btn.pack(pady=(10, 30), padx=40)
        
        # Bind enter key
        self.bind('<Return>', lambda event: action())

    def clear_main_container(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_vault(self):
        password = self.password_entry.get()
        confirm = self.confirm_password_entry.get()
        
        if not password:
            self.error_label.configure(text="Password cannot be empty.")
            return
        if password != confirm:
            self.error_label.configure(text="Passwords do not match.")
            return
            
        success = DataAccess.initialize_vault(VAULT_FILE, password)
        if success:
            self.master_password = password
            self.load_vault_data()
            self.show_main_vault_screen()
        else:
            self.error_label.configure(text="Error creating vault.")

    def unlock_vault(self):
        password = self.password_entry.get()
        if not password:
            self.error_label.configure(text="Please enter password.")
            return
            
        try:
            self.vault_data = DataAccess.load_vault(VAULT_FILE, password)
            self.master_password = password
            self.show_main_vault_screen()
        except ValueError:
            self.error_label.configure(text="Incorrect password or corrupted vault.")
        except Exception as e:
            self.error_label.configure(text=f"Error: {str(e)}")

    def load_vault_data(self):
        try:
            self.vault_data = DataAccess.load_vault(VAULT_FILE, self.master_password)
        except Exception as e:
            print(f"Failed to load vault data: {e}")

    def show_main_vault_screen(self):
        self.clear_main_container()
        self.unbind('<Return>')
        
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(4, weight=1)
        
        logo_label = ctk.CTkLabel(sidebar, text="Password\nManager", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        add_btn = ctk.CTkButton(sidebar, text="+ Add Entry", command=self.show_add_entry_dialog)
        add_btn.grid(row=1, column=0, padx=20, pady=10)
        
        lock_btn = ctk.CTkButton(sidebar, text="Lock Vault", command=self.lock_vault, fg_color="transparent", border_width=2)
        lock_btn.grid(row=5, column=0, padx=20, pady=(10, 20))
        
        # Main Area
        self.main_area = ctk.CTkScrollableFrame(self)
        self.main_area.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.grid_columnconfigure(1, weight=5)
        
        self.populate_entries()

    def lock_vault(self):
        self.master_password = None
        self.vault_data = None
        self.show_login_screen()

    def populate_entries(self):
        for widget in self.main_area.winfo_children():
            widget.destroy()
            
        title_label = ctk.CTkLabel(self.main_area, text="Your Vault Entries", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20), columnspan=4)
        
        entries = self.vault_data.get("entries", [])
        if not entries:
            empty_lbl = ctk.CTkLabel(self.main_area, text="Vault is empty. Add a new entry.", text_color="gray")
            empty_lbl.grid(row=1, column=0, sticky="w", pady=10)
            return

        # Headers
        ctk.CTkLabel(self.main_area, text="Platform", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(self.main_area, text="Username", font=ctk.CTkFont(weight="bold")).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(self.main_area, text="Actions", font=ctk.CTkFont(weight="bold")).grid(row=1, column=2, sticky="w", padx=10, pady=5)

        for idx, entry in enumerate(entries):
            row = idx + 2
            
            # Use small frames for aesthetic rows
            row_frame = ctk.CTkFrame(self.main_area, fg_color="transparent")
            row_frame.grid(row=row, column=0, columnspan=3, sticky="we", pady=5)
            row_frame.grid_columnconfigure(1, weight=1)
            
            ctk.CTkLabel(row_frame, text=entry.get('platform', 'N/A'), width=150, anchor="w").grid(row=0, column=0, padx=10)
            ctk.CTkLabel(row_frame, text=entry.get('username', 'N/A'), width=200, anchor="w").grid(row=0, column=1, padx=10)
            
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.grid(row=0, column=2, sticky="e")
            
            copy_btn = ctk.CTkButton(actions_frame, text="Copy", width=60, command=lambda e=entry: self.copy_password(e['password']))
            copy_btn.pack(side="left", padx=5)
            
            edit_btn = ctk.CTkButton(actions_frame, text="Edit", width=60, fg_color="#F2A900", hover_color="#C68A00", 
                                     command=lambda e=entry: self.show_add_entry_dialog(e))
            edit_btn.pack(side="left", padx=5)
            
            del_btn = ctk.CTkButton(actions_frame, text="Delete", width=60, fg_color="#D32F2F", hover_color="#B71C1C", 
                                    command=lambda e=entry: self.delete_entry(e['id']))
            del_btn.pack(side="left", padx=5)

    def show_add_entry_dialog(self, entry=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add/Edit Entry")
        dialog.geometry("450x550")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (450 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (550 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text="Platform/URL:").pack(pady=(20, 5), padx=20, anchor="w")
        platform_var = ctk.StringVar(value=entry['platform'] if entry else "")
        platform_entry = ctk.CTkEntry(dialog, textvariable=platform_var, width=400)
        platform_entry.pack(padx=20, pady=5)
        
        ctk.CTkLabel(dialog, text="Username:").pack(pady=5, padx=20, anchor="w")
        user_var = ctk.StringVar(value=entry['username'] if entry else "")
        user_entry = ctk.CTkEntry(dialog, textvariable=user_var, width=400)
        user_entry.pack(padx=20, pady=5)
        
        ctk.CTkLabel(dialog, text="Password:").pack(pady=5, padx=20, anchor="w")
        pwd_var = ctk.StringVar(value=entry['password'] if entry else "")
        pwd_entry = ctk.CTkEntry(dialog, textvariable=pwd_var, width=400, show="*")
        pwd_entry.pack(padx=20, pady=5)
        
        # Password generator buttons
        gen_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        gen_frame.pack(fill="x", padx=20, pady=5)
        
        def toggle_show():
            if pwd_entry.cget('show') == '*':
                pwd_entry.configure(show='')
            else:
                pwd_entry.configure(show='*')
                
        def gen_pwd():
            new_pwd = PasswordGenerator.generate_password(length=16)
            pwd_var.set(new_pwd)
            pwd_entry.configure(show='') # Usually nice to see newly generated password
            
        show_btn = ctk.CTkButton(gen_frame, text="Show/Hide", width=80, command=toggle_show)
        show_btn.pack(side="left", padx=(0, 10))
        
        gen_btn = ctk.CTkButton(gen_frame, text="Generate Strong Password", command=gen_pwd)
        gen_btn.pack(side="left")
        
        ctk.CTkLabel(dialog, text="Notes:").pack(pady=5, padx=20, anchor="w")
        notes_text = ctk.CTkTextbox(dialog, width=400, height=80)
        notes_text.pack(padx=20, pady=5)
        if entry and entry.get('notes'):
            notes_text.insert("1.0", entry['notes'])
            
        error_lbl = ctk.CTkLabel(dialog, text="", text_color="red")
        error_lbl.pack(pady=5)
        
        def save():
            plat = platform_var.get().strip()
            usr = user_var.get().strip()
            pwd = pwd_var.get().strip()
            nts = notes_text.get("1.0", "end-1c").strip()
            
            if not plat or not pwd:
                error_lbl.configure(text="Platform and Password are required.")
                return
                
            if entry:
                # Update
                entry['platform'] = plat
                entry['username'] = usr
                entry['password'] = pwd
                entry['notes'] = nts
            else:
                # Create
                new_entry = {
                    'id': str(uuid.uuid4()),
                    'platform': plat,
                    'username': usr,
                    'password': pwd,
                    'notes': nts
                }
                self.vault_data.setdefault("entries", []).append(new_entry)
                
            if DataAccess.save_vault(VAULT_FILE, self.master_password, self.vault_data):
                self.populate_entries()
                dialog.destroy()
            else:
                error_lbl.configure(text="Failed to save vault.")
                
        save_btn = ctk.CTkButton(dialog, text="Save Entry", command=save)
        save_btn.pack(pady=20)
        
    def delete_entry(self, entry_id):
        # In a real app, you might want a confirmation dialog here
        self.vault_data["entries"] = [e for e in self.vault_data["entries"] if e["id"] != entry_id]
        if DataAccess.save_vault(VAULT_FILE, self.master_password, self.vault_data):
            self.populate_entries()

    def copy_password(self, password):
        pyperclip.copy(password)
        self.last_copied_password = password
        
        # Start a background thread to clear the clipboard after timeout
        threading.Thread(target=self.clear_clipboard_delayed, daemon=True).start()
        
    def clear_clipboard_delayed(self):
        time.sleep(CLIPBOARD_TIMEOUT)
        # Only clear if the clipboard still contains the password we copied
        # This prevents annoying behavior if the user copied something else in the meantime
        if pyperclip.paste() == self.last_copied_password:
            pyperclip.copy('')
