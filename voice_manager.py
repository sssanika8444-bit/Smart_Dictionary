"""
voice_manager.py
Handles:
- Voice input  : speech_recognition (Google Web Speech API offline fallback)
- Voice output : pyttsx3 (fully offline TTS)
"""

import threading

# ── TTS (pyttsx3) ─────────────────────────────────────────────────────────────
try:
    import pyttsx3
    _tts_engine = pyttsx3.init()
    _tts_engine.setProperty("rate", 155)   # words per minute
    _tts_engine.setProperty("volume", 0.9)
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False
    _tts_engine = None

# ── STT (speech_recognition) ─────────────────────────────────────────────────
try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except Exception:
    STT_AVAILABLE = False
    sr = None


# ─────────────────────────────────────────────────────────────────────────────
# Text-to-Speech
# ─────────────────────────────────────────────────────────────────────────────

def speak(text: str):
    """
    Speak the given text in a background thread so the GUI doesn't freeze.
    """
    if not TTS_AVAILABLE or not _tts_engine:
        return

    def _run():
        try:
            _tts_engine.say(text)
            _tts_engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error] {e}")

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()


def set_speech_rate(rate: int):
    """Adjust TTS speed (default 155 wpm)."""
    if TTS_AVAILABLE and _tts_engine:
        _tts_engine.setProperty("rate", rate)


# ─────────────────────────────────────────────────────────────────────────────
# Speech-to-Text
# ─────────────────────────────────────────────────────────────────────────────

def listen_once(timeout: int = 5, phrase_limit: int = 4) -> tuple:
    """
    Listen from the microphone and return (success: bool, text_or_error: str).

    Uses Google Web Speech API by default.
    Falls back to Sphinx (offline) if google fails — Sphinx must be installed
    separately (`pip install pocketsphinx`) for full offline STT.
    """
    if not STT_AVAILABLE:
        return False, "speech_recognition library not installed."

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.energy_threshold = 300

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_limit
            )
    except sr.WaitTimeoutError:
        return False, "No speech detected. Please try again."
    except OSError:
        return False, "Microphone not found or not accessible."
    except Exception as e:
        return False, f"Microphone error: {e}"

    # Try Google (needs internet for first use; cached for some systems)
    try:
        text = recognizer.recognize_google(audio)
        return True, text.strip()
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        pass

    # Fallback: Sphinx (fully offline)
    try:
        text = recognizer.recognize_sphinx(audio)
        return True, text.strip()
    except Exception:
        pass

    return False, "Could not understand speech. Please speak clearly."
