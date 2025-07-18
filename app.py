"""
Flask Web Application for AI-Powered Guessing Game
Modern, responsive web interface with real-time interactions
"""
from flask import Flask, render_template, jsonify, request, session
import os
import secrets
import json
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Import game modules  
from cloud_scoring import CloudScoreKeeper
from language_manager import LanguageManager
from scoring import GameSession, GameRound, ScoringSystem
from postgresql_db import PostgreSQLHandler
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
import jellyfish

# Load environment variables
load_dotenv()

# Constants
CATEGORIES_FILE = "categories.json"
NO_ACTIVE_SESSION_ERROR = "No active game session"
ENCODING_UTF8 = "utf-8"

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Initialize game components
score_keeper = CloudScoreKeeper()
lang_manager = LanguageManager()
scoring_system = ScoringSystem()
db_handler = PostgreSQLHandler()

# Game classes from console version
class GameCategoryManager:
    """Manages game categories and provides category-based hints."""
    
    def __init__(self, categories_file=CATEGORIES_FILE, lang_manager=None):
        """Initialize the category manager with categories from JSON file."""
        self.categories = []
        self.lang_manager = lang_manager
        self.generated_items = set()  # Track generated items to avoid duplicates
        self.category_usage_count = {}  # Track how many times each category/subcategory is used
        self.load_categories(categories_file)
        self.init_polish_translations()

    def load_categories(self, filename):
        """Load categories from JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.categories = data.get('categories', [])
        except FileNotFoundError:
            # If categories file is missing, this is a critical error
            # The application cannot function without categories
            raise FileNotFoundError(f"Critical: Categories file '{filename}' not found. Cannot start application.")
        except json.JSONDecodeError as e:
            # If categories file is corrupted, this is also critical
            raise ValueError(f"Critical: Categories file '{filename}' contains invalid JSON: {e}")

    def init_polish_translations(self):
        """Initialize Polish translations for categories."""
        try:
            with open('category_translations.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.polish_translations = data.get('category_translations', {}).get('pl', {})
        except FileNotFoundError:
            # If translations file is missing, log warning but continue with empty translations
            # The app can still function in English-only mode
            logging.warning("Category translations file not found. Polish translations will not be available.")
            self.polish_translations = {}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in category_translations.json: {e}")
            self.polish_translations = {}

    def find_category(self, name):
        """Find a category by name."""
        for cat in self.categories:
            if cat['name'].lower() == name.lower():
                return cat
        return None

    def get_category_hint(self, category_name):
        """Get a smart subcategory hint that avoids recently used ones."""
        category = self.find_category(category_name)
        if not category or not category.get('examples'):
            return None
        
        # Track usage for this category
        if category_name not in self.category_usage_count:
            self.category_usage_count[category_name] = {}
        
        examples = category['examples']
        usage_counts = self.category_usage_count[category_name]
        
        # If we haven't used all examples yet, prefer unused ones
        unused_examples = [ex for ex in examples if ex not in usage_counts]
        if unused_examples:
            chosen_hint = random.choice(unused_examples)
        else:
            # All examples have been used, choose the least used one
            min_usage = min(usage_counts.values())
            least_used = [ex for ex, count in usage_counts.items() if count == min_usage]
            chosen_hint = random.choice(least_used)
        
        # Update usage count
        usage_counts[chosen_hint] = usage_counts.get(chosen_hint, 0) + 1
        
        return self.get_localized_hint(chosen_hint)

    def get_localized_hint(self, english_hint):
        """Get localized version of a subcategory hint."""
        if not self.lang_manager or self.lang_manager.current_language == 'en':
            return english_hint
        return self.lang_manager.translate_category_example(english_hint)

    def get_random_category(self):
        """Get a random category."""
        return random.choice(self.categories) if self.categories else None

    def get_localized_category(self, category):
        """Get category with localized name and description."""
        if not self.lang_manager or self.lang_manager.current_language == 'en':
            return category
        
        category_name = category['name']
        if category_name in self.polish_translations:
            localized = {
                'name': self.polish_translations[category_name]['name'],
                'description': self.polish_translations[category_name]['description'],
                'original_name': category_name,  # Keep original for AI prompts
                'examples': []
            }
            
            # Localize examples using language manager
            for example in category.get('examples', []):
                translated_example = self.lang_manager.translate_category_example(example)
                localized['examples'].append(translated_example)
            
            return localized
        
        return category

    def get_category_names(self):
        """Get list of available category names."""
        return [cat['name'] for cat in self.categories]

    def find_category_by_any_name(self, name):
        """Find a category by English or Polish name."""
        name_lower = name.lower()
        
        # First try English names
        for cat in self.categories:
            if cat['name'].lower() == name_lower:
                return cat
        
        # Then try Polish names
        if self.lang_manager and self.lang_manager.current_language == 'pl':
            for cat in self.categories:
                if cat['name'] in self.polish_translations:
                    polish_name = self.polish_translations[cat['name']]['name']
                    if polish_name.lower() == name_lower:
                        return cat
        
        return None

    def get_category_display_name(self, category):
        """Get the display name for a category in current language."""
        if not self.lang_manager or self.lang_manager.current_language == 'en':
            return category['name']
        
        if category['name'] in self.polish_translations:
            return self.polish_translations[category['name']]['name']
        
        return category['name']

    def get_category_display_description(self, category):
        """Get the display description for a category in current language."""
        if not self.lang_manager or self.lang_manager.current_language == 'en':
            return category['description']
        
        if category['name'] in self.polish_translations:
            return self.polish_translations[category['name']]['description']
        
        return category['description']

    def add_generated_item(self, item_name):
        """Track a generated item to avoid duplicates."""
        self.generated_items.add(item_name.lower())
        logger.info(f"Added '{item_name}' to generated items list. Total unique items: {len(self.generated_items)}")
    
    def get_generated_items_for_category(self, category_name, subcategory=None):
        """Get list of recently generated items for a category to help AI avoid duplicates."""
        # Use database to get recent items instead of local memory for better accuracy
        try:
            if db_handler and db_handler.is_connected():
                return db_handler.get_recent_items_for_category(
                    category=category_name, 
                    subcategory=subcategory,
                    hours_back=48,  # Look back 48 hours
                    limit=30       # Limit to prevent prompt bloat
                )
        except Exception as e:
            logger.warning(f"Failed to get recent items from database: {e}")
        
        # Fallback to local memory
        return list(self.generated_items)
    
    def reset_tracking(self):
        """Reset tracking (useful for testing or long sessions)."""
        self.generated_items.clear()
        self.category_usage_count.clear()
        logger.info("Reset item tracking and category usage counts")

class AnswerChecker:
    """Handles answer checking with fuzzy matching using Jaro-Winkler algorithm."""
    
    def __init__(self, similarity_threshold=0.9):
        """Initialize with similarity threshold (0.9 = 90% similar)."""
        self.similarity_threshold = similarity_threshold

    def is_correct_answer(self, guess, correct_answer):
        """
        Check if the guess is correct using exact match or fuzzy matching.
        
        Args:
            guess (str): The player's guess
            correct_answer (str): The correct answer
            
        Returns:
            tuple: (is_correct, similarity_score, match_type)
        """
        if not guess or not correct_answer:
            return False, 0.0, "invalid"
        
        # Clean inputs
        guess_clean = guess.strip().lower()
        answer_clean = correct_answer.strip().lower()
        
        # Exact match
        if guess_clean == answer_clean:
            return True, 1.0, "exact"
        
        # Jaro-Winkler similarity
        similarity = jellyfish.jaro_winkler_similarity(guess_clean, answer_clean)
        
        if similarity >= self.similarity_threshold:
            return True, similarity, "similar"
        
        return False, similarity, "different"

    def get_feedback(self, guess, correct_answer, lang_manager=None):
        """Get feedback message for the guess."""
        _, similarity, match_type = self.is_correct_answer(guess, correct_answer)
        
        if lang_manager and lang_manager.current_language == 'pl':
            # Polish feedback
            if match_type == "exact":
                return "🎉 Poprawnie! Idealne dopasowanie!"
            elif match_type == "similar":
                return f"🎉 Poprawnie! Wystarczająco blisko! ({similarity:.1%} podobne)"
            elif similarity >= 0.7:
                return f"🔥 Bardzo blisko! ({similarity:.1%} podobne) - Spróbuj ponownie!"
            elif similarity >= 0.5:
                return f"🌟 Robi się cieplej! ({similarity:.1%} podobne) - Próbuj dalej!"
            else:
                return "❌ Nie całkiem - Spróbuj ponownie!"
        else:
            # English feedback
            if match_type == "exact":
                return "🎉 Correct! Perfect match!"
            elif match_type == "similar":
                return f"🎉 Correct! Close enough! ({similarity:.1%} similar)"
            elif similarity >= 0.7:
                return f"🔥 Very close! ({similarity:.1%} similar) - Try again!"
            elif similarity >= 0.5:
                return f"🌟 Getting warmer! ({similarity:.1%} similar) - Keep trying!"
            else:
                return "❌ Not quite right - Try again!"

class AzureOpenAIGameEngine:
    """Game engine that uses Azure OpenAI to generate random items and facts."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client with secure authentication."""
        # Get configuration from environment variables
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        # Check if we have the required environment variables
        if not self.endpoint or not self.deployment_name:
            logger.error("Azure OpenAI environment variables not configured. AI features will be disabled.")
            self.client = None
            return
        
        try:
            # Initialize Azure OpenAI client with appropriate authentication
            if self.api_key:
                # Use API key authentication for local development
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version,
                )
            else:
                # Use DefaultAzureCredential for production
                credential = DefaultAzureCredential()
                self.client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    azure_ad_token_provider=lambda: credential.get_token("https://cognitiveservices.azure.com/.default").token,
                    api_version=self.api_version,
                )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self.client = None

    def generate_game_item(self, category_hint=None, subcategory_hint=None, lang_manager=None, 
                          difficulty=None, category_manager=None, session_id=None, player_name=None):
        """Generate a random item with 5 facts using Azure OpenAI, with strong duplicate prevention."""
        # If Azure OpenAI client is not available, return fallback item
        if not self.client:
            logger.warning("Azure OpenAI client not available, returning fallback item")
            return self._get_fallback_item(lang_manager)
        
        generation_start_time = time.time()
        max_attempts = 5
        
        try:
            avoid_items = self._get_avoid_items(category_manager, category_hint, subcategory_hint)
            
            for attempt in range(max_attempts):
                try:
                    prompt = self._build_generation_prompt(
                        category_hint, subcategory_hint, lang_manager, difficulty, 
                        avoid_items, attempt
                    )
                    
                    response = self._call_openai_api(prompt, attempt)
                    generation_time_ms = int((time.time() - generation_start_time) * 1000)
                    
                    item = self._parse_openai_response(response)
                    
                    if self._is_duplicate_item(item['name'], category_hint, lang_manager, attempt, max_attempts):
                        avoid_items.append(item['name'])
                        continue
                    
                    self._track_generated_item(item, category_manager)
                    self._save_question_to_database(
                        item, category_hint, subcategory_hint, difficulty, lang_manager,
                        session_id, player_name, generation_time_ms, response
                    )
                    
                    return item
                    
                except (ValueError, KeyError) as parse_error:
                    logger.warning(f"Parse error in attempt {attempt + 1}: {parse_error}")
                    if attempt == max_attempts - 1:
                        raise
                    continue
            
            logger.error("No valid item generated after all attempts")
            # Try to get a question from the database first
            db_item = self._get_database_item(category_hint, lang_manager, db_handler)
            if db_item:
                logger.info("Using question from database as fallback")
                return db_item
            # If no database item available, return error item
            return self._get_fallback_item(lang_manager)
            
        except Exception as e:
            logger.error(f"Error generating game content: {e}")
            # Try to get a question from the database first
            db_item = self._get_database_item(category_hint, lang_manager, db_handler)
            if db_item:
                logger.info("Using question from database due to generation error")
                return db_item
            # If no database item available, return error item
            return self._get_fallback_item(lang_manager)
    
    def _get_avoid_items(self, category_manager, category_hint, subcategory_hint):
        """Get list of items to avoid based on recent generation."""
        if category_manager:
            return category_manager.get_generated_items_for_category(category_hint, subcategory_hint)
        return []
    
    def _build_generation_prompt(self, category_hint, subcategory_hint, lang_manager, 
                               difficulty, avoid_items, attempt):
        """Build the AI generation prompt with all context."""
        if lang_manager:
            return lang_manager.get_localized_prompt(category_hint, subcategory_hint)
        
        prompt = self._build_base_english_prompt(category_hint, subcategory_hint)
        prompt = self._add_avoidance_context(prompt, avoid_items)
        prompt = self._add_difficulty_context(prompt, difficulty)
        prompt = self._add_retry_context(prompt, attempt)
        
        return prompt
    
    def _build_base_english_prompt(self, category_hint, subcategory_hint):
        """Build the base English prompt template."""
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
- Ensure the final fact makes it very clear what the answer is
- BE CREATIVE AND UNIQUE - avoid common or obvious choices"""
    
    def _add_avoidance_context(self, prompt, avoid_items):
        """Add context about items to avoid."""
        if avoid_items:
            avoid_list = ", ".join(avoid_items[-15:])  # Show last 15 to avoid token limits
            prompt += f"\n\nIMPORTANT: Do NOT generate any of these recently used items: {avoid_list}"
            prompt += "\nChoose something completely different, unique, and creative."
        return prompt
    
    def _add_difficulty_context(self, prompt, difficulty):
        """Add difficulty-specific context to prompt."""
        if difficulty:
            prompt += f"\n\nDifficulty guideline: {difficulty.get('prompt_hint', '')}"
        return prompt
    
    def _add_retry_context(self, prompt, attempt):
        """Add retry-specific context for better uniqueness."""
        if attempt > 0:
            prompt += f"\n\nATTEMPT {attempt + 1}: This is a retry. Please be even MORE creative and unique. Avoid obvious choices!"
        return prompt
    
    def _call_openai_api(self, prompt, attempt):
        """Make the API call to OpenAI."""
        if not self.client:
            raise ValueError("Azure OpenAI client not available")
        
        return self.client.chat.completions.create(
            model=self.deployment_name or "gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates unique and engaging guessing game content. Always prioritize originality and avoid repetition. Be creative and think outside the box."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=min(0.9 + (attempt * 0.1), 1.0),  # Increase temperature on retries
            timeout=30
        )
    
    def _parse_openai_response(self, response):
        """Parse and validate the OpenAI response."""
        content = response.choices[0].message.content
        
        if content is None:
            raise ValueError("Empty response from Azure OpenAI")
        
        content = content.strip()
        
        # Extract JSON from the response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        item = json.loads(content)
        
        # Validate the response format
        if not isinstance(item, dict) or 'name' not in item or 'facts' not in item:
            raise ValueError("Invalid response format from Azure OpenAI")
        
        if not isinstance(item['facts'], list) or len(item['facts']) != 5:
            raise ValueError("Facts must be a list of exactly 5 items")
        
        return item
    
    def _is_duplicate_item(self, item_name, category_hint, lang_manager, attempt, max_attempts):
        """Check if the generated item is a duplicate."""
        language = lang_manager.current_language if lang_manager else 'en'
        
        if db_handler and db_handler.is_connected():
            if db_handler.check_item_exists(item_name, category_hint, language, time_window_hours=72):
                logger.warning(f"Duplicate item '{item_name}' detected in attempt {attempt + 1}, retrying...")
                if attempt < max_attempts - 1:
                    return True
                else:
                    logger.warning(f"Max attempts reached, accepting potentially duplicate item: {item_name}")
        
        return False
    
    def _track_generated_item(self, item, category_manager):
        """Track the generated item in the category manager."""
        if category_manager:
            category_manager.add_generated_item(item['name'])
    
    def _save_question_to_database(self, item, category_hint, subcategory_hint, difficulty, 
                                 lang_manager, session_id, player_name, generation_time_ms, response):
        """Save the generated question to the database."""
        try:
            language = lang_manager.current_language if lang_manager else 'en'
            
            # Get localized category name for storage
            localized_category = category_hint
            if lang_manager and lang_manager.current_language != 'en':
                # Create a category manager to get localized category name
                category_manager = GameCategoryManager(lang_manager=lang_manager)
                category_obj = category_manager.find_category(category_hint)
                if category_obj:
                    localized_category_obj = category_manager.get_localized_category(category_obj)
                    localized_category = localized_category_obj['name']
            
            question_data = {
                'item_name': item['name'],
                'category': localized_category,  # Store localized category name
                'subcategory': subcategory_hint,  # Already localized
                'difficulty': difficulty['name'] if difficulty else 'normal',
                'facts': item['facts'],
                'language': language,
                'session_id': session_id,
                'player_name': player_name,
                'ai_model': self.deployment_name or 'gpt-4o',
                'generation_time_ms': generation_time_ms,
                'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                'completion_tokens': response.usage.completion_tokens if response.usage else 0
            }
            question_id = db_handler.save_generated_question(question_data)
            item['question_id'] = question_id
            logger.info(f"Generated unique item '{item['name']}' and saved to database with ID: {question_id}")
        except Exception as db_error:
            logger.error(f"Failed to save question to database: {db_error}")
            item['question_id'] = None

    def _get_fallback_item(self, lang_manager=None):
        """Return a simple error item if Azure OpenAI generation fails completely."""
        # Instead of hardcoded fallback items, return a simple error indicator
        # The calling code should handle this gracefully by either:
        # 1. Retrying the AI generation
        # 2. Using a question from the database
        # 3. Showing an appropriate error message to the user
        
        language = lang_manager.current_language if lang_manager else 'en'
        
        if language == 'pl':
            return {
                "name": "Błąd generowania",
                "facts": [
                    "Wystąpił problem z generowaniem pytania.",
                    "Spróbuj ponownie lub wybierz inną kategorię.",
                    "System nie może obecnie wygenerować nowego pytania."
                ],
                "error": True
            }
        else:
            return {
                "name": "Generation Error",
                "facts": [
                    "There was a problem generating a question.",
                    "Please try again or select a different category.",
                    "The system cannot currently generate a new question."
                ],
                "error": True
            }
    
    def _get_database_item(self, category_hint, lang_manager=None, db_handler=None):
        """Retrieve a random question from the database when AI generation fails."""
        if not db_handler:
            return None
            
        try:
            language = lang_manager.current_language if lang_manager else 'en'
            
            # Try to get a random question from the database for this category and language
            with db_handler.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT item_name, facts, category, subcategory
                    FROM generated_questions 
                    WHERE LOWER(category) = LOWER(%s) 
                    AND language = %s 
                    ORDER BY RANDOM() 
                    LIMIT 1
                """, (category_hint, language))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "name": result[0],
                        "facts": result[1] if isinstance(result[1], list) else [str(result[1])],
                        "category": result[2],
                        "subcategory": result[3],
                        "from_database": True
                    }
        except Exception as e:
            logger.error(f"Failed to retrieve question from database: {e}")
            
        return None

