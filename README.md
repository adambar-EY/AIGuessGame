# Fact Quest - Technical Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Backend Components](#backend-components)
4. [Frontend Components](#frontend-components)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Data Flow](#data-flow)
9. [Class Reference](#class-reference)

## Project Overview

The Fact Quest is a Flask-based web application that creates an interactive multilingual guessing game where players guess items based on progressive AI-generated facts. The game features graceful degradation with dual-mode operation (online AI generation vs offline database questions).

### Key Features

- **AI Integration**: Azure OpenAI GPT-4 for dynamic content generation
- **Multilingual Support**: English and Polish with localized UI and AI prompts
- **Dual Game Modes**: Online (AI generation) and Offline (database questions)
- **Persistent Storage**: PostgreSQL/Supabase with local JSON fallback
- **Responsive Design**: Mobile-first responsive UI with touch gestures
- **Progressive Hints**: Gradual fact revelation and letter hints
- **Fuzzy Matching**: Jaro-Winkler similarity-based answer checking

## Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask Backend  │    │   Azure OpenAI  │
│   (JavaScript)  │◄──►│   (Python)       │◄──►│   (GPT-4)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │   PostgreSQL    │
                       │   (Supabase)    │
                       └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │   Local JSON    │
                       │   (Fallback)    │
                       └─────────────────┘
```

### Core Design Patterns

- **Triple Fallback Strategy**: AI Generation → Database Retrieval → Static Fallback
- **Session Management**: UUID-based session tracking with in-memory storage
- **Graceful Degradation**: Automatic fallback between modes and storage systems
- **Mobile-First**: Progressive enhancement for desktop features

## Backend Components

### 1. Flask Application (`app.py`)

#### Main Classes

##### `GameCategoryManager`

**Purpose**: Manages game categories and provides intelligent category-based hints.

**Properties**:

- `categories: List[Dict]` - Loaded categories from JSON
- `lang_manager: LanguageManager` - Language management instance
- `generated_items: set` - Tracks generated items to avoid duplicates
- `category_usage_count: Dict` - Tracks category/subcategory usage
- `polish_translations: Dict` - Polish translations for categories

**Methods**:

- `__init__(categories_file, lang_manager)` - Initialize with categories file and language manager
- `load_categories(filename)` - Load categories from JSON file
  - **Input**: `filename: str` - Path to categories JSON file
  - **Output**: None (raises exceptions on critical errors)
  - **Purpose**: Load and validate categories data
- `find_category(name)` - Find category by name
  - **Input**: `name: str` - Category name to search
  - **Output**: `Dict | None` - Category object or None
- `get_category_hint(category_name)` - Get smart subcategory hint avoiding recent usage
  - **Input**: `category_name: str` - Name of category
  - **Output**: `str | None` - Localized subcategory hint
  - **Logic**: Prefers unused examples, falls back to least used
- `get_localized_category(category)` - Get category with localized names
  - **Input**: `category: Dict` - Category object
  - **Output**: `Dict` - Localized category object

##### `GameEngine`

**Purpose**: Core game logic engine handling AI integration and item generation.

**Properties**:

- `client: AzureOpenAI` - Azure OpenAI client
- `endpoint: str` - OpenAI endpoint URL
- `deployment_name: str` - Model deployment name
- `api_key: Optional[str]` - API key for authentication
- `timeout: int` - Request timeout in seconds
- `max_retries: int` - Maximum retry attempts

**Methods**:

- `__init__()` - Initialize with Azure OpenAI configuration
  - **Authentication**: Uses DefaultAzureCredential for managed identity or API key
- `generate_game_item(category, subcategory_hint, lang_manager, difficulty)` - Generate game item with facts
  - **Input**:
    - `category: str` - Game category
    - `subcategory_hint: str` - Specific subcategory guidance
    - `lang_manager: LanguageManager` - Language context
    - `difficulty: Dict` - Difficulty configuration
  - **Output**: `Dict` - Generated item with name and facts
  - **Fallback Logic**: AI → Database → Static error item
- `_call_openai_api(prompt)` - Make API call to OpenAI
  - **Input**: `prompt: str` - Formatted prompt for AI
  - **Output**: `Dict` - Parsed AI response
  - **Error Handling**: Comprehensive retry logic with exponential backoff
- `_get_database_item(category)` - Fallback to database items
- `_get_fallback_item()` - Last resort static item

##### `AnswerChecker`

**Purpose**: Handles answer validation with fuzzy matching and feedback generation.

**Properties**:

- `similarity_threshold: float` - Minimum similarity for correct answer (default: 0.90)

**Methods**:

- `is_correct_answer(guess, answer)` - Check if guess matches answer
  - **Input**:
    - `guess: str` - Player's guess
    - `answer: str` - Correct answer
  - **Output**: `Tuple[bool, float, str]` - (is_correct, similarity, match_type)
  - **Algorithm**: Jaro-Winkler similarity with 90% threshold
- `get_feedback(guess, answer, lang_manager)` - Generate feedback message
  - **Input**:
    - `guess: str` - Player's guess
    - `answer: str` - Correct answer
    - `lang_manager: LanguageManager` - For localization
  - **Output**: `str` - Localized feedback message
  - **Categories**: Perfect (100%), Very Close (80-89%), Getting Warmer (60-79%), Not Quite (<60%)

##### `WebGameSession`

**Purpose**: Web-specific session management with round tracking and scoring.

**Properties**:

- `session_id: str` - Unique session identifier
- `player_name: str` - Player's name
- `language: str` - Session language ('en' or 'pl')
- `max_rounds: Optional[int]` - Maximum rounds (None for unlimited)
- `rounds_completed: int` - Number of completed rounds
- `current_item: Optional[str]` - Current answer
- `current_facts: List[str]` - Available facts for current item
- `facts_shown: int` - Number of facts revealed
- `guesses: List[str]` - All guesses for current round
- `failed_attempts: int` - Failed guess count
- `max_failed_attempts: int` - Maximum allowed failures (3)
- `round_start_time: Optional[datetime]` - Round timing
- `total_score: int` - Cumulative score
- `difficulty: Dict` - Current difficulty settings
- `answer_checker: AnswerChecker` - Answer validation instance
- `revealed_letters: set` - Positions of revealed hint letters
- `hints_used: int` - Number of letter hints used
- `max_hints: int` - Maximum hints per round (3)

**Methods**:

- `__init__(player_name, language, max_rounds)` - Initialize session
- `start_new_round(category, item, facts, difficulty)` - Begin new round
  - **Input**:
    - `category: str` - Round category
    - `item: str` - Answer item
    - `facts: List[str]` - Available facts
    - `difficulty: Dict` - Difficulty configuration
  - **Output**: `Dict` - Round start response
- `get_next_fact()` - Reveal next fact
  - **Output**: `Dict` - Fact data or "no more facts" response
  - **Limit**: Maximum 5 facts per round
- `add_guess(guess)` - Process player guess
  - **Input**: `guess: str` - Player's guess
  - **Output**: `Dict` - Guess result with scoring
  - **Logic**: Fuzzy matching → auto-reveal after 3 failures
- `get_hint()` - Reveal random letter hint
  - **Output**: `Dict` - Hint result with letter display
  - **Logic**: Randomly reveals unrevealed letters, max 3 per round
- `is_complete()` - Check if session is finished
  - **Output**: `bool` - True if max rounds reached

### 2. Scoring System (`scoring.py`)

#### Data Classes

##### `GameRound`

**Purpose**: Represents a single game round result.

**Properties**:

- `item_name: str` - The item that was being guessed
- `category: str` - Category of the item
- `subcategory: Optional[str]` - Subcategory hint used
- `facts_shown: int` - Number of facts revealed
- `total_facts: int` - Total facts available (usually 5)
- `correct: bool` - Whether round was won
- `guess_attempts: int` - Number of wrong guesses
- `similarity_score: float` - Final similarity score (0.0-1.0)
- `match_type: str` - "exact", "similar", "different"
- `time_taken: float` - Time in seconds
- `round_score: int` - Points scored
- `hints_used: int` - Number of letter hints used

##### `GameSession`

**Purpose**: Represents a complete game session.

**Properties**:

- `start_time: datetime` - Session start timestamp
- `end_time: Optional[datetime]` - Session end timestamp
- `rounds: List[GameRound]` - All rounds in session
- `total_score: int` - Cumulative session score
- `rounds_won: int` - Number of successful rounds
- `rounds_lost: int` - Number of failed rounds
- `average_facts_used: float` - Average facts per round
- `average_time_per_round: float` - Average time per round
- `player_name: str` - Player identifier

#### Classes

##### `ScoringSystem`

**Purpose**: Handles all scoring calculations and statistics.

**Properties**:

- `base_points: int` - Starting points per round (1000)
- `fact_penalty: int` - Points lost per fact (150)
- `guess_penalty: int` - Points lost per wrong guess (50)
- `similarity_bonus: int` - Bonus for exact matches (100)
- `time_bonus_threshold: int` - Seconds for time bonus (30)
- `time_bonus_points: int` - Time bonus amount (200)
- `streak_multiplier: float` - Consecutive win multiplier (1.1)

**Methods**:

- `calculate_round_score(round_obj, difficulty_name)` - Calculate points for round
  - **Formula**: `max(0, base_points - (facts_shown × fact_penalty) - (wrong_guesses × guess_penalty) + bonuses)`
  - **Bonuses**: Time bonus (<30s), exact match bonus, difficulty multiplier
- `calculate_session_stats(rounds)` - Generate session statistics
- `get_grade(score, rounds_count)` - Assign letter grade based on performance

### 3. Language Management (`language_manager.py`)

##### `LanguageManager`

**Purpose**: Manages multilingual support with translations and localized AI prompts.

**Properties**:

- `languages: Dict` - All language definitions
- `current_language: str` - Active language code
- `translations: Dict` - Current language translations

**Methods**:

- `__init__(languages_file)` - Load languages from JSON
- `set_language(language_code)` - Switch active language
  - **Input**: `language_code: str` - Language to activate
  - **Effect**: Updates current_language and translations
- `translate(key, **kwargs)` - Get translated text with formatting
  - **Input**:
    - `key: str` - Translation key
    - `**kwargs` - Format parameters
  - **Output**: `str` - Formatted translated text
- `translate_category_example(example)` - Translate category examples
- `get_ai_prompt_template(prompt_type)` - Get localized AI prompts
  - **Types**: 'generation', 'fallback'
  - **Purpose**: Provides culturally adapted prompts for AI

### 4. Database Layer (`postgresql_db.py`)

##### `PostgreSQLHandler`

**Purpose**: Direct PostgreSQL connection to Supabase with comprehensive database operations.

**Connection Strategy**:

- Primary: `DATABASE_URL` environment variable
- Fallback: Supabase-specific URL construction
- Connection pooling with automatic reconnection

**Methods**:

- `__init__()` - Initialize connection with fallback strategy
- `is_connected()` - Check connection status
  - **Output**: `bool` - Connection availability
- `save_session(session)` - Store complete game session
  - **Input**: `GameSession` - Session to save
  - **Output**: `bool` - Success status
  - **Tables**: Updates `game_sessions`, `generated_questions`
- `get_top_sessions(limit)` - Retrieve leaderboard data
  - **Input**: `limit: int` - Number of sessions to return
  - **Output**: `List[Dict]` - Top sessions with player stats
- `get_player_stats(player_name)` - Get individual player statistics
  - **Input**: `player_name: str` - Player to analyze
  - **Output**: `Dict` - Comprehensive player stats
- `save_generated_question(item_data, metadata)` - Store AI-generated content
  - **Input**:
    - `item_data: Dict` - Generated item and facts
    - `metadata: Dict` - Generation metadata (tokens, timing)
  - **Purpose**: Build offline question database
- `get_offline_questions(category, difficulty, language, limit)` - Retrieve questions for offline mode
  - **Input**:
    - `category: str` - Question category filter
    - `difficulty: str` - Difficulty level filter
    - `language: str` - Language filter
    - `limit: int` - Maximum questions to return
  - **Output**: `List[Dict]` - Available questions
- `mark_question_as_used(question_id, player_name)` - Track question usage
  - **Purpose**: Prevent question repetition for players
- `get_offline_status(player_name, category, difficulty, language)` - Check offline availability
  - **Output**: `Dict` - Availability statistics and question counts

**Database Schema Tables**:

- `game_sessions` - Complete session records
- `generated_questions` - AI-generated content cache
- `question_usage` - Tracks which players used which questions
- `player_stats` - Aggregated player statistics

### 5. Cloud Integration (`cloud_scoring.py`)

##### `CloudScoreKeeper`

**Purpose**: Abstraction layer providing automatic fallback from PostgreSQL to local JSON storage.

**Properties**:

- `postgres_handler: PostgreSQLHandler` - Database connection
- `local_keeper: LocalScoreKeeper` - JSON fallback
- `use_cloud: bool` - Database availability flag
- `scoring_system: ScoringSystem` - Shared scoring logic

**Methods**:

- `__init__()` - Initialize with automatic fallback detection
- `update_high_scores(session)` - Save session with fallback
  - **Logic**: Try PostgreSQL → fallback to JSON on failure
- `get_top_scores_display(lang_manager)` - Get formatted leaderboard
  - **Output**: `str` - Formatted leaderboard text
  - **Source**: PostgreSQL or JSON based on availability
- `get_player_stats_display(player_name, lang_manager)` - Get player statistics
  - **Output**: `str` - Formatted player stats
- `save_ai_generated_content(content, metadata)` - Store for offline use

## Frontend Components

### JavaScript Application (`static/js/app.js`)

#### Main Class: `GameApp`

##### Constructor Properties

```javascript
constructor() {
    // Core game state
    this.currentPlayer = '';           // Player name
    this.currentCategory = '';         // Selected category  
    this.currentDifficulty = 'normal'; // Difficulty level
    this.currentLanguage = 'en';       // UI language
    this.gameActive = false;           // Game session active
    this.gameStarting = false;         // Prevents duplicate starts
    
    // Game data
    this.categories = [];              // Available categories
    this.difficulties = [];            // Available difficulties
    this.gameSession = null;           // Backend session ID
    this.currentFacts = [];            // Facts for current round
    this.factsRevealed = 0;           // Number of facts shown
    
    // Round tracking
    this.maxRounds = null;            // Session round limit
    this.roundsCompleted = 0;         // Completed rounds count
    this.gameComplete = false;        // Session finished flag
    
    // Mobile features
    this.currentFactIndex = 0;        // Carousel position
    this.carouselFacts = [];          // Facts for carousel
    
    // Offline mode
    this.offlineMode = false;         // Offline game active
    this.offlineAvailable = false;    // Offline questions available
    this.offlineStats = null;         // Offline statistics
    this.offlineStatusCache = null;   // Cached status (30s TTL)
    
    this.initialized = false;         // Initialization complete
}
```

##### Core Methods

###### Game Lifecycle

- `initSync()` - Synchronous initialization
  - **Purpose**: Set up event listeners and language
- `initAsync()` - Asynchronous initialization  
  - **Purpose**: Load categories, difficulties, check offline status
  - **Performance**: Non-blocking background loading
- `validateStartButton()` - Enable/disable start button
  - **Logic**: Requires player name after initialization
- `startGame()` - Begin online game session
  - **HTTP**: `POST /api/start_game`
  - **Response**: Session ID and initial round data
- `startOfflineGame()` - Begin offline game session  
  - **HTTP**: `POST /api/start_offline_game`
  - **Validation**: Checks offline availability first
- `handleGameStarted(data)` - Process game start response
  - **UI Updates**: Switch to game screen, display category
  - **State**: Set session variables, auto-request first fact

###### Round Management

- `startNewRound()` - Begin next round in session
  - **HTTP**: `POST /api/new_round` or `/api/offline-new-round`
  - **Logic**: Uses current session, maintains game state
- `handleNewRoundStarted(data)` - Process new round response
  - **UI**: Reset game state, update progress, auto-request fact
- `resetGameState()` - Reset UI for new round
  - **Elements**: Clear facts, guesses, hints, re-enable buttons

###### Fact and Hint System

- `requestFact()` - Get next fact for current round
  - **HTTP**: `POST /api/request_fact`
  - **Limit**: Maximum 5 facts per round
  - **UI**: Add to fact list and mobile carousel
- `handleFactRevealed(data)` - Process fact response
  - **Updates**: Fact display, button states, carousel
  - **Logic**: Disable hint button after 5 facts
- `getLetterHint()` - Request letter hint
  - **HTTP**: `POST /api/get_hint`  
  - **Limit**: Maximum 3 letters per round
  - **UI**: Show hint display with revealed letters
- `handleLetterHintResponse(data)` - Process hint response
  - **Updates**: Letter display, hint counters, scoring info

###### Guess Processing

- `submitGuess()` - Submit player's guess
  - **HTTP**: `POST /api/submit_guess`
  - **UI**: Add to guess history with pending status
  - **Response**: Update with result and similarity
- `addGuessToHistory(guess, status, similarity)` - Add guess to UI
  - **Status**: 'pending', 'correct', 'incorrect'
  - **Similarity**: Shown for incorrect guesses (0-100%)
- `handleGuessResult(data)` - Process guess response
  - **Logic**: Update last guess, trigger outcome handling
- `processGuessOutcome(data)` - Handle guess outcomes
  - **Correct**: Show result modal, update scores
  - **Auto-revealed**: Show revealed answer modal
  - **Incorrect**: Display similarity feedback inline

###### UI and Mobile Features  

- `setupEventListeners()` - Initialize all event handlers
  - **Elements**: All buttons, inputs, mobile navigation
- `setupTouchGestures()` - Mobile swipe support
  - **Gestures**: Left/right swipe for fact navigation
- `initializeCarousel()` - Mobile fact carousel
  - **Purpose**: Touch-friendly fact browsing
- `goToFact(index)` - Navigate carousel to specific fact
  - **Bounds**: Validates index within available facts
- `toggleMobileNav()` - Show/hide mobile menu
- `showSwipeIndicatorOnMobile()` - First-time user guidance

###### Offline Mode

- `checkOfflineStatus()` - Check offline availability
  - **HTTP**: `GET /api/offline_status` with category/difficulty
  - **Caching**: 30-second cache per language/category/difficulty
  - **Timeout**: 3-second timeout for quick check
- `updateOfflineUI(isChecking)` - Update offline UI elements
  - **Button**: Enable/disable based on availability
  - **Status**: Show question counts and availability
- `clearOfflineStatusCache()` - Force fresh status check
  - **Trigger**: When category or difficulty changes

###### Session Management

- `playAgain()` - Start new session with same settings
  - **Reset**: Clear session ID, start fresh game
- `startNewGame()` - Complete new game (same as playAgain)
- `changePlayer()` - Return to welcome screen
  - **Reset**: Clear all state, return to player selection
- `backToMenu()` - Return to main menu
  - **Confirmation**: Prompt if game active
- `giveUp()` - Surrender current round
  - **HTTP**: `POST /api/give_up`
  - **Confirmation**: Require user confirmation

###### Localization

- `t(key)` - Get translated text
  - **Fallback**: English if key not found in current language
- `setLanguage(languageCode)` - Change UI language
  - **Update**: All UI elements with `data-translate` attributes
- `updateTranslations()` - Apply current language to UI

###### HTTP Communication

- `httpRequest(url, method, data, params, timeout)` - Core HTTP method
  - **Timeout**: Configurable (default 30s, 3s for offline status)
  - **Error Handling**: Structured error parsing
  - **Headers**: JSON content type, CSRF if needed

### UI Structure (`templates/index.html`)

#### Screen Layout

```html
<!-- Welcome Screen -->
<div id="welcomeScreen" class="screen active">
    <!-- Player setup form -->
    <!-- Category/difficulty selection -->  
    <!-- Online/offline game buttons -->
    <!-- Offline status display -->
</div>

<!-- Game Screen -->  
<div id="gameScreen" class="screen">
    <!-- Header with player info and navigation -->
    <!-- Game info (category, progress, scores) -->
    <!-- Fact display (desktop list + mobile carousel) -->
    <!-- Letter hint display -->
    <!-- Guess input and history -->
    <!-- Action buttons (hint, guess, give up) -->
</div>
```

#### Mobile-First Features

- **Responsive Grid**: CSS Grid with mobile breakpoints
- **Touch Gestures**: Swipe navigation for facts
- **Hamburger Menu**: Collapsible navigation on mobile
- **Carousel**: Touch-friendly fact browsing
- **Large Touch Targets**: 44px minimum button sizes

## API Endpoints

### Game Management

#### `POST /api/start_game`

**Purpose**: Start new online game session with AI generation.

**Request Body**:

```json
{
    "player_name": "string",
    "category": "string",      // Optional, random if empty
    "difficulty": "string",    // easy/normal/hard/expert  
    "language": "string",      // en/pl
    "max_rounds": "int|null"   // null for unlimited
}
```

**Response**:

```json
{
    "session_id": "uuid",
    "player_name": "string",
    "category": "string",
    "subcategory": "string",
    "facts_available": "int",
    "difficulty": "object",
    "max_rounds": "int|null",
    "rounds_completed": "int",
    "hints_available": "int",
    "hints_used": "int"
}
```

#### `POST /api/start_offline_game`  

**Purpose**: Start new offline game session using database questions.

**Request/Response**: Same as start_game, but uses pre-generated questions.

#### `POST /api/new_round`

**Purpose**: Start new round in existing session.

**Request Body**:

```json
{
    "session_id": "uuid",
    "category": "string",      // Optional override
    "difficulty": "string",    // Optional override  
    "language": "string"
}
```

**Response**: Same as start_game for new round.

### Gameplay

#### `POST /api/request_fact`

**Purpose**: Get next fact for current round.

**Request Body**:

```json
{
    "session_id": "uuid",
    "language": "string"
}
```

**Response**:

```json
{
    "fact": "string",
    "fact_number": "int",        // 1-5
    "facts_remaining": "int",
    "no_more_facts": "boolean"   // true if at limit
}
```

#### `POST /api/submit_guess`

**Purpose**: Submit guess for current round.

**Request Body**:

```json
{
    "session_id": "uuid", 
    "guess": "string"
}
```

**Response**:

```json
{
    "correct": "boolean",
    "similarity": "float",        // 0.0-1.0
    "message": "string",          // Feedback message
    "score": "int",              // Points earned (if correct)
    "total_score": "int",        // Session total
    "time_taken": "float",       // Round duration
    "facts_used": "int",         // Facts shown
    "auto_revealed": "boolean",   // Answer revealed after failures
    "rounds_completed": "int",
    "game_complete": "boolean",   // Session finished
    "answer": "string"           // Revealed if correct/auto-revealed
}
```

#### `POST /api/get_hint`

**Purpose**: Get letter hint for current round.

**Request Body**:

```json
{
    "session_id": "uuid",
    "language": "string"
}
```

**Response**:

```json
{
    "success": "boolean",
    "message": "string",
    "hint_display": "string",     // "W_R_D" format
    "hints_used": "int",         // Current usage
    "max_hints": "int",          // Maximum per round
    "hints_remaining": "int",
    "hint_penalty": "int",       // Points deducted
    "total_hint_penalty": "int"  // Total deducted this round
}
```

#### `POST /api/give_up`

**Purpose**: Surrender current round.

**Request/Response**: Same as submit_guess with auto_revealed=true.

### Information

#### `GET /api/categories`

**Purpose**: Get available game categories.

**Response**:

```json
{
    "categories": [
        {
            "name": "string",
            "description": "string", 
            "name_pl": "string",
            "description_pl": "string",
            "examples": ["string"]
        }
    ]
}
```

#### `GET /api/difficulties`

**Purpose**: Get available difficulty levels.

**Response**:

```json
{
    "difficulties": [
        {
            "name": "string",
            "description": "string",
            "score_multiplier": "float",
            "ai_complexity": "string"
        }
    ]
}
```

#### `GET /api/offline_status`

**Purpose**: Check offline mode availability.

**Query Parameters**:

- `lang`: Language code (en/pl)
- `category`: Category filter (optional)
- `difficulty`: Difficulty filter (optional)

**Response**:

```json
{
    "offline_available": "boolean",
    "total_questions": "int",
    "unused_questions": "int",
    "used_questions": "int", 
    "categories": ["string"],
    "reason": "string"          // If unavailable
}
```

### Statistics

#### `GET /api/leaderboard`

**Purpose**: Get top scores leaderboard.

**Query Parameters**:

- `lang`: Language for formatting

**Response**:

```json
{
    "leaderboard": "string"     // Formatted text display
}
```

#### `POST /api/player_stats`

**Purpose**: Get individual player statistics.

**Request Body**:

```json
{
    "player_name": "string",
    "language": "string"
}
```

**Response**:

```json
{
    "stats": "string"          // Formatted text display
}
```

## Configuration

### Environment Variables

#### Required for Online Mode

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_KEY=your-key-here              # Optional in production

# Flask Configuration  
FLASK_SECRET_KEY=your-secret-key                 # Auto-generated if not set
```

#### Optional for Cloud Features

```bash
# PostgreSQL/Supabase Database
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PASSWORD=your-password
```

### Configuration Files

#### `categories.json`

Defines available game categories with examples and translations.

```json
{
    "categories": [
        {
            "name": "category_name",
            "description": "English description",
            "name_pl": "Polish name", 
            "description_pl": "Polish description",
            "examples": ["subcategory1", "subcategory2"]
        }
    ]
}
```

#### `difficulty_levels.json`

Defines difficulty configurations affecting AI prompts and scoring.

```json
{
    "difficulties": [
        {
            "name": "normal",
            "description": "Standard difficulty",
            "score_multiplier": 1.0,
            "ai_complexity": "moderate_challenge"
        }
    ]
}
```

#### `languages.json`

Complete translation system with UI strings and category examples.

```json
{
    "languages": {
        "en": {
            "name": "English",
            "flag": "🇬🇧", 
            "translations": {
                "welcome": "Welcome text",
                "category_examples": {
                    "example_key": "translated_value"
                }
            }
        }
    }
}
```

## Data Flow

### Game Session Flow

```
1. Player Setup
   ├── Enter name + select options
   ├── Validate inputs
   └── Enable start button

2. Session Creation
   ├── POST /api/start_game
   ├── Create WebGameSession
   ├── Generate first round item (AI/Database)
   └── Return session_id + round data

3. Round Loop
   ├── Request facts (POST /api/request_fact)
   ├── Submit guesses (POST /api/submit_guess)  
   ├── Get hints (POST /api/get_hint)
   └── Round completion → Score calculation

4. Session Management
   ├── New rounds (POST /api/new_round)
   ├── Give up (POST /api/give_up)
   └── Session completion → Database save
```

### AI Generation Flow

```
1. Prompt Construction
   ├── Category + subcategory hint
   ├── Difficulty configuration
   ├── Language-specific prompt template
   └── Cultural adaptation

2. OpenAI API Call
   ├── Azure OpenAI GPT-4
   ├── Timeout: 30 seconds
   ├── Retry: 3 attempts with backoff
   └── Response parsing

3. Fallback Strategy  
   ├── AI Generation (primary)
   ├── Database Retrieval (fallback)
   └── Static Error Item (last resort)

4. Content Storage
   ├── Save to generated_questions table
   ├── Include metadata (tokens, timing)
   └── Build offline question cache
```

### Database Operations

```
1. Connection Management
   ├── DATABASE_URL (primary)
   ├── Supabase fallback
   └── Local JSON fallback

2. Session Storage
   ├── game_sessions table
   ├── Individual round data
   └── Player statistics update

3. Offline Questions
   ├── generated_questions table
   ├── Usage tracking (question_usage)
   └── Availability checks

4. Statistics
   ├── Aggregated player stats
   ├── Global leaderboards  
   └── Performance metrics
```

## Class Reference

### Backend Classes Summary

| Class | Purpose | Key Methods | Properties |
|-------|---------|-------------|------------|
| `GameCategoryManager` | Category management | `get_category_hint()`, `find_category()` | `categories`, `category_usage_count` |
| `GameEngine` | AI integration | `generate_game_item()`, `_call_openai_api()` | `client`, `timeout`, `max_retries` |
| `AnswerChecker` | Answer validation | `is_correct_answer()`, `get_feedback()` | `similarity_threshold` |
| `WebGameSession` | Session management | `start_new_round()`, `add_guess()`, `get_hint()` | `session_id`, `current_item`, `total_score` |
| `ScoringSystem` | Score calculation | `calculate_round_score()`, `get_grade()` | `base_points`, `fact_penalty` |
| `LanguageManager` | Localization | `translate()`, `set_language()` | `current_language`, `translations` |
| `PostgreSQLHandler` | Database operations | `save_session()`, `get_offline_questions()` | `connection`, `is_connected_flag` |
| `CloudScoreKeeper` | Storage abstraction | `update_high_scores()`, `get_top_scores_display()` | `postgres_handler`, `local_keeper` |

### Frontend Classes Summary

| Class | Purpose | Key Methods | Properties |
|-------|---------|-------------|------------|
| `GameApp` | Main application | `startGame()`, `submitGuess()`, `requestFact()` | `gameSession`, `currentPlayer`, `offlineMode` |

### Data Classes

| Class | Purpose | Properties |
|-------|---------|------------|
| `GameRound` | Round result | `item_name`, `correct`, `round_score`, `time_taken` |
| `GameSession` | Session result | `rounds`, `total_score`, `player_name`, `start_time` |

This documentation provides a comprehensive overview of the Fact Quest's architecture, components, and functionality. The system demonstrates modern web development practices with robust error handling, graceful degradation, and multi-modal operation capabilities.
