"""
main_app.py
Smart Offline Dictionary – Main GUI Application
Built with Tkinter. Run this file to start the app.

Features:
  ✓ Word lookup from offline JSON dictionary
  ✓ Spell suggestions (difflib)
  ✓ Synonyms & Antonyms (NLTK WordNet)
  ✓ Word of the Day
  ✓ Voice Input (speech_recognition)
  ✓ Text-to-Speech output (pyttsx3)
  ✓ Search History & Favorites (SQLite)
  ✓ Attractive dark-themed UI
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading

import db_manager
import dictionary_engine
import voice_manager


# ═══════════════════════════════════════════════════════════════════════════════
# THEME / COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
COLORS = {
    "bg_dark":      "#0F1117",   # main background
    "bg_panel":     "#1A1D27",   # card / panel background
    "bg_input":     "#252836",   # input field background
    "accent":       "#6C63FF",   # purple accent
    "accent_hover": "#8B85FF",
    "accent2":      "#FF6584",   # pink accent (favorites)
    "text_primary": "#E8E8F0",
    "text_secondary":"#9A9AB0",
    "text_muted":   "#5A5A7A",
    "success":      "#4ECCA3",
    "warning":      "#FFD166",
    "border":       "#2E3148",
    "wotd_bg":      "#1E1040",
}

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEADER = ("Segoe UI", 13, "bold")
FONT_BODY   = ("Segoe UI", 11)
FONT_SMALL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)
FONT_WORD   = ("Segoe UI", 18, "bold")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, bg=None, fg=None, width=None, font_=None):
    """Create a flat, styled button."""
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg or COLORS["accent"],
        fg=fg or "#FFFFFF",
        activebackground=COLORS["accent_hover"],
        activeforeground="#FFFFFF",
        relief="flat", cursor="hand2",
        font=font_ or FONT_BODY,
        width=width or 0,
        padx=10, pady=6,
        bd=0,
    )
    return btn


def section_label(parent, text):
    """Section header label."""
    return tk.Label(
        parent, text=text,
        bg=COLORS["bg_panel"],
        fg=COLORS["accent"],
        font=FONT_HEADER,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class SmartDictionaryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📖 Smart Offline Dictionary")
        self.root.geometry("1100x740")
        self.root.minsize(900, 620)
        self.root.configure(bg=COLORS["bg_dark"])

        # State
        self.current_word = tk.StringVar()
        self.is_listening = False
        self.is_favorite = False

        # Init DB
        db_manager.init_db()

        # Build UI
        self._build_header()
        self._build_main_area()
        self._build_status_bar()

        # Load Word of the Day on startup
        self._show_word_of_day()

    # ──────────────────────────────────────────────────────────────────────────
    # HEADER
    # ──────────────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=COLORS["bg_panel"], pady=0)
        header.pack(fill="x")

        # Left: Title
        left = tk.Frame(header, bg=COLORS["bg_panel"])
        left.pack(side="left", padx=20, pady=14)
        tk.Label(left, text="📖", bg=COLORS["bg_panel"], fg=COLORS["accent"],
                 font=("Segoe UI", 28)).pack(side="left")
        tk.Label(left, text="Smart Dictionary",
                 bg=COLORS["bg_panel"], fg=COLORS["text_primary"],
                 font=FONT_TITLE).pack(side="left", padx=(8, 0))
        tk.Label(left, text="  Offline · Voice · Intelligent",
                 bg=COLORS["bg_panel"], fg=COLORS["text_muted"],
                 font=("Segoe UI", 10, "italic")).pack(side="left", pady=(6, 0))

        # Right: Word of the Day button
        right = tk.Frame(header, bg=COLORS["bg_panel"])
        right.pack(side="right", padx=20)
        styled_button(
            right, "✨ Word of the Day", self._show_word_of_day,
            bg=COLORS["wotd_bg"], font_=("Segoe UI", 10)
        ).pack()

        # Separator
        tk.Frame(self.root, bg=COLORS["border"], height=1).pack(fill="x")

    # ──────────────────────────────────────────────────────────────────────────
    # MAIN AREA (3 columns)
    # ──────────────────────────────────────────────────────────────────────────
    def _build_main_area(self):
        main = tk.Frame(self.root, bg=COLORS["bg_dark"])
        main.pack(fill="both", expand=True, padx=0, pady=0)

        # Left sidebar (History + Favorites)
        self._build_left_panel(main)

        # Center (search + results)
        self._build_center_panel(main)

    # ──────────────────────────────────────────────────────────────────────────
    # LEFT PANEL – History & Favorites
    # ──────────────────────────────────────────────────────────────────────────
    def _build_left_panel(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg_panel"], width=220)
        frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        frame.pack_propagate(False)

        # ── Favorites ──────────────────────────────────────────────────────
        tk.Label(frame, text="❤  Favorites",
                 bg=COLORS["bg_panel"], fg=COLORS["accent2"],
                 font=FONT_HEADER).pack(anchor="w", padx=14, pady=(14, 4))

        fav_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        fav_frame.pack(fill="both", padx=8, expand=False)

        self.fav_listbox = tk.Listbox(
            fav_frame, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            selectbackground=COLORS["accent2"], relief="flat",
            font=FONT_BODY, height=8, activestyle="none",
            highlightthickness=0, bd=0,
        )
        self.fav_listbox.pack(fill="both", side="left", expand=True)
        self.fav_listbox.bind("<Double-Button-1>", self._fav_double_click)

        fav_scroll = tk.Scrollbar(fav_frame, command=self.fav_listbox.yview,
                                  troughcolor=COLORS["bg_panel"], bg=COLORS["border"])
        fav_scroll.pack(side="right", fill="y")
        self.fav_listbox.config(yscrollcommand=fav_scroll.set)

        btn_row = tk.Frame(frame, bg=COLORS["bg_panel"])
        btn_row.pack(fill="x", padx=8, pady=(4, 0))
        styled_button(btn_row, "Remove", self._remove_favorite,
                      bg="#3A1A2E", fg=COLORS["accent2"],
                      font_=FONT_SMALL).pack(side="right")

        tk.Frame(frame, bg=COLORS["border"], height=1).pack(fill="x", padx=8, pady=10)

        # ── History ────────────────────────────────────────────────────────
        tk.Label(frame, text="🕐  History",
                 bg=COLORS["bg_panel"], fg=COLORS["accent"],
                 font=FONT_HEADER).pack(anchor="w", padx=14, pady=(0, 4))

        hist_frame = tk.Frame(frame, bg=COLORS["bg_panel"])
        hist_frame.pack(fill="both", padx=8, expand=True)

        self.hist_listbox = tk.Listbox(
            hist_frame, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            selectbackground=COLORS["accent"], relief="flat",
            font=FONT_BODY, activestyle="none",
            highlightthickness=0, bd=0,
        )
        self.hist_listbox.pack(fill="both", side="left", expand=True)
        self.hist_listbox.bind("<Double-Button-1>", self._hist_double_click)

        hist_scroll = tk.Scrollbar(hist_frame, command=self.hist_listbox.yview,
                                   troughcolor=COLORS["bg_panel"], bg=COLORS["border"])
        hist_scroll.pack(side="right", fill="y")
        self.hist_listbox.config(yscrollcommand=hist_scroll.set)

        btn_row2 = tk.Frame(frame, bg=COLORS["bg_panel"])
        btn_row2.pack(fill="x", padx=8, pady=(4, 10))
        styled_button(btn_row2, "Clear", self._clear_history,
                      bg="#1A1A2E", fg=COLORS["text_secondary"],
                      font_=FONT_SMALL).pack(side="right")

        self._refresh_lists()

    # ──────────────────────────────────────────────────────────────────────────
    # CENTER PANEL – Search & Results
    # ──────────────────────────────────────────────────────────────────────────
    def _build_center_panel(self, parent):
        center = tk.Frame(parent, bg=COLORS["bg_dark"])
        center.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

        # ── Search bar ─────────────────────────────────────────────────────
        search_card = tk.Frame(center, bg=COLORS["bg_panel"], pady=16)
        search_card.pack(fill="x")

        inner = tk.Frame(search_card, bg=COLORS["bg_panel"])
        inner.pack(padx=16)

        self.entry = tk.Entry(
            inner, textvariable=self.current_word,
            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            insertbackground=COLORS["accent"],
            font=("Segoe UI", 15), relief="flat",
            highlightthickness=2,
            highlightcolor=COLORS["accent"],
            highlightbackground=COLORS["border"],
            width=32, bd=0,
        )
        self.entry.pack(side="left", ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self._search())
        self.entry.focus()

        styled_button(inner, "🔍 Search", self._search,
                      font_=("Segoe UI", 12, "bold")).pack(side="left", ipady=4)

        # Voice input button
        self.voice_btn = styled_button(
            inner, "🎤 Voice", self._start_voice_input,
            bg="#1B2A3B", fg=COLORS["success"],
            font_=("Segoe UI", 11),
        )
        self.voice_btn.pack(side="left", padx=(8, 0), ipady=4)

        # Favorite toggle button
        self.fav_btn = styled_button(
            inner, "♡ Favorite", self._toggle_favorite,
            bg="#2A1A2E", fg=COLORS["accent2"],
            font_=("Segoe UI", 11),
        )
        self.fav_btn.pack(side="left", padx=(8, 0), ipady=4)

        # Speak button
        styled_button(
            inner, "🔊 Speak", self._speak_result,
            bg="#0D2020", fg=COLORS["success"],
            font_=("Segoe UI", 11),
        ).pack(side="left", padx=(8, 0), ipady=4)

        # ── Word of the Day banner ─────────────────────────────────────────
        self.wotd_frame = tk.Frame(center, bg=COLORS["wotd_bg"], pady=10)
        self.wotd_frame.pack(fill="x", pady=(8, 0))

        tk.Label(self.wotd_frame, text="✨ Word of the Day",
                 bg=COLORS["wotd_bg"], fg=COLORS["warning"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16)

        self.wotd_word_lbl = tk.Label(
            self.wotd_frame, text="",
            bg=COLORS["wotd_bg"], fg=COLORS["text_primary"],
            font=("Segoe UI", 14, "bold")
        )
        self.wotd_word_lbl.pack(anchor="w", padx=16)

        self.wotd_def_lbl = tk.Label(
            self.wotd_frame, text="", wraplength=680, justify="left",
            bg=COLORS["wotd_bg"], fg=COLORS["text_secondary"],
            font=("Segoe UI", 10)
        )
        self.wotd_def_lbl.pack(anchor="w", padx=16)

        # ── Results area ───────────────────────────────────────────────────
        result_card = tk.Frame(center, bg=COLORS["bg_panel"])
        result_card.pack(fill="both", expand=True, pady=(8, 0))

        # Word title + meaning
        top_area = tk.Frame(result_card, bg=COLORS["bg_panel"])
        top_area.pack(fill="x", padx=16, pady=(14, 0))

        self.result_word_lbl = tk.Label(
            top_area, text="Enter a word to search",
            bg=COLORS["bg_panel"], fg=COLORS["text_muted"],
            font=FONT_WORD, anchor="w"
        )
        self.result_word_lbl.pack(anchor="w")

        self.result_meaning_lbl = tk.Label(
            top_area, text="",
            bg=COLORS["bg_panel"], fg=COLORS["text_primary"],
            font=("Segoe UI", 12), wraplength=680, justify="left", anchor="w"
        )
        self.result_meaning_lbl.pack(anchor="w", pady=(4, 0))

        tk.Frame(result_card, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=10)

        # Synonyms & Antonyms
        syn_ant = tk.Frame(result_card, bg=COLORS["bg_panel"])
        syn_ant.pack(fill="x", padx=16)

        # Synonyms
        syn_col = tk.Frame(syn_ant, bg=COLORS["bg_panel"])
        syn_col.pack(side="left", fill="both", expand=True)
        tk.Label(syn_col, text="Synonyms", bg=COLORS["bg_panel"],
                 fg=COLORS["success"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.syn_lbl = tk.Label(
            syn_col, text="—", bg=COLORS["bg_panel"],
            fg=COLORS["text_secondary"], font=FONT_BODY,
            wraplength=300, justify="left"
        )
        self.syn_lbl.pack(anchor="w", pady=(2, 0))

        # Antonyms
        ant_col = tk.Frame(syn_ant, bg=COLORS["bg_panel"])
        ant_col.pack(side="left", fill="both", expand=True, padx=(20, 0))
        tk.Label(ant_col, text="Antonyms", bg=COLORS["bg_panel"],
                 fg=COLORS["accent2"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.ant_lbl = tk.Label(
            ant_col, text="—", bg=COLORS["bg_panel"],
            fg=COLORS["text_secondary"], font=FONT_BODY,
            wraplength=300, justify="left"
        )
        self.ant_lbl.pack(anchor="w", pady=(2, 0))

        tk.Frame(result_card, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=10)

        # Suggestions
        tk.Label(result_card, text="Did you mean?",
                 bg=COLORS["bg_panel"], fg=COLORS["warning"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16)

        self.suggestions_frame = tk.Frame(result_card, bg=COLORS["bg_panel"])
        self.suggestions_frame.pack(anchor="w", padx=14, pady=(4, 12))

    # ──────────────────────────────────────────────────────────────────────────
    # STATUS BAR
    # ──────────────────────────────────────────────────────────────────────────
    def _build_status_bar(self):
        tk.Frame(self.root, bg=COLORS["border"], height=1).pack(fill="x")
        bar = tk.Frame(self.root, bg=COLORS["bg_panel"], pady=5)
        bar.pack(fill="x")
        self.status_var = tk.StringVar(value="Ready  •  Double-click history/favorites to look up a word")
        tk.Label(bar, textvariable=self.status_var,
                 bg=COLORS["bg_panel"], fg=COLORS["text_muted"],
                 font=FONT_SMALL).pack(side="left", padx=14)

        # TTS / STT availability indicators
        indicators = []
        if voice_manager.TTS_AVAILABLE:
            indicators.append("🔊 TTS ✓")
        else:
            indicators.append("🔊 TTS ✗")
        if voice_manager.STT_AVAILABLE:
            indicators.append("🎤 STT ✓")
        else:
            indicators.append("🎤 STT ✗")

        tk.Label(bar, text="  |  ".join(indicators),
                 bg=COLORS["bg_panel"], fg=COLORS["text_muted"],
                 font=FONT_SMALL).pack(side="right", padx=14)

    # ══════════════════════════════════════════════════════════════════════════
    # CORE ACTIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _search(self, word_override: str = None):
        """Main search action."""
        word = word_override or self.current_word.get().strip()
        if not word:
            self._set_status("Please enter a word.")
            return

        self.current_word.set(word)
        result = dictionary_engine.lookup_word(word)

        # Clear suggestions
        for w in self.suggestions_frame.winfo_children():
            w.destroy()

        if result["found"]:
            self._display_result(result)
            db_manager.add_to_history(word)
            self._refresh_lists()
            self._set_status(f"Found: {word.capitalize()}")
        else:
            # Not found
            self.result_word_lbl.config(
                text=f'"{word}"  — not found',
                fg=COLORS["accent2"]
            )
            self.result_meaning_lbl.config(text="")
            self.syn_lbl.config(text="—")
            self.ant_lbl.config(text="—")

            if result["suggestions"]:
                self._set_status(f"Word not found. Showing suggestions for '{word}'.")
                self._show_suggestions(result["suggestions"])
                # Show the best match's meaning dimly
                if result["meaning"]:
                    self.result_meaning_lbl.config(
                        text=f'Best match ({result["suggestions"][0]}): {result["meaning"]}',
                        fg=COLORS["text_muted"]
                    )
            else:
                self._set_status(f"No results for '{word}'.")

        # Update favorite button state
        self.is_favorite = db_manager.is_favorite(word)
        self._update_fav_btn()

    def _display_result(self, result: dict):
        """Populate the result area with a found word's data."""
        word = result["word"]
        meaning = result["meaning"]
        synonyms = result["synonyms"]
        antonyms = result["antonyms"]

        self.result_word_lbl.config(
            text=word.capitalize(),
            fg=COLORS["text_primary"]
        )
        self.result_meaning_lbl.config(
            text=meaning,
            fg=COLORS["text_primary"]
        )

        self.syn_lbl.config(
            text=", ".join(synonyms) if synonyms else "—",
            fg=COLORS["text_secondary"] if synonyms else COLORS["text_muted"]
        )
        self.ant_lbl.config(
            text=", ".join(antonyms) if antonyms else "—",
            fg=COLORS["text_secondary"] if antonyms else COLORS["text_muted"]
        )

    def _show_suggestions(self, suggestions: list):
        """Render clickable suggestion buttons."""
        for sug in suggestions:
            btn = tk.Button(
                self.suggestions_frame, text=sug,
                bg=COLORS["bg_input"], fg=COLORS["warning"],
                activebackground=COLORS["accent"],
                activeforeground="#FFF",
                relief="flat", cursor="hand2",
                font=FONT_BODY, padx=10, pady=4, bd=0,
                command=lambda w=sug: self._search(w)
            )
            btn.pack(side="left", padx=4)

    def _show_word_of_day(self):
        """Display a random Word of the Day in the banner."""
        word, meaning = dictionary_engine.word_of_the_day()
        self.wotd_word_lbl.config(text=word.capitalize())
        # Trim meaning to fit banner
        short = meaning if len(meaning) <= 120 else meaning[:117] + "..."
        self.wotd_def_lbl.config(text=short)

    def _toggle_favorite(self):
        """Add or remove current word from favorites."""
        word = self.current_word.get().strip().lower()
        if not word:
            self._set_status("Search a word first to favorite it.")
            return

        if self.is_favorite:
            db_manager.remove_from_favorites(word)
            self.is_favorite = False
            self._set_status(f"Removed '{word}' from favorites.")
        else:
            added = db_manager.add_to_favorites(word)
            self.is_favorite = True
            if added:
                self._set_status(f"Added '{word}' to favorites! ❤")
            else:
                self._set_status(f"'{word}' is already in favorites.")

        self._update_fav_btn()
        self._refresh_lists()

    def _update_fav_btn(self):
        """Update favorite button text."""
        if self.is_favorite:
            self.fav_btn.config(text="♥ Favorited", fg=COLORS["accent2"])
        else:
            self.fav_btn.config(text="♡ Favorite", fg=COLORS["accent2"])

    def _speak_result(self):
        """Read the current meaning aloud."""
        word = self.current_word.get().strip()
        meaning = self.result_meaning_lbl.cget("text")
        if not word or not meaning:
            self._set_status("Nothing to speak. Search a word first.")
            return
        if not voice_manager.TTS_AVAILABLE:
            self._set_status("TTS not available. Install pyttsx3.")
            return
        text = f"{word}. {meaning}"
        voice_manager.speak(text)
        self._set_status(f"🔊 Speaking: {word}")

    def _start_voice_input(self):
        """Start microphone listening in a background thread."""
        if self.is_listening:
            return
        if not voice_manager.STT_AVAILABLE:
            messagebox.showwarning(
                "Not Available",
                "speech_recognition is not installed.\n"
                "Run: pip install SpeechRecognition"
            )
            return

        self.is_listening = True
        self.voice_btn.config(text="🔴 Listening...", state="disabled")
        self._set_status("🎤 Listening... Speak a word now.")

        def listen_thread():
            success, text = voice_manager.listen_once(timeout=6, phrase_limit=3)
            self.root.after(0, lambda: self._handle_voice_result(success, text))

        threading.Thread(target=listen_thread, daemon=True).start()

    def _handle_voice_result(self, success: bool, text: str):
        """Called on main thread after voice input completes."""
        self.is_listening = False
        self.voice_btn.config(text="🎤 Voice", state="normal")

        if success:
            self.current_word.set(text.lower().strip())
            self._set_status(f'🎤 Heard: "{text}"')
            self._search()
        else:
            self._set_status(f"🎤 {text}")

    # ──────────────────────────────────────────────────────────────────────────
    # HISTORY / FAVORITES LIST ACTIONS
    # ──────────────────────────────────────────────────────────────────────────

    def _refresh_lists(self):
        """Reload history and favorites listboxes."""
        self.hist_listbox.delete(0, "end")
        for word, ts in db_manager.get_history(limit=40):
            self.hist_listbox.insert("end", f"  {word}")

        self.fav_listbox.delete(0, "end")
        for word, ts in db_manager.get_favorites():
            self.fav_listbox.insert("end", f"  {word}")

    def _hist_double_click(self, event):
        sel = self.hist_listbox.curselection()
        if sel:
            word = self.hist_listbox.get(sel[0]).strip()
            self.current_word.set(word)
            self._search()

    def _fav_double_click(self, event):
        sel = self.fav_listbox.curselection()
        if sel:
            word = self.fav_listbox.get(sel[0]).strip()
            self.current_word.set(word)
            self._search()

    def _remove_favorite(self):
        sel = self.fav_listbox.curselection()
        if not sel:
            self._set_status("Select a favorite word first.")
            return
        word = self.fav_listbox.get(sel[0]).strip()
        db_manager.remove_from_favorites(word)
        self._refresh_lists()
        self._set_status(f"Removed '{word}' from favorites.")
        if self.current_word.get().strip().lower() == word:
            self.is_favorite = False
            self._update_fav_btn()

    def _clear_history(self):
        if messagebox.askyesno("Clear History", "Delete all search history?"):
            db_manager.clear_history()
            self._refresh_lists()
            self._set_status("History cleared.")

    # ──────────────────────────────────────────────────────────────────────────
    # UTILITIES
    # ──────────────────────────────────────────────────────────────────────────

    def _set_status(self, message: str):
        self.status_var.set(message)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartDictionaryApp(root)
    root.mainloop()
