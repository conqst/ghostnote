import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class GhostNoteGUI:
    def __init__(self, root, note_manager, config: dict, app):
        self.root = root
        self.note_manager = note_manager
        self.config = config
        self.app = app

        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill='both')

        # Notes Tab
        notes_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(notes_frame, text="Notes")
        self.notes_list = tk.Listbox(notes_frame)
        self.notes_list.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(notes_frame, orient='vertical', command=self.notes_list.yview)
        scrollbar.pack(side='right', fill='y')
        self.notes_list.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(notes_frame)
        btn_frame.pack(fill='x', pady=5)
        tk.Button(btn_frame, text="View", width=10, command=self._on_view_note).pack(side='left', padx=5)
        tk.Button(btn_frame, text="New Note", width=12, command=self._on_add_note).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete", width=10, command=self._on_delete_note).pack(side='left', padx=5)

        self.notes_list.bind("<Double-Button-1>", lambda event: self._on_view_note())

        # Change Password Tab
        pass_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(pass_frame, text="Change Password")
        ttk.Label(pass_frame, text="Current Password:").pack(anchor='w', padx=10, pady=(10, 0))
        self.current_pass_entry = ttk.Entry(pass_frame, show="*")
        self.current_pass_entry.pack(fill='x', padx=10)
        ttk.Label(pass_frame, text="New Password:").pack(anchor='w', padx=10, pady=(10, 0))
        self.new_pass_entry = ttk.Entry(pass_frame, show="*")
        self.new_pass_entry.pack(fill='x', padx=10)
        ttk.Label(pass_frame, text="Confirm Password:").pack(anchor='w', padx=10, pady=(10, 0))
        self.confirm_pass_entry = ttk.Entry(pass_frame, show="*")
        self.confirm_pass_entry.pack(fill='x', padx=10)
        ttk.Button(pass_frame, text="Change Password", command=self._on_change_password).pack(pady=10)

        # Settings Tab
        settings_frame = ttk.Frame(self.tab_control)
        self.tab_control.add(settings_frame, text="Settings")
        ttk.Label(settings_frame, text="Hotkey - GUI:").pack(anchor='w', padx=10, pady=(10, 0))
        self.gui_hotkey_entry = ttk.Entry(settings_frame)
        self.gui_hotkey_entry.pack(fill='x', padx=10)
        ttk.Label(settings_frame, text="Hotkey - Keylogger:").pack(anchor='w', padx=10, pady=(10, 0))
        self.key_hotkey_entry = ttk.Entry(settings_frame)
        self.key_hotkey_entry.pack(fill='x', padx=10)
        self.gui_hotkey_entry.insert(0, self.config.get("gui_hotkey", "<ctrl>+<alt>+g"))
        self.key_hotkey_entry.insert(0, self.config.get("keylogger_hotkey", "<ctrl>+<alt>+k"))
        ttk.Button(settings_frame, text="Save", command=self._on_save_settings).pack(pady=10)

        self.keylogger_status_label = ttk.Label(settings_frame, text="Keylogger OFF")
        self.keylogger_status_label.pack(anchor='w', padx=10, pady=(5, 0))

        self.refresh_notes_list()

    def toggle_visibility(self):
        if self.root.state() == "withdrawn":
            self.root.deiconify()
            self.refresh_notes_list()
        else:
            self.root.withdraw()

    def refresh_notes_list(self):
        self.notes_list.delete(0, tk.END)
        try:
            files = self.note_manager.list_notes()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load notes: {e}")
            return
        for filename in files:
            name = filename[:-4] if filename.lower().endswith(".enc") else filename
            self.notes_list.insert(tk.END, name)

    def _on_view_note(self):
        if not self.notes_list.curselection():
            return
        filename = self.notes_list.get(self.notes_list.curselection()[0]) + ".enc"
        pwd = simpledialog.askstring("Password", "Enter password:", show="*")
        if pwd is None:
            return
        if not self._validate_password(pwd):
            messagebox.showerror("Error", "Invalid password.")
            return
        try:
            content = self.note_manager.read_note_content(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed: {e}")
            return
        view_win = tk.Toplevel(self.root)
        view_win.title("Note Viewer")
        view_win.geometry("400x300")
        text_widget = tk.Text(view_win, wrap='word')
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')
        text_widget.pack(fill='both', expand=True, padx=5, pady=5)
        scroll = ttk.Scrollbar(view_win, orient='vertical', command=text_widget.yview)
        text_widget.config(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')

    def _on_add_note(self):
        new_win = tk.Toplevel(self.root)
        new_win.title("New Note")
        new_win.geometry("300x400")
        tk.Label(new_win, text="Title:").pack(anchor='w', padx=10, pady=(10, 0))
        title_entry = tk.Entry(new_win)
        title_entry.pack(fill='x', padx=10)
        tk.Label(new_win, text="Content:").pack(anchor='w', padx=10, pady=(10, 0))
        content_text = tk.Text(new_win, height=15)
        content_text.pack(fill='both', expand=True, padx=10, pady=5)

        def save_note():
            title = title_entry.get().strip()
            content = content_text.get("1.0", tk.END)
            if not title and not content.strip():
                messagebox.showwarning("Warning", "Empty note.")
                new_win.destroy()
                return
            try:
                self.note_manager.add_note(title or "Note", content)
            except Exception as e:
                messagebox.showerror("Error", f"Saving failed: {e}")
                return
            new_win.destroy()
            self.refresh_notes_list()

        button_frame = tk.Frame(new_win)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Save", command=save_note).pack(side='left', padx=5)
        tk.Button(button_frame, text="Cancel", command=new_win.destroy).pack(side='left', padx=5)
        title_entry.focus_set()

    def _on_delete_note(self):
        if not self.notes_list.curselection():
            return
        index = self.notes_list.curselection()[0]
        filename = self.notes_list.get(index) + ".enc"
        confirm = messagebox.askyesno("Confirm", f"Delete note \"{self.notes_list.get(index)}\"?")
        if not confirm:
            return
        try:
            success = self.note_manager.delete_note(filename)
            if success:
                self.refresh_notes_list()
            else:
                messagebox.showerror("Error", "Deletion failed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete: {e}")

    def _on_change_password(self):
        old = self.current_pass_entry.get()
        new = self.new_pass_entry.get()
        confirm = self.confirm_pass_entry.get()
        if not old or not new or not confirm:
            messagebox.showerror("Error", "All fields are required.")
            return
        if new != confirm:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        result = self.app.change_password(old, new)
        if result:
            self.current_pass_entry.delete(0, tk.END)
            self.new_pass_entry.delete(0, tk.END)
            self.confirm_pass_entry.delete(0, tk.END)

    def _on_save_settings(self):
        gui_hotkey = self._normalize_hotkey(self.gui_hotkey_entry.get())
        key_hotkey = self._normalize_hotkey(self.key_hotkey_entry.get())
        if not gui_hotkey or not key_hotkey:
            messagebox.showerror("Error", "Invalid hotkey format.")
            return
        if gui_hotkey == key_hotkey:
            messagebox.showerror("Error", "Hotkeys must be different.")
            return
        success = self.app.update_hotkeys(gui_hotkey, key_hotkey)
        if success:
            self.gui_hotkey_entry.delete(0, tk.END)
            self.key_hotkey_entry.delete(0, tk.END)
            self.gui_hotkey_entry.insert(0, gui_hotkey)
            self.key_hotkey_entry.insert(0, key_hotkey)
            messagebox.showinfo("Success", "Hotkeys saved.")

    def _normalize_hotkey(self, hotkey_str: str) -> str:
        parts = [p.strip().lower() for p in hotkey_str.replace("+", " ").replace("-", " ").split() if p.strip()]
        keys = []
        for token in parts:
            if token in ("ctrl", "<ctrl>", "control"):
                keys.append("<ctrl>")
            elif token in ("alt", "<alt>", "menu"):
                keys.append("<alt>")
            elif token in ("shift", "<shift>"):
                keys.append("<shift>")
            elif token in ("cmd", "<cmd>", "win", "<win>"):
                keys.append("<cmd>")
            elif len(token) == 1:
                keys.append(token)
            else:
                return None
        return "+".join(keys)

    def update_keylogger_status(self, is_active: bool):
        self.keylogger_status_label.config(text="Keylogger ON" if is_active else "Keylogger OFF")

    def _validate_password(self, pwd: str) -> bool:
        import hashlib
        salt = self.config.get("salt", "")
        expected_hash = self.config.get("password_hash", "")
        test_hash = hashlib.sha256((pwd + salt).encode('utf-8')).hexdigest()
        return test_hash == expected_hash
