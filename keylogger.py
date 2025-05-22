from pynput import keyboard

class Keylogger:
    """
    Records keystrokes and can be started/stopped using a global hotkey.
    """
    def __init__(self):
        self.listener = None
        self.active = False
        self.log_buffer = []  # Stores collected characters
        self.ctrl_active = False
        self.alt_active = False

    def _on_press(self, key):
        """
        Internal method called when a key is pressed.
        Ignores system shortcuts (Ctrl/Alt).
        """
        try:
            if key.char:
                if self.ctrl_active or self.alt_active:
                    return
                self.log_buffer.append(key.char)
        except AttributeError:
            if key == keyboard.Key.space:
                self.log_buffer.append(" ")
            elif key == keyboard.Key.enter:
                self.log_buffer.append("\n")
            elif key == keyboard.Key.tab:
                self.log_buffer.append("\t")
            elif key == keyboard.Key.backspace:
                if self.log_buffer:
                    self.log_buffer.pop()
            elif key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl]:
                self.ctrl_active = True
            elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr]:
                self.alt_active = True
            # Other special keys like Shift, Esc etc. are ignored

    def _on_release(self, key):
        """
        Internal method called when a key is released.
        Resets modifier flags.
        """
        if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl]:
            self.ctrl_active = False
        elif key in [keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr]:
            self.alt_active = False

    def start_logging(self):
        """
        Starts global keyboard listener in the background.
        """
        if not self.active:
            self.log_buffer = []
            self.ctrl_active = False
            self.alt_active = False
            self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self.listener.start()
            self.active = True

    def stop_logging(self) -> str:
        """
        Stops the listener and returns collected keystrokes as a string.
        """
        collected_text = ""
        if self.active:
            try:
                self.listener.stop()
            except Exception:
                pass
            try:
                self.listener.join(timeout=0.1)
            except Exception:
                pass
            self.active = False
            collected_text = "".join(self.log_buffer)
            self.log_buffer = []
        return collected_text