class DifficultyLevel:
    """Manages game difficulty settings."""
    
    _levels = None  # Class variable to store loaded levels
    
    @classmethod
    def _load_levels(cls):
        """Load difficulty levels from JSON file."""
        if cls._levels is not None:
            return cls._levels
            
        try:
            with open('difficulty_levels.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                levels_data = data.get('difficulty_levels', {})
        except FileNotFoundError:
            # Fallback levels if file not found
            levels_data = {
                'very_easy': {
                    'name': 'very_easy',
                    'score_multiplier': 0.8,
                    'pl_name': 'bardzo łatwy',
                    'pl_desc': 'Najłatwiejsze zagadki z oczywistymi wskazówkami, zmniejszone punktowanie',
                    'en_desc': 'Easiest puzzles with very obvious clues, reduced scoring',
                    'prompt_hint': 'Make the facts extremely obvious and straightforward, with very clear hints from the beginning. Perfect for children or absolute beginners.'
                },
                'easy': {
                    'name': 'easy',
                    'score_multiplier': 1.0,
                    'pl_name': 'łatwy',
                    'pl_desc': 'Prostsze zagadki, normalne punktowanie',
                    'en_desc': 'Simpler puzzles, normal scoring',
                    'prompt_hint': 'Make the facts very straightforward and obvious, suitable for beginners.'
                },
                'normal': {
                    'name': 'normal',
                    'score_multiplier': 1.2,
                    'pl_name': 'normalny',
                    'pl_desc': 'Standardowy poziom zagadek, zwiększone punktowanie',
                    'en_desc': 'Standard puzzle difficulty, increased scoring',
                    'prompt_hint': 'Balance the facts between obvious and subtle hints, suitable for average players.'
                },
                'hard': {
                    'name': 'hard',
                    'score_multiplier': 1.5,
                    'pl_name': 'trudny',
                    'pl_desc': 'Bardziej wymagające zagadki, znacznie zwiększone punktowanie',
                    'en_desc': 'More challenging puzzles, significantly increased scoring',
                    'prompt_hint': 'Make the facts more subtle and clever, requiring good deduction skills. Avoid very obvious hints until the final fact.'
                },
                'expert': {
                    'name': 'expert',
                    'score_multiplier': 2.0,
                    'pl_name': 'ekspert',
                    'pl_desc': 'Najtrudniejsze zagadki z zawoalowanymi wskazówkami, maksymalne punktowanie',
                    'en_desc': 'Hardest puzzles with cryptic clues, maximum scoring',
                    'prompt_hint': 'Make the facts very cryptic, abstract, and challenging. Use metaphors, indirect references, and require deep thinking. Only the final fact should be somewhat direct.'
                }
            }
        
        cls._levels = levels_data
        
        # Set class variables for backward compatibility
        cls.VERY_EASY = levels_data.get('very_easy')
        cls.EASY = levels_data.get('easy')
        cls.NORMAL = levels_data.get('normal')
        cls.HARD = levels_data.get('hard')
        cls.EXPERT = levels_data.get('expert')
        
        # Ensure NORMAL has a fallback if not found in JSON
        if cls.NORMAL is None:
            cls.NORMAL = {
                'name': 'normal',
                'score_multiplier': 1.2,
                'pl_name': 'normalny',
                'pl_desc': 'Standardowy poziom zagadek, zwiększone punktowanie',
                'en_desc': 'Standard puzzle difficulty, increased scoring',
                'prompt_hint': 'Balance the facts between obvious and subtle hints, suitable for average players.'
            }
        
        return cls._levels
    
    @classmethod
    def get_level(cls, level_name):
        """Get a specific difficulty level by name."""
        levels = cls._load_levels()
        return levels.get(level_name)
    
    @classmethod
    def get_all_levels(cls):
        """Get list of all difficulty levels."""
        levels = cls._load_levels()
        return list(levels.values())

# Initialize the difficulty levels on import
DifficultyLevel._load_levels()

class WebGameSession:
    """Web-specific game session management"""
    
    def __init__(self, player_name: str, language: str = 'en', max_rounds: Optional[int] = None):
        self.player_name = player_name
        self.language = language
        self.max_rounds = max_rounds  # New: Maximum rounds for this session
        self.rounds_completed = 0  # New: Track completed rounds
        self.current_category: Optional[str] = None
        self.current_item: Optional[str] = None
        self.current_facts: List[str] = []
        self.current_question_id: Optional[int] = None  # Track database question ID
        self.facts_shown = 0
        self.guesses: List[str] = []
        self.failed_attempts = 0  # New: Track failed guess attempts
        self.max_failed_attempts = 3  # New: Maximum failed attempts before revealing answer
        self.round_start_time: Optional[datetime] = None
        self.rounds: List[GameRound] = []
        self.session_start_time = datetime.now()
        self.total_score = 0
        self.difficulty = DifficultyLevel.NORMAL
        self.answer_checker = AnswerChecker(similarity_threshold=0.90)
        self.round_history: List = []  # Store completed rounds for database saving
        
        # Hint system
        self.revealed_letters: set = set()  # Track revealed letter positions
        self.hints_used = 0  # Track number of hints used in current round
        self.max_hints = 3  # Maximum hints per round
        
    def start_new_round(self, category: str, item: str, facts: List[str], difficulty=None, question_id: Optional[int] = None):
        """Start a new game round"""
        self.current_category = category
        self.current_item = item
        self.current_facts = facts
        self.current_question_id = question_id
        self.facts_shown = 0
        self.guesses = []
        self.failed_attempts = 0  # Reset failed attempts for new round
        self.round_start_time = datetime.now()
        if difficulty:
            self.difficulty = difficulty
        
        # Reset hint system for new round
        self.revealed_letters.clear()
        self.hints_used = 0
        
    def add_guess(self, guess: str) -> Dict:
        """Add a guess and return result using proper answer checking"""
        if not self.current_item or not self.round_start_time:
            return {"correct": False, "similarity": 0.0, "message": "Invalid game state"}
        
        if not guess or not guess.strip():
            return {"correct": False, "similarity": 0.0, "message": "Please enter a valid guess"}
            
        self.guesses.append(guess)
        
        # Use the proper answer checker with fuzzy matching
        is_correct, similarity, match_type = self.answer_checker.is_correct_answer(guess, self.current_item)
        
        if is_correct:
            return self._end_round(True, similarity, match_type)
        else:
            # Increment failed attempts
            self.failed_attempts += 1
            
            # Check if maximum failed attempts reached
            if self.failed_attempts >= self.max_failed_attempts:
                # Auto-reveal answer after 3 failed attempts
                return self._end_round(False, similarity, match_type, auto_revealed=True)
            
            # Get feedback message
            feedback = self.answer_checker.get_feedback(guess, self.current_item, lang_manager)
            
            # Add attempt count to feedback
            attempts_remaining = self.max_failed_attempts - self.failed_attempts
            if lang_manager and lang_manager.current_language == 'pl':
                attempt_info = f" (Pozostało prób: {attempts_remaining})"
            else:
                attempt_info = f" (Attempts remaining: {attempts_remaining})"
            
            return {
                "correct": False, 
                "similarity": similarity, 
                "message": feedback + attempt_info,
                "failed_attempts": self.failed_attempts,
                "max_failed_attempts": self.max_failed_attempts,
                "attempts_remaining": attempts_remaining
            }
    
    def reveal_next_fact(self) -> Optional[str]:
        """Reveal the next fact"""
        if self.facts_shown < len(self.current_facts):
            fact = self.current_facts[self.facts_shown]
            self.facts_shown += 1
            return fact
        return None
    
    def get_hint(self) -> Dict:
        """Reveal a random letter from the answer and return hint status"""
        if not self.current_item:
            return {"success": False, "message": "No active round"}
        
        # Check if hints are available
        if self.hints_used >= self.max_hints:
            if lang_manager and lang_manager.current_language == 'pl':
                return {"success": False, "message": "Wykorzystano wszystkie podpowiedzi dla tej rundy"}
            else:
                return {"success": False, "message": "All hints used for this round"}
        
        # Get positions of letters (not spaces or punctuation)
        answer = self.current_item.lower()
        letter_positions = []
        for i, char in enumerate(answer):
            if char.isalpha() and i not in self.revealed_letters:
                letter_positions.append(i)
        
        if not letter_positions:
            if lang_manager and lang_manager.current_language == 'pl':
                return {"success": False, "message": "Nie ma więcej liter do ujawnienia"}
            else:
                return {"success": False, "message": "No more letters to reveal"}
        
        # Reveal a random letter
        position = random.choice(letter_positions)
        self.revealed_letters.add(position)
        self.hints_used += 1
        
        # Create hint display
        hint_display = self._create_hint_display()
        
        hints_remaining = self.max_hints - self.hints_used
        if lang_manager and lang_manager.current_language == 'pl':
            message = f"Ujawniono literę! Pozostałe podpowiedzi: {hints_remaining}"
        else:
            message = f"Letter revealed! Hints remaining: {hints_remaining}"
        
        return {
            "success": True,
            "message": message,
            "hint_display": hint_display,
            "hints_used": self.hints_used,
            "hints_remaining": hints_remaining,
            "max_hints": self.max_hints
        }
    
    def _create_hint_display(self) -> str:
        """Create a display string showing revealed letters and blanks"""
        if not self.current_item:
            return ""
        
        display = []
        for i, char in enumerate(self.current_item):
            if char.isalpha():
                if i in self.revealed_letters:
                    display.append(char.upper())
                else:
                    display.append('_')
            else:
                # Keep spaces and punctuation as is
                display.append(char)
        
        return ''.join(display)
    
    def get_current_hint_display(self) -> str:
        """Get the current hint display (for when switching between UI screens)"""
        if not self.revealed_letters:
            return ""
        return self._create_hint_display()
    
    def _end_round(self, correct: bool, similarity: float, match_type: str, auto_revealed: bool = False) -> Dict:
        """End the current round and calculate score"""
        if not self.current_item or not self.current_category or not self.round_start_time:
            return {"correct": False, "message": "Invalid game state"}
            
        time_taken = (datetime.now() - self.round_start_time).total_seconds()
        round_obj = self._create_game_round(correct, similarity, match_type, time_taken)
        
        if correct:
            self._calculate_and_apply_score(round_obj)
        
        self.rounds.append(round_obj)
        self.rounds_completed += 1
        self._save_round_history(round_obj, correct, time_taken)
        
        feedback = self._get_round_feedback(auto_revealed)
        return self._build_round_result(correct, round_obj, time_taken, similarity, feedback, auto_revealed)

    def _create_game_round(self, correct: bool, similarity: float, match_type: str, time_taken: float) -> GameRound:
        """Create a GameRound object for scoring"""
        # Ensure we have valid item and category names (should already be checked in _end_round)
        item_name = self.current_item or "Unknown"
        category = self.current_category or "Unknown"
        
        return GameRound(
            item_name=item_name,
            category=category,
            subcategory=None,
            facts_shown=self.facts_shown,
            total_facts=len(self.current_facts),
            correct=correct,
            guess_attempts=len(self.guesses) - 1 if correct else len(self.guesses),
            similarity_score=similarity,
            match_type=match_type,
            time_taken=time_taken,
            round_score=0,
            hints_used=self.hints_used
        )

    def _calculate_and_apply_score(self, round_obj: GameRound) -> None:
        """Calculate score with difficulty multiplier and hint penalties"""
        difficulty_name = self.difficulty.get('name', 'normal') if self.difficulty else 'normal'
        base_score = scoring_system.calculate_round_score(round_obj, difficulty_name)
        
        if self.difficulty and 'score_multiplier' in self.difficulty:
            round_obj.round_score = int(base_score * self.difficulty['score_multiplier'])
        else:
            round_obj.round_score = base_score
            
        self.total_score += round_obj.round_score

    def _save_round_history(self, round_obj: GameRound, correct: bool, time_taken: float) -> None:
        """Save round data to history"""
        try:
            round_record = {
                'category': self.current_category,
                'item_name': self.current_item,
                'facts_shown': self.facts_shown,
                'is_correct': correct,
                'round_score': round_obj.round_score,
                'time_taken_seconds': time_taken,
                'guesses': self.guesses.copy()
            }
            
            self.round_history.append(type('RoundRecord', (), round_record)())
            logger.info(f"Round completed: {self.current_item} ({'correct' if correct else 'incorrect'})")
            
        except Exception as db_error:
            logger.error(f"Failed to save round data: {db_error}")

    def _get_round_feedback(self, auto_revealed: bool) -> str:
        """Get appropriate feedback message for the round"""
        if auto_revealed:
            if lang_manager and lang_manager.current_language == 'pl':
                return f"💔 Odpowiedź została ujawniona po {self.max_failed_attempts} nieudanych próbach!"
            else:
                return f"💔 Answer revealed after {self.max_failed_attempts} failed attempts!"
        else:
            return self.answer_checker.get_feedback(self.guesses[-1], self.current_item, lang_manager)

    def _build_round_result(self, correct: bool, round_obj: GameRound, time_taken: float, 
                           similarity: float, feedback: str, auto_revealed: bool) -> Dict:
        """Build the final round result dictionary"""
        return {
            "correct": correct,
            "answer": self.current_item,
            "score": round_obj.round_score,
            "total_score": self.total_score,
            "time_taken": time_taken,
            "facts_used": self.facts_shown,
            "similarity": similarity,
            "feedback": feedback,
            "rounds_completed": self.rounds_completed,
            "max_rounds": self.max_rounds,
            "game_complete": self.is_game_complete(),
            "auto_revealed": auto_revealed,
            "failed_attempts": self.failed_attempts,
            "hints_used": self.hints_used,
            "hint_display": self.get_current_hint_display()
        }

    def is_game_complete(self) -> bool:
        """Check if the game session is complete"""
        if self.max_rounds is None:
            return False  # Unlimited rounds mode
        return self.rounds_completed >= self.max_rounds

# Store active sessions and game components
active_sessions: Dict[str, WebGameSession] = {}
game_engine = AzureOpenAIGameEngine()
category_manager = GameCategoryManager(lang_manager=lang_manager)

# Global category manager for tracking across all sessions
global_category_manager = GameCategoryManager(lang_manager=lang_manager)

def save_session_to_db(game_session: WebGameSession) -> bool:
    """Save game session data to database using CloudScoreKeeper"""
    try:
        # Convert WebGameSession to GameSession format expected by score keeper
        from scoring import GameSession
        from datetime import datetime
        
        # Calculate session statistics
        rounds_won = sum(1 for round_obj in game_session.rounds if round_obj.correct)
        rounds_lost = len(game_session.rounds) - rounds_won
        
        # Calculate averages
        if game_session.rounds:
            avg_facts = sum(r.facts_shown for r in game_session.rounds) / len(game_session.rounds)
            avg_time = sum(r.time_taken for r in game_session.rounds) / len(game_session.rounds)
        else:
            avg_facts = 0.0
            avg_time = 0.0
        
        # Create a scoring.GameSession object
        scoring_session = GameSession(
            start_time=game_session.session_start_time,
            end_time=datetime.now(),
            rounds=game_session.rounds,  # GameRound objects from WebGameSession
            total_score=game_session.total_score,
            rounds_won=rounds_won,
            rounds_lost=rounds_lost,
            average_facts_used=avg_facts,
            average_time_per_round=avg_time,
            player_name=game_session.player_name
        )
        
        # Save using the CloudScoreKeeper
        score_keeper.update_high_scores(scoring_session)
        
        logger.info(f"Session saved to database for {game_session.player_name}: {game_session.total_score} points, {len(game_session.rounds)} rounds (won: {rounds_won}, lost: {rounds_lost})")
        return True
        
    except Exception as e:
        logger.error(f"Error in save_session_to_db: {e}")
        return False

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Basic application health check
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "app": "GuessGame",
            "version": "1.0.0",
            "database": "unknown"
        }
        
        # Check database connection
        try:
            if db_handler and db_handler.is_connected():
                status["database"] = "connected"
            else:
                status["database"] = "disconnected"
        except Exception:
            status["database"] = "error"
        
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/')
def index():
    """Main game page"""
    return render_template('index.html')

