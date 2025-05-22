import os
from datetime import datetime

class NoteManager:
    def __init__(self, enc_manager, notes_dir: str):
        self.enc = enc_manager
        self.notes_dir = notes_dir
        os.makedirs(self.notes_dir, exist_ok=True)

    def _save_note_file(self, base_name: str, content: str) -> str:
        filename = base_name + ".enc"
        file_path = os.path.join(self.notes_dir, filename)
        if os.path.exists(file_path):
            index = 1
            base = base_name
            while os.path.exists(file_path):
                filename = f"{base}({index}).enc"
                file_path = os.path.join(self.notes_dir, filename)
                index += 1
        encrypted_data = self.enc.encrypt(content.encode('utf-8'))
        with open(file_path, 'wb') as f:
            f.write(encrypted_data)
        return filename

    def add_note(self, title: str, content: str) -> str:
        safe_title = "".join([c if c.isalnum() or c in " _-" else "_" for c in title]).strip()
        safe_title = safe_title.replace(" ", "_") or "Note"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{safe_title}_{timestamp}"
        return self._save_note_file(base_name, content)

    def add_log(self, content: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"LOG_{timestamp}"
        return self._save_note_file(base_name, content)

    def list_notes(self):
        files = [f for f in os.listdir(self.notes_dir) if f.endswith('.enc')]
        files.sort(key=lambda name: os.path.getmtime(os.path.join(self.notes_dir, name)), reverse=True)
        return files

    def read_note_content(self, filename: str) -> str:
        file_path = os.path.join(self.notes_dir, filename)
        with open(file_path, 'rb') as f:
            encrypted_bytes = f.read()
        plaintext_bytes = self.enc.decrypt(encrypted_bytes)
        return plaintext_bytes.decode('utf-8', errors='ignore')

    def delete_note(self, filename: str) -> bool:
        try:
            os.remove(os.path.join(self.notes_dir, filename))
            return True
        except Exception:
            return False
