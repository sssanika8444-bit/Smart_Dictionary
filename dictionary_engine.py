"""
dictionary_engine.py
Core logic for:
- Loading the offline JSON dictionary
- Looking up word meanings
- Suggesting similar words (spell check)
- Fetching synonyms/antonyms via NLTK WordNet
- Providing Word of the Day
"""

import json
import os
import random
import difflib

# ── NLTK WordNet (optional but loaded if available) ──────────────────────────
try:
    from nltk.corpus import wordnet
    WORDNET_AVAILABLE = True
except Exception:
    WORDNET_AVAILABLE = False

DICT_PATH = os.path.join(os.path.dirname(__file__), "data", "dictionary.json")


def load_dictionary() -> dict:
    """Load the JSON dictionary file into a Python dict."""
    if not os.path.exists(DICT_PATH):
        return {}
    with open(DICT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Load once at import time so it's fast during lookups
_DICTIONARY = load_dictionary()


def lookup_word(word: str) -> dict:
    """
    Look up a word and return a result dict with:
    - meaning, suggestions, synonyms, antonyms
    """
    word = word.strip().lower()
    result = {
        "word": word,
        "meaning": None,
        "suggestions": [],
        "synonyms": [],
        "antonyms": [],
        "found": False,
    }

    if not word:
        return result

    # ── Exact match ──────────────────────────────────────────────────────────
    if word in _DICTIONARY:
        result["meaning"] = _DICTIONARY[word]
        result["found"] = True
        result["synonyms"], result["antonyms"] = get_synonyms_antonyms(word)
        return result

    # ── Fuzzy suggestions ────────────────────────────────────────────────────
    suggestions = difflib.get_close_matches(
        word, _DICTIONARY.keys(), n=5, cutoff=0.6
    )
    result["suggestions"] = suggestions

    # If there's a very close match, auto-fill its meaning too
    if suggestions:
        best = suggestions[0]
        result["meaning"] = _DICTIONARY.get(best)
        result["synonyms"], result["antonyms"] = get_synonyms_antonyms(best)

    return result


def get_synonyms_antonyms(word: str):
    """Return (synonyms_list, antonyms_list) using NLTK WordNet."""
    synonyms = set()
    antonyms = set()

    if not WORDNET_AVAILABLE:
        return [], []

    try:
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                name = lemma.name().replace("_", " ")
                if name.lower() != word.lower():
                    synonyms.add(name)
                for antonym in lemma.antonyms():
                    antonyms.add(antonym.name().replace("_", " "))
    except Exception:
        pass

    return sorted(synonyms)[:8], sorted(antonyms)[:6]


def word_of_the_day() -> tuple:
    """Return a random (word, meaning) tuple from the dictionary."""
    if not _DICTIONARY:
        return ("---", "Dictionary not loaded.")
    word = random.choice(list(_DICTIONARY.keys()))
    return (word, _DICTIONARY[word])


def all_words() -> list:
    """Return all words in the dictionary (sorted)."""
    return sorted(_DICTIONARY.keys())


def reload_dictionary():
    """Reload dictionary from disk (useful if file is updated)."""
    global _DICTIONARY
    _DICTIONARY = load_dictionary()