@app.route('/api/categories')
def get_categories():
    """Get available game categories with optional language translation"""
    try:
        language = request.args.get('lang', 'en')
        
        with open(CATEGORIES_FILE, 'r', encoding=ENCODING_UTF8) as f:
            categories_data = json.load(f)
        
        categories = categories_data['categories']
        
        # Set display names based on language
        for category in categories:
            if language == 'pl':
                # Use Polish translations if available, fallback to English
                category['display_name'] = category.get('name_pl', category['name'])
                category['display_description'] = category.get('description_pl', category['description'])
            else:
                # Use English names
                category['display_name'] = category['name']
                category['display_description'] = category['description']
        
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        return jsonify({"error": "Failed to load categories"}), 500

@app.route('/api/difficulties')
def get_difficulties():
    """Get available difficulty levels with optional language translation"""
    try:
        language = request.args.get('lang', 'en')
        
        difficulties = []
        for level in DifficultyLevel.get_all_levels():
            # Get localized names based on language parameter
            if language == 'pl':
                display_name = level['pl_name']
                description = level['pl_desc']
            else:
                display_name = level['name'].replace('_', ' ').title()
                description = level['en_desc']
            
            difficulties.append({
                'name': level['name'],
                'display_name': display_name,
                'description': description,
                'score_multiplier': level['score_multiplier']
            })
        return jsonify(difficulties)
    except Exception as e:
        logger.error(f"Error loading difficulties: {e}")
        return jsonify({"error": "Failed to load difficulties"}), 500

