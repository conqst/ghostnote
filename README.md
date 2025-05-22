# GhostNote – Encrypted Notes & Keylogger for Windows 🕵️‍♂️🔐

**GhostNote** is a stealthy note-taking app for Windows that encrypts all your notes using a global password and optionally logs your keystrokes in the background. It launches silently at startup and can be toggled via global hotkeys.

---

## Features

- 🔐 **Encrypted Notes**  
  Every note is securely encrypted using AES (via Fernet). The default password is `1234`, but you should change it on first use. Notes are stored locally as `.enc` files.

-  **Global Hotkeys (Customizable)**  
  - `Ctrl + Alt + G` → Show/hide the GUI  
  - `Ctrl + Alt + K` → Start/stop the keylogger  
  You can change these hotkeys inside the app.

-  **Optional Keylogger**  
  When enabled, it logs keystrokes in the background and saves them as encrypted notes (prefixed with `LOG_`). System shortcuts (like Ctrl, Alt) are ignored.

-  **Tabbed Interface (GUI built with Tkinter)**  
  - **Notes:** View, create, or delete encrypted notes  
  - **Change Password:** Securely update your encryption password  
  - **Settings:** Customize hotkeys and monitor keylogger status

-  **Auto-Startup Enabled**  
  After the first launch, GhostNote adds itself to your system’s startup via a `.lnk` shortcut, so it runs silently on every boot.

---

##  Installation Options

###  Option 1: Source Code (For Developers)

> Requires Python 3.8+ on Windows

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ghostnote.git
   cd ghostnote


2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   

3. Run the app:
   ```bash
   python ghostnote.py


###  Option 2: Precompiled .exe (For End Users)

    No Python required

        1. Go to the Releases
        
        2. Download the latest GhostNote.zip
        
        3. Extract it and run GhostNote.exe
        
        4. The app will launch in the background and can be toggled with hotkeys


📁 Project Structure

    ghostnote/
    ├── ghostnote.py        # Main launcher
    ├── config.py           # Loads/saves config (hotkeys, password hash, etc.)
    ├── encryption.py       # AES/Fernet encryption manager
    ├── keylogger.py        # Background keylogger engine
    ├── notes.py            # Encrypted note storage
    ├── gui.py              # GUI built with tkinter
    ├── requirements.txt
    └── README.md


⚠️ Disclaimer
    This project includes a keylogger module. It is intended only for personal, educational, and ethical use.
    Recording others without consent may be illegal in your country. Use responsibly.


👤 Author
Created by conqst
🔗 GitHub: https://github.com/conqst
