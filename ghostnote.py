import os
import sys
import hashlib
import tkinter as tk
from tkinter import messagebox, simpledialog
from pynput import keyboard

from config import load_config, save_config, create_default_config
from encryption import EncryptionManager
from notes import NoteManager
from keylogger import Keylogger
from gui import GhostNoteGUI

# App directories
APP_DIR = os.path.join(os.getenv('LOCALAPPDATA', os.getenv('APPDATA', os.path.expanduser('~'))), "GhostNote")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")
NOTES_DIR = os.path.join(APP_DIR, "notes")


class GhostNoteApp:
    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)

        if not os.path.isfile(CONFIG_PATH):
            self.config = create_default_config()
        else:
            try:
                self.config = load_config()
                required_keys = {"password_hash", "salt", "gui_hotkey", "keylogger_hotkey"}
                if not required_keys.issubset(self.config.keys()):
                    self.config = create_default_config()
            except Exception:
                messagebox.showwarning("Warning", "Corrupted configuration – resetting to default.")
                self.config = create_default_config()

        self.current_password = None
        for _ in range(3):
            password = simpledialog.askstring("Password", "Enter your password:", show="*")
            if password:
                hashed = hashlib.sha256((password + self.config["salt"]).encode('utf-8')).hexdigest()
                if hashed == self.config["password_hash"]:
                    self.current_password = password
                    break

        if self.current_password is None:
            messagebox.showerror("Error", "Too many failed attempts. Exiting.")
            exit(1)

        self.enc_manager = EncryptionManager(self.current_password, self.config["salt"])
        self.note_manager = NoteManager(self.enc_manager, NOTES_DIR)
        self.keylogger = Keylogger()

        self.root = tk.Tk()
        self.root.title("GhostNote")
        self.root.withdraw()
        self.gui = GhostNoteGUI(self.root, self.note_manager, self.config, self)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.hotkey_listener = None
        self._setup_hotkeys()

    def _setup_hotkeys(self):
        """Configure global hotkeys for toggling GUI and keylogger."""
        def on_show_gui():
            self.root.after(0, self.gui.toggle_visibility)

        def on_toggle_keylogger():
            self.root.after(0, self.toggle_keylogger)

        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({
                self.config["gui_hotkey"]: on_show_gui,
                self.config["keylogger_hotkey"]: on_toggle_keylogger
            })
            self.hotkey_listener.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to register hotkeys: {e}")

    def toggle_keylogger(self):
        """Start or stop keylogger and save logs if needed."""
        if not self.keylogger.active:
            self.keylogger.start_logging()
            if hasattr(self.gui, "update_keylogger_status"):
                self.gui.update_keylogger_status(True)
        else:
            content = self.keylogger.stop_logging()
            if content:
                try:
                    self.note_manager.add_log(content)
                except Exception as e:
                    messagebox.showwarning("Warning", f"Failed to save keystroke log: {e}")
            if self.root.state() != 'withdrawn':
                self.gui.refresh_notes_list()
            if hasattr(self.gui, "update_keylogger_status"):
                self.gui.update_keylogger_status(False)

    def change_password(self, old_pass: str, new_pass: str):
        """Change encryption password and re-encrypt all notes."""
        salt_str = self.config.get("salt", "")
        hash_check = hashlib.sha256((old_pass + salt_str).encode('utf-8')).hexdigest()
        if hash_check != self.config.get("password_hash", ""):
            messagebox.showerror("Error", "Current password is incorrect.")
            return False
        if not new_pass:
            messagebox.showerror("Error", "New password cannot be empty.")
            return False

        new_enc_manager = EncryptionManager(new_pass, self.config["salt"])
        old_enc_manager = self.enc_manager
        files = self.note_manager.list_notes()
        decrypted_data = {}

        try:
            for filename in files:
                file_path = os.path.join(NOTES_DIR, filename)
                with open(file_path, 'rb') as f:
                    encrypted_bytes = f.read()
                plaintext_bytes = old_enc_manager.decrypt(encrypted_bytes)
                decrypted_data[filename] = plaintext_bytes
        except Exception as e:
            messagebox.showerror("Error", f"Aborted: failed to decrypt a file: {e}")
            return False

        try:
            for filename, plaintext_bytes in decrypted_data.items():
                file_path = os.path.join(NOTES_DIR, filename)
                new_encrypted = new_enc_manager.encrypt(plaintext_bytes)
                with open(file_path, 'wb') as f:
                    f.write(new_encrypted)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write re-encrypted notes: {e}")
            return False

        self.current_password = new_pass
        self.enc_manager = new_enc_manager
        self.note_manager.enc = new_enc_manager
        self.config["password_hash"] = hashlib.sha256((new_pass + self.config["salt"]).encode('utf-8')).hexdigest()
        save_config(self.config)
        messagebox.showinfo("Success", "Password changed successfully.")
        return True

    def update_hotkeys(self, new_gui_hotkey: str, new_keylog_hotkey: str) -> bool:
        """Update global hotkeys based on settings."""
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass
            self.hotkey_listener = None

        self.config["gui_hotkey"] = new_gui_hotkey
        self.config["keylogger_hotkey"] = new_keylog_hotkey

        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({
                new_gui_hotkey: lambda: self.hotkey_show_gui(),
                new_keylog_hotkey: lambda: self.hotkey_toggle_keylogger()
            })
            self.hotkey_listener.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply new hotkeys: {e}")
            self._setup_hotkeys()
            return False

        save_config(self.config)
        return True

    def hotkey_show_gui(self):
        self.root.after(0, self.gui.toggle_visibility)

    def hotkey_toggle_keylogger(self):
        self.root.after(0, self.toggle_keylogger)

    def run(self):
        self.root.mainloop()

    def quit(self):
        try:
            if self.keylogger.active:
                self.keylogger.stop_logging()
        except Exception:
            pass
        try:
            if self.hotkey_listener:
                self.hotkey_listener.stop()
        except Exception:
            pass
        self.root.destroy()


def add_to_startup():
    """Create shortcut in Windows Startup folder to enable auto-launch on system boot."""
    try:
        import winshell
        from win32com.client import Dispatch
        startup_path = os.path.join(os.getenv('APPDATA'), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
        shortcut_path = os.path.join(startup_path, "GhostNote.lnk")
        if not os.path.exists(shortcut_path):
            target = sys.executable  # Full path to .exe
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = os.path.dirname(target)
            shortcut.IconLocation = target
            shortcut.save()
    except Exception as e:
        print("Failed to add to startup:", e)


if __name__ == "__main__":
    add_to_startup()
    app = GhostNoteApp()
    app.run()