@app.route('/api/languages')
def get_languages():
    """Get available languages"""
    try:
        languages = [
            {'code': 'en', 'name': 'English', 'flag': '🇺🇸'},
            {'code': 'pl', 'name': 'Polski', 'flag': '🇵🇱'}
        ]
        return jsonify(languages)
    except Exception as e:
        logger.error(f"Error loading languages: {e}")
        return jsonify({"error": "Failed to load languages"}), 500

@app.route('/api/leaderboard')
def get_leaderboard():
    """Get global leaderboard"""
    try:
        leaderboard_text = score_keeper.get_top_scores_display(lang_manager)
        return jsonify({"leaderboard": leaderboard_text})
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        return jsonify({"error": "Failed to load leaderboard"}), 500

@app.route('/api/player/<player_name>/stats')
def get_player_stats(player_name):
    """Get player statistics"""
    try:
        stats_text = score_keeper.get_player_stats(player_name, lang_manager)
        return jsonify({"stats": stats_text})
    except Exception as e:
        logger.error(f"Error getting player stats: {e}")
        return jsonify({"error": "Failed to load player stats"}), 500

@app.route('/api/set_language', methods=['POST'])
def set_language():
    """Set the current language"""
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        
        if language in ['en', 'pl']:
            session['language'] = language
            lang_manager.set_language(language)
            return jsonify({"success": True, "language": language})
        else:
            return jsonify({"error": "Invalid language"}), 400
    except Exception as e:
        logger.error(f"Error setting language: {e}")
        return jsonify({"error": "Failed to set language"}), 500

