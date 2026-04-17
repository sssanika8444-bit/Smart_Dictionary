"""
setup_nltk.py
Run this ONCE after installing requirements to download WordNet data.
Usage: python setup_nltk.py
"""

import nltk

print("Downloading NLTK WordNet corpus (one-time setup)...")
nltk.download("wordnet")
nltk.download("omw-1.4")
print("\n✅ Setup complete! You can now run: python main_app.py")
