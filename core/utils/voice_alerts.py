import pyttsx3
import threading

class VoiceAlert:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self._lock = threading.Lock()

    def speak(self, text):
        def _target():
            with self._lock:
                self.engine.say(text)
                self.engine.runAndWait()
        
        thread = threading.Thread(target=_target)
        thread.start()

voice_alert = VoiceAlert()

def notify_pothole(severity="Medium"):
    if severity == "High":
        msg = "Critical Warning! Major road damage detected ahead. Reduce speed immediately."
    elif severity == "Medium":
        msg = "Caution: Pothole detected ahead. Maintain awareness."
    else:
        msg = "Minor road irregularity detected."
    
    voice_alert.speak(msg)

def notify_lane_departure():
    voice_alert.speak("Warning: Vehicle drifting from lane. Please correct steering.")