@app.route('/api/start_game', methods=['POST'])
def handle_start_game():
    """Handle game start"""
    try:
        data = request.get_json()
        print(f"🎮 Received start_game request with data: {data}")
        
        player_name = data.get('player_name', 'Anonymous')
        language = data.get('language', 'en')
        category = data.get('category', '')  # Empty string for random
        difficulty_name = data.get('difficulty', 'normal')
        max_rounds = data.get('max_rounds', None)  # New: rounds limit (None = unlimited)
        
        print(f"Player: {player_name}, Category: {category}, Difficulty: {difficulty_name}, Language: {language}, Max Rounds: {max_rounds}")
        
        # If no category specified, select random category
        if not category:
            with open(CATEGORIES_FILE, 'r', encoding=ENCODING_UTF8) as f:
                categories_data = json.load(f)
            available_categories = [cat['name'] for cat in categories_data['categories']]
            category = random.choice(available_categories)
            logger.info(f"Selected random category: {category}")
            print(f"🎲 Random category selected: {category}")
        
        # Find difficulty level
        difficulty = DifficultyLevel.get_level('normal')  # Use get_level method
        if difficulty is None:
            difficulty = DifficultyLevel.NORMAL  # Fallback to class variable
        for level in DifficultyLevel.get_all_levels():
            if level and level.get('name') == difficulty_name:
                difficulty = level
                break
        
        # Create new session with unique ID
        session_id = str(uuid.uuid4())
        game_session = WebGameSession(player_name, language, max_rounds)  # Pass max_rounds
        active_sessions[session_id] = game_session
        
        # Store session ID in the session
        session['game_session_id'] = session_id
        
        # Create a language manager for this request
        request_lang_manager = LanguageManager()
        request_lang_manager.set_language(language)
        
        # Update category manager with the request language manager
        request_category_manager = GameCategoryManager(lang_manager=request_lang_manager)
        
        # Generate game content using AI with proper subcategory hint
        subcategory_hint = request_category_manager.get_category_hint(category)
        localized_subcategory = request_category_manager.get_localized_hint(subcategory_hint) if subcategory_hint else None
        item_data = game_engine.generate_game_item(
            category, 
            subcategory_hint, 
            request_lang_manager, 
            difficulty, 
            global_category_manager,
            session_id,
            player_name
        )
        
        if item_data:
            game_session.start_new_round(
                category, 
                item_data['name'], 
                item_data['facts'], 
                difficulty,
                item_data.get('question_id')
            )
            
            print("✅ Game started successfully")
            return jsonify({
                'session_id': session_id,
                'category': category,
                'subcategory': localized_subcategory,
                'facts_available': len(item_data['facts']),
                'player_name': player_name,
                'difficulty': difficulty['name'] if difficulty else 'normal',
                'score_multiplier': difficulty['score_multiplier'] if difficulty else 1.0,
                'max_rounds': max_rounds,
                'rounds_completed': 0,
                'hints_available': game_session.max_hints,
                'hints_used': 0,
                'hint_display': ""
            })
        else:
            print("❌ Failed to generate item data")
            return jsonify({'error': 'Failed to generate game content'}), 500
            
    except Exception as e:
        logger.error(f"Error starting game: {e}")
        return jsonify({'error': 'Failed to start game'}), 500

