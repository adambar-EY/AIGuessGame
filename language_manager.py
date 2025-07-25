"""
Language management system for the guessing game.
Supports multiple languages with easy translation management.
"""

import json
import os

class LanguageManager:
    """Manages game translations and language switching."""
    
    def __init__(self, languages_file="languages.json"):
        """Initialize the language manager."""
        self.languages = {}
        self.current_language = "en"  # Default to English
        self.translations = {}
        self.load_languages(languages_file)
    
    def load_languages(self, filename):
        """Load language definitions from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.languages = data.get('languages', {})
                
                # Set default language if available
                if 'en' in self.languages:
                    self.set_language('en')
                elif self.languages:
                    # Set first available language
                    self.set_language(list(self.languages.keys())[0])
                    
        except FileNotFoundError:
            # Fallback to English if file not found
            self.languages = {
                'en': {
                    'name': 'English',
                    'flag': '🇬🇧',
                    'translations': {
                        'welcome': '🎮 Welcome to the AI-Powered Guessing Game!',
                        'error': 'Error: Language file not found'
                    }
                }
            }
            self.set_language('en')
    
    def get_available_languages(self):
        """Get list of available languages."""
        return [(code, lang['name'], lang['flag']) for code, lang in self.languages.items()]
    
    def set_language(self, language_code):
        """Set the current language."""
        if language_code in self.languages:
            self.current_language = language_code
            self.translations = self.languages[language_code]['translations']
            return True
        return False
    
    def get_current_language(self):
        """Get current language info."""
        if self.current_language in self.languages:
            lang = self.languages[self.current_language]
            return {
                'code': self.current_language,
                'name': lang['name'],
                'flag': lang['flag']
            }
        return None
    
    def get_text(self, key, **kwargs):
        """Get translated text for a key with optional formatting."""
        text = self.translations.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text
    
    def get_list(self, key):
        """Get a list of strings for a key."""
        return self.translations.get(key, [])
    
    def translate_category_example(self, example):
        """Translate a category example to current language."""
        if self.current_language == 'en':
            return example
        
        category_examples = self.translations.get('category_examples', {})
        return category_examples.get(example, example)
    
    def is_quit_command(self, command):
        """Check if command is a quit command in current language."""
        quit_commands = self.get_list('quit_commands')
        return command.lower() in quit_commands
    
    def is_yes_command(self, command):
        """Check if command is a yes command in current language."""
        yes_commands = self.get_list('yes_commands')
        return command.lower() in yes_commands
    
    def is_list_command(self, command):
        """Check if command is a list command in current language."""
        list_command = self.get_text('list_command')
        return command.lower() == list_command.lower()
    
    def show_language_selection(self):
        """Display language selection menu."""
        print(self.get_text('select_language'))
        print("=" * 40)
        
        languages = self.get_available_languages()
        for i, (code, name, flag) in enumerate(languages, 1):
            current = " ← Current" if code == self.current_language else ""
            print(f"{i}. {flag} {name} ({code}){current}")
        
        print("=" * 40)
        return languages
    
    def select_language_interactive(self):
        """Interactive language selection."""
        languages = self.show_language_selection()
        
        while True:
            try:
                choice = input(f"\nSelect language (1-{len(languages)}): ").strip()
                
                if self._handle_numeric_choice(choice, languages):
                    return True
                elif self._handle_language_code_choice(choice):
                    return True
                else:
                    print("❌ Invalid selection. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return False
    
    def _handle_numeric_choice(self, choice, languages):
        """Handle numeric language selection."""
        if not choice.isdigit():
            return False
            
        index = int(choice) - 1
        if 0 <= index < len(languages):
            language_code = languages[index][0]
            return self._set_language_with_confirmation(language_code)
        return False
    
    def _handle_language_code_choice(self, choice):
        """Handle direct language code selection."""
        if choice.lower() in self.languages:
            return self._set_language_with_confirmation(choice.lower())
        return False
    
    def _set_language_with_confirmation(self, language_code):
        """Set language and display confirmation message."""
        if self.set_language(language_code):
            current_lang = self.get_current_language()
            if current_lang:
                print(f"\n✅ Language set to: {current_lang['flag']} {current_lang['name']}")
            return True
        return False
    
    def get_localized_prompt(self, category_hint=None, subcategory_hint=None):
        """Get localized prompt for AI generation."""
        if self.current_language == 'pl':
            # Polish prompt
            category_prompt = f" z kategorii {category_hint}" if category_hint else ""
            if subcategory_hint:
                category_prompt += f" (konkretnie związane z {subcategory_hint})"
            
            return f"""Wygeneruj losowy obiekt, osobę, miejsce lub koncept{category_prompt} do gry w zgadywanie.
            
            Odpowiedz obiektem JSON w dokładnie tym formacie:
            {{
                "name": "NazwaElementu",
                "facts": [
                    "Fakt 1 o elemencie (zacznij od 'Jestem' lub 'Mam')",
                    "Fakt 2 o elemencie",
                    "Fakt 3 o elemencie", 
                    "Fakt 4 o elemencie",
                    "Fakt 5 o elemencie (najbardziej specyficzny/identyfikujący)"
                ]
            }}
            
            Zasady:
            - Fakty powinny być stopniowo bardziej specyficzne i identyfikujące
            - Zacznij fakty od pierwszej osoby ("Jestem", "Mam", "Mieszkam", itp.)
            - Każdy fakt powinien być pojedynczym zdaniem
            - Zrób to wyzwaniem, ale sprawiedliwym
            - NIGDY nie ujawniaj bezpośrednio nazwy lub tytułu w faktach
            - Ostatni fakt powinien być bardzo charakterystyczny, ale nie może zawierać właściwej odpowiedzi
            - Używaj opisów, cech i kontekstu zamiast bezpośrednich nazw
            - Wszystkie fakty i nazwa muszą być w języku polskim"""
        else:
            # English prompt (default)
            category_prompt = f" from the category of {category_hint}" if category_hint else ""
            if subcategory_hint:
                category_prompt += f" (specifically related to {subcategory_hint})"
            
            return f"""Generate a random object, person, place, or concept{category_prompt} for a guessing game.
            
            Respond with a JSON object in this exact format:
            {{
                "name": "ItemName",
                "facts": [
                    "Fact 1 about the item (start with 'I am' or 'I have')",
                    "Fact 2 about the item",
                    "Fact 3 about the item", 
                    "Fact 4 about the item",
                    "Fact 5 about the item (most specific/identifying)"
                ]
            }}
            
            Rules:
            - Make facts progressively more specific and identifying
            - Start facts with first person ("I am", "I have", "I live", etc.)
            - Each fact should be a single sentence
            - Make it challenging but fair
            - NEVER directly reveal the name or title in the facts
            - The final fact should be very distinctive but must not contain the correct answer
            - Use descriptions, characteristics, and context instead of direct names
            - All facts and name must be in English"""
