# 📖 Smart Offline Dictionary
### with Voice Input, TTS, Synonyms/Antonyms, History & Favorites

---

## 📁 Project Structure

```
smart_dictionary/
│
├── main_app.py           ← Run this to launch the app
├── dictionary_engine.py  ← Word lookup, suggestions, Word of the Day
├── voice_manager.py      ← TTS (pyttsx3) + STT (speech_recognition)
├── db_manager.py         ← SQLite: history & favorites
├── setup_nltk.py         ← One-time WordNet download script
├── requirements.txt      ← All dependencies
│
└── data/
    ├── dictionary.json   ← Offline word database (100+ words)
    └── smart_dict.db     ← Auto-created SQLite database
```

---

## ⚙️ Installation Steps

### Step 1 — Make sure Python 3.8+ is installed
```
python --version
```

### Step 2 — Install dependencies
```
pip install -r requirements.txt
```

> **PyAudio note** (for voice input):
> - **Windows**: `pip install pyaudio`
> - **macOS**: `brew install portaudio && pip install pyaudio`
> - **Linux**: `sudo apt install portaudio19-dev python3-dev && pip install pyaudio`

### Step 3 — Download WordNet data (one time only)
```
python setup_nltk.py
```

### Step 4 — Run the app
```
python main_app.py
```

---

## 🖥️ How to Use

| Feature | How |
|---|---|
| Search a word | Type in the box → press Enter or click 🔍 Search |
| Voice input | Click 🎤 Voice → speak a word |
| Hear meaning | Click 🔊 Speak |
| Add to favorites | Click ♡ Favorite after searching |
| Remove favorite | Select in left panel → click Remove |
| Lookup from history | Double-click any entry in the left panel |
| Word of the Day | Click ✨ Word of the Day (top right) |
| Spell suggestions | Click any suggestion button if word not found |

---

## 🌟 Features Summary

- ✅ **100+ word offline dictionary** (JSON file — no internet needed)
- ✅ **Spell suggestions** via Python's `difflib`
- ✅ **Synonyms & Antonyms** via NLTK WordNet
- ✅ **Word of the Day** (random each session)
- ✅ **Voice input** via `speech_recognition`
- ✅ **Text-to-speech** via `pyttsx3` (fully offline)
- ✅ **Search history** saved to SQLite
- ✅ **Favorites** saved to SQLite
- ✅ **Dark themed GUI** built with Tkinter

---

## 💡 Optional Improvements

1. **Expand the dictionary** — Add more words to `data/dictionary.json`
2. **Import from external source** — Write a one-time script to pull words from PyDictionary and cache them in the JSON
3. **Export favorites** — Add a button to export favorites as a PDF or text file
4. **Quiz mode** — Flash cards from your favorites list
5. **Pronunciation** — Add phonetic spelling to the JSON
6. **Themes** — Add a light mode toggle
7. **Fully offline STT** — Install `pocketsphinx` for voice recognition without internet

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: tkinter` | `sudo apt install python3-tk` (Linux) |
| `pyttsx3` error on Linux | `sudo apt install espeak` |
| PyAudio install fails | See platform notes in Step 2 above |
| "Microphone not found" | Check OS microphone permissions |
| Synonyms show "—" | Run `python setup_nltk.py` to download WordNet |