@app.route('/api/request_fact', methods=['POST'])
def handle_request_fact():
    """Handle fact request"""
    try:
        data = request.get_json() or {}
        
        session_id = data.get('session_id') or session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        game_session = active_sessions[session_id]
        fact = game_session.reveal_next_fact()
        
        if fact:
            return jsonify({
                'fact': fact,
                'fact_number': game_session.facts_shown,
                'total_facts': len(game_session.current_facts)
            })
        else:
            return jsonify({'error': 'No more facts available'}), 400
            
    except Exception as e:
        logger.error(f"Error revealing fact: {e}")
        return jsonify({'error': 'Failed to reveal fact'}), 500

@app.route('/api/submit_guess', methods=['POST'])
def handle_submit_guess():
    """Handle guess submission"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        guess = data.get('guess', '').strip()
        if not guess:
            return jsonify({'error': 'Please enter a guess'}), 400
        
        game_session = active_sessions[session_id]
        result = game_session.add_guess(guess)
        
        # Save session if round ended (correct answer OR auto-revealed after max attempts)
        # Check for both winning condition and auto-reveal condition
        if result.get('correct', False) or result.get('auto_revealed', False):
            save_session_to_db(game_session)
        
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"Error processing guess: {e}")
        return jsonify({'error': 'Failed to process guess'}), 500

@app.route('/api/get_hint', methods=['POST'])
def handle_get_hint():
    """Handle hint request"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id') or session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        game_session = active_sessions[session_id]
        hint_result = game_session.get_hint()
        
        # Add scoring information to the hint result
        if hint_result.get('success', False):
            difficulty_name = game_session.difficulty.get('name', 'normal') if game_session.difficulty else 'normal'
            hint_penalty = scoring_system.hint_penalties.get(difficulty_name, scoring_system.hint_penalties['normal'])
            hint_result['hint_penalty'] = hint_penalty
            hint_result['total_hint_penalty'] = hint_penalty * game_session.hints_used
        
        return jsonify(hint_result)
            
    except Exception as e:
        logger.error(f"Error getting hint: {e}")
        return jsonify({'error': 'Failed to get hint'}), 500

@app.route('/api/give_up', methods=['POST'])
def handle_give_up():
    """Give up the current round and reveal the answer"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        game_session = active_sessions[session_id]
        if not game_session.current_item:
            return jsonify({'error': 'No active round to give up'}), 400
        
        # End the round as incorrect (give up)
        result = game_session._end_round(
            correct=False, 
            similarity=0.0, 
            match_type="gave_up",
            auto_revealed=True
        )
        
        # Add a custom message for giving up
        result['gave_up'] = True
        result['message'] = 'You gave up this round'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error giving up: {e}")
        return jsonify({'error': 'Failed to give up'}), 500

@app.route('/api/new_round', methods=['POST'])
def handle_new_round():
    """Start a new round"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        game_session = active_sessions[session_id]
        if game_session.is_game_complete():
            return jsonify({'error': 'Game session is already complete'}), 400
        
        # Extract request parameters
        category = data.get('category', '')
        difficulty_name = data.get('difficulty', 'normal')
        language = data.get('language', 'en')
        
        # Set up category and difficulty
        category = _get_or_select_category(category)
        difficulty = _get_difficulty_level(difficulty_name)
        
        # Generate new round content
        item_data = _generate_round_content(category, difficulty, language, session_id, game_session.player_name)
        
        if item_data:
            return _create_successful_round_response(game_session, category, item_data, difficulty)
        else:
            return jsonify({'error': 'Failed to generate new round'}), 500
            
    except Exception as e:
        logger.error(f"Error starting new round: {e}")
        return jsonify({'error': 'Failed to start new round'}), 500

def _get_or_select_category(category: str) -> str:
    """Get the specified category or select a random one"""
    if not category:
        with open(CATEGORIES_FILE, 'r', encoding=ENCODING_UTF8) as f:
            categories_data = json.load(f)
        available_categories = [cat['name'] for cat in categories_data['categories']]
        category = random.choice(available_categories)
        logger.info(f"Selected random category for new round: {category}")
    return category

def _get_difficulty_level(difficulty_name: str):
    """Get the difficulty level object"""
    difficulty = DifficultyLevel.get_level('normal')
    if difficulty is None:
        difficulty = DifficultyLevel.NORMAL
    
    for level in DifficultyLevel.get_all_levels():
        if level and level.get('name') == difficulty_name:
            difficulty = level
            break
    return difficulty

def _generate_round_content(category: str, difficulty, language: str, session_id: str, player_name: str):
    """Generate new round content using AI"""
    request_lang_manager = LanguageManager()
    request_lang_manager.set_language(language)
    request_category_manager = GameCategoryManager(lang_manager=request_lang_manager)
    
    subcategory_hint = request_category_manager.get_category_hint(category)
    return game_engine.generate_game_item(
        category, 
        subcategory_hint, 
        request_lang_manager, 
        difficulty, 
        global_category_manager,
        session_id,
        player_name
    )

def _create_successful_round_response(game_session, category: str, item_data, difficulty):
    """Create response for successful round generation"""
    # Create language manager for localization
    request_lang_manager = LanguageManager()
    request_lang_manager.set_language(game_session.language)
    request_category_manager = GameCategoryManager(lang_manager=request_lang_manager)
    
    subcategory_hint = request_category_manager.get_category_hint(category)
    localized_subcategory = request_category_manager.get_localized_hint(subcategory_hint) if subcategory_hint else None
    
    game_session.start_new_round(
        category, 
        item_data['name'], 
        item_data['facts'], 
        difficulty,
        item_data.get('question_id')
    )
    
    return jsonify({
        'category': category,
        'subcategory': localized_subcategory,
        'facts_available': len(item_data['facts']),
        'difficulty': difficulty['name'] if difficulty else 'normal',
        'score_multiplier': difficulty['score_multiplier'] if difficulty else 1.0,
        'rounds_completed': game_session.rounds_completed,
        'max_rounds': game_session.max_rounds,
        'game_complete': game_session.is_game_complete(),
        'hints_available': game_session.max_hints,
        'hints_used': 0,
        'hint_display': ""
    })

@app.route('/api/start_offline_game', methods=['POST'])
def handle_start_offline_game():
    """Handle offline game start using database questions"""
    try:
        data = request.get_json()
        print(f"🎮 Received start_offline_game request with data: {data}")
        
        player_name = data.get('player_name', 'Anonymous')
        language = data.get('language', 'en')
        category = data.get('category', '')  # Empty string for random
        difficulty_name = data.get('difficulty', 'normal')
        max_rounds = data.get('max_rounds', None)
        
        print(f"OFFLINE Player: {player_name}, Category: {category}, Difficulty: {difficulty_name}, Language: {language}, Max Rounds: {max_rounds}")
        
        # Check if we have any offline questions available
        total_questions = db_handler.get_offline_question_count(
            category=category if category else None,
            difficulty=difficulty_name,
            language=language,
            exclude_used=True
        )
        
        if total_questions == 0:
            return jsonify({
                'error': 'No offline questions available',
                'message': 'No questions found in database for the selected criteria. Please try online mode or different settings.',
                'available_questions': 0
            }), 404
        
        # Get a random question from database
        question_data = db_handler.get_random_offline_question(
            category=category if category else None,
            difficulty=difficulty_name,
            language=language,
            exclude_used=True
        )
        
        if not question_data:
            return jsonify({
                'error': 'No offline question found',
                'message': 'Unable to retrieve question from database.',
                'available_questions': total_questions
            }), 500
        
        # Mark question as used
        db_handler.mark_question_as_used(question_data['id'])
        
        # Find difficulty level
        difficulty = DifficultyLevel.get_level('normal')  # Use get_level method
        if difficulty is None:
            difficulty = DifficultyLevel.NORMAL  # Fallback to class variable
        for level in DifficultyLevel.get_all_levels():
            if level and level.get('name') == difficulty_name:
                difficulty = level
                break
        
        # Create new session with unique ID
        session_id = str(uuid.uuid4())
        game_session = WebGameSession(player_name, language, max_rounds)
        active_sessions[session_id] = game_session
        
        # Store session ID in the session
        session['game_session_id'] = session_id
        
        # Use the question data from database
        item_name = question_data['item_name']
        category_used = question_data['category']
        subcategory = question_data.get('subcategory', '')
        facts = question_data['facts'] if isinstance(question_data['facts'], list) else []
        
        # Start the round with database question
        game_session.start_new_round(
            category_used, 
            item_name, 
            facts, 
            difficulty,
            question_data['id']  # Use database ID as question_id
        )
        
        print(f"✅ Offline game started successfully with question: {item_name}")
        return jsonify({
            'session_id': session_id,
            'category': category_used,
            'subcategory': subcategory,
            'item_name': item_name,
            'facts_available': len(facts),
            'difficulty': difficulty_name,
            'mode': 'offline',
            'total_offline_questions': total_questions,
            'question_id': question_data['id']
        })
        
    except Exception as e:
        logger.error(f"Error starting offline game: {e}")
        return jsonify({
            'error': 'Failed to start offline game',
            'message': str(e)
        }), 500

@app.route('/api/offline_status', methods=['GET'])
def get_offline_status():
    """Get offline mode status and available question counts with category/difficulty filtering"""
    try:
        language = request.args.get('lang', request.args.get('language', 'en'))
        category = request.args.get('category', '')  # Empty string means "Random"
        difficulty = request.args.get('difficulty', 'normal')
        
        # Convert empty category to None for database query
        category_filter = category if category else None
        
        # Check total questions available (including used ones) with filters
        total_questions = db_handler.get_offline_question_count(
            category=category_filter,
            difficulty=difficulty,
            language=language,
            exclude_used=False  # Include all questions
        )
        
        # Check unused questions with filters
        unused_questions = db_handler.get_offline_question_count(
            category=category_filter,
            difficulty=difficulty,
            language=language,
            exclude_used=True
        )
        
        # Offline is available if we have unused questions for this specific combination
        offline_available = unused_questions > 0
        
        return jsonify({
            'offline_available': offline_available,
            'total_questions': total_questions,
            'unused_questions': unused_questions,
            'used_questions': total_questions - unused_questions,
            'categories': {},  # Skip category details for speed
            'language': language,
            'category': category,
            'difficulty': difficulty
        })
        
    except Exception as e:
        logger.error(f"Error getting offline status: {e}")
        return jsonify({
            'error': 'Failed to get offline status',
            'offline_available': False,
            'total_questions': 0,
            'unused_questions': 0
        }), 500

@app.route('/api/offline-new-round', methods=['POST'])
def handle_offline_new_round():
    """Handle starting a new round in offline mode"""
    try:
        session_id = session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        game_session = active_sessions[session_id]
        data = request.get_json()
        language = data.get('language', 'en')
        category = data.get('category', '')
        difficulty_name = data.get('difficulty', 'normal')
        
        # Check if we have any offline questions available (include used questions)
        total_questions = db_handler.get_offline_question_count(
            category=category if category else None,
            difficulty=difficulty_name,
            language=language,
            exclude_used=False  # Allow both used and unused questions
        )
        
        if total_questions == 0:
            return jsonify({
                'error': 'No offline questions available',
                'message': 'No questions found in database for the selected criteria.',
                'available_questions': 0
            }), 404
        
        # Get a random question from database (include used questions)
        question_data = db_handler.get_random_offline_question(
            category=category if category else None,
            difficulty=difficulty_name,
            language=language,
            exclude_used=False  # Allow both used and unused questions
        )
        
        if not question_data:
            return jsonify({
                'error': 'No offline question found',
                'message': 'Unable to retrieve new question from database.',
                'available_questions': total_questions
            }), 500
        
        # Don't automatically mark question as used in offline mode
        # This allows players to replay questions multiple times
        # db_handler.mark_question_as_used(question_data['id'])
        
        # Find difficulty level
        difficulty = DifficultyLevel.NORMAL  # default
        for level in DifficultyLevel.get_all_levels():
            if level['name'] == difficulty_name:
                difficulty = level
                break
        
        # Use the question data from database
        item_name = question_data['item_name']
        category_used = question_data['category']
        subcategory = question_data.get('subcategory', '')
        facts = question_data['facts'] if isinstance(question_data['facts'], list) else []
        
        # Start the new round with database question
        game_session.start_new_round(
            category_used, 
            item_name, 
            facts, 
            difficulty,
            question_data['id']  # Use database ID as question_id
        )
        
        return jsonify({
            'session_id': session_id,
            'category': category_used,
            'subcategory': subcategory,
            'item_name': item_name,
            'facts_available': len(facts),
            'difficulty': difficulty_name,
            'mode': 'offline',
            'total_offline_questions': total_questions,
            'question_id': question_data['id'],
            'game_complete': game_session.is_game_complete()
        })
        
    except Exception as e:
        logger.error(f"Error starting offline new round: {e}")
        return jsonify({
            'error': 'Failed to start offline new round',
            'message': str(e)
        }), 500

@app.route('/api/analytics/questions')
def get_question_analytics():
    """Get analytics on generated questions"""
    try:
        # Simplified analytics - just return basic info
        return jsonify({
            'questions': [],
            'total_count': 0,
            'message': 'Analytics feature not fully implemented yet'
        })
    except Exception as e:
        logger.error(f"Error getting question analytics: {e}")
        return jsonify({'error': 'Failed to retrieve question analytics'}), 500

@app.route('/api/analytics/categories')
def get_category_analytics():
    """Get analytics by category and subcategory"""
    try:
        # Simplified analytics - just return basic info
        return jsonify({
            'categories': [],
            'total_categories': 0,
            'message': 'Analytics feature not fully implemented yet'
        })
    except Exception as e:
        logger.error(f"Error getting category analytics: {e}")
        return jsonify({'error': 'Failed to retrieve category analytics'}), 500

@app.route('/api/analytics/database_status')
def get_database_status():
    """Get database connection status and basic stats"""
    try:
        status = {
            'connected': db_handler.is_connected(),
            'message': 'Database connected successfully' if db_handler.is_connected() else 'Database not connected'
        }
        
        if db_handler.is_connected():
            # Get basic stats using existing methods
            offline_count = db_handler.get_offline_question_count()
            status['stats'] = {
                'questions_in_db': offline_count > 0,
                'offline_questions_available': offline_count
            }
        
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        return jsonify({
            'connected': False,
            'message': f'Database error: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/end_session', methods=['POST'])
def handle_end_session():
    """End a game session and save it to the database"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') or session.get('game_session_id')
        if not session_id or session_id not in active_sessions:
            return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
        
        game_session = active_sessions[session_id]
        
        # Save the session to database if there are any completed rounds
        if game_session.rounds:
            success = save_session_to_db(game_session)
            if success:
                logger.info(f"Session ended and saved for {game_session.player_name}")
            else:
                logger.warning(f"Failed to save session for {game_session.player_name}")
        
        # Remove the session from active sessions
        del active_sessions[session_id]
        
        # Clear session data
        if 'game_session_id' in session:
            session.pop('game_session_id', None)
        
        return jsonify({
            'message': 'Session ended successfully',
            'total_score': game_session.total_score,
            'rounds_completed': len(game_session.rounds),
            'session_saved': bool(game_session.rounds)
        })
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({'error': 'Failed to end session'}), 500

if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Get port from environment variable (for Azure App Service) or use default
    port = int(os.environ.get('PORT', 5001))
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port)
