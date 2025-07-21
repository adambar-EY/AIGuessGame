# AI Coding Agent Instructions for AI-Powered Guessing Game

## Project Overview
This is a **Flask web application** that creates an AI-powered multilingual guessing game where players guess items based on progressive AI-generated facts. The architecture emphasizes graceful degradation and dual-mode operation.

## Core Architecture

### Primary Components
- **`app.py`** (1800+ lines): Main Flask application with session management, API routes, and Azure OpenAI integration
- **`language_manager.py`**: Bilingual support (EN/PL) with localized AI prompts and UI translations
- **`postgresql_db.py`**: Direct PostgreSQL/Supabase integration using psycopg2 (NOT REST APIs)
- **`cloud_scoring.py`**: Abstraction layer providing automatic fallback from PostgreSQL to local JSON storage
- **`scoring.py`**: Core game logic for scoring and session management

### Critical Session Flow Pattern
```python
# 1. Game Start: Creates WebGameSession stored in active_sessions dict
session_id = str(uuid.uuid4())
game_session = WebGameSession(player_name, language, max_rounds)
active_sessions[session_id] = game_session

# 2. Round Generation: AI generation → Database storage → Facts revelation
item_data = game_engine.generate_game_item(category, subcategory_hint, lang_manager, difficulty)
game_session.start_new_round(category, item_data['name'], item_data['facts'], difficulty)

# 3. Answer Checking: Jaro-Winkler fuzzy matching (90% threshold)
is_correct, similarity, match_type = answer_checker.is_correct_answer(guess, current_item)
```

## Azure OpenAI Integration Patterns

### Dual Authentication Strategy
```python
# Production: Uses DefaultAzureCredential for managed identity
# Development: Uses API key from environment variables
if self.api_key:
    self.client = AzureOpenAI(azure_endpoint=self.endpoint, api_key=self.api_key)
else:
    credential = DefaultAzureCredential()
    self.client = AzureOpenAI(azure_endpoint=self.endpoint, azure_ad_token_provider=...)
```

### Triple Fallback Strategy
Always implement this pattern: **AI Generation → Database Retrieval → Error Item**
```python
try:
    item = self._call_openai_api(prompt)  # Primary: AI generation
except:
    item = self._get_database_item(category)  # Fallback: Database
    if not item:
        item = self._get_fallback_item()  # Last resort: Static error
```

## Database Integration Specifics

### Connection Strategy
- Uses **psycopg2 with connection pooling**, NOT REST APIs
- **Dual connection**: `DATABASE_URL` primary, fallback to `SUPABASE_URL` + password  
- **Graceful degradation**: Falls back to local JSON storage if PostgreSQL unavailable

### Key Tables
- `generated_questions`: AI content with metadata (tokens, timing, language)
- `game_sessions`: Player sessions with scoring data
- `player_stats`: Aggregated statistics for leaderboards

## Frontend Architecture Patterns

### JavaScript Class Structure
```javascript
class GameApp {
    constructor() {
        // State management
        this.gameSession = null;  // Session ID from backend
        this.currentFacts = [];   // Progressive fact revelation
        this.offlineMode = false; // Dual-mode indicator
    }
}
```

### Dual Game Mode Implementation
- **Online Mode**: AI generation via `/api/start_game` → Azure OpenAI
- **Offline Mode**: Database questions via `/api/start_offline_game` → PostgreSQL
- **Smart switching**: Auto-detects availability and suggests alternatives

## Critical Development Workflows

### Environment Setup (Always Required)
```bash
# Virtual environment is MANDATORY
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Required environment variables (copy from .env.example)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_KEY=your-key  # Optional in production (uses managed identity)
DATABASE_URL=postgresql://user:pass@host:port/db  # Optional for cloud features
```

### API Route Patterns
```python
# Session management pattern used across all routes
session_id = data.get('session_id') or session.get('game_session_id')
if not session_id or session_id not in active_sessions:
    return jsonify({'error': NO_ACTIVE_SESSION_ERROR}), 400
game_session = active_sessions[session_id]
```

## Project-Specific Conventions

### Error Handling Strategy
- **Graceful degradation**: Always provide fallbacks (AI → Database → Static)
- **User-friendly errors**: Use `language_manager` for localized error messages
- **Logging levels**: WARNING for normal operations, ERROR for actual failures

### Fuzzy Matching Implementation
Uses Jaro-Winkler algorithm with 90% threshold via `jellyfish` library:
```python
similarity = jellyfish.jaro_winkler_similarity(guess.lower(), answer.lower())
is_correct = similarity >= 0.90
```

### Mobile-First CSS Patterns
```css
@media (max-width: 768px) {
    .header { display: none; }  /* Hide by default */
    .show-header .header { display: block; }  /* Show when toggled */
    .hamburger-menu { display: flex; }  /* Show hamburger */
}
```

## Integration Points

### Language Support Pattern
- **Dual prompts**: Separate English/Polish AI generation prompts with cultural adaptation
- **Dynamic translation**: All UI elements use `data-translate` attributes
- **Consistent keys**: Use translation keys like `welcome_title`, `start_game` throughout

### Hint System Implementation
```python
# Reveal random letters from answer with position tracking
self.revealed_letters.add(position)
hint_display = self._create_hint_display()  # Shows "W_R_" format
```

## Common Development Pitfalls

1. **Session Management**: Always validate `session_id` exists in `active_sessions` dict before operations
2. **Database Fallback**: Handle PostgreSQL unavailability gracefully - never break core gameplay
3. **Language Context**: Pass `lang_manager` to AI generation for proper localized prompts
4. **Mobile Testing**: Test hamburger menu functionality and responsive spacing on actual devices
5. **AI Timeouts**: Implement proper error handling for Azure OpenAI calls (30s default timeout)

## Debugging Commands
```bash
# Always activate virtual environment first
.venv\Scripts\activate

# Test database connection
python -c "from postgresql_db import PostgreSQLHandler; db = PostgreSQLHandler(); print('Connected:', db.is_connected())"

# Verify Azure OpenAI setup
python -c "import os; print('OpenAI:', bool(os.getenv('AZURE_OPENAI_ENDPOINT')))"

# Run development server
python app.py  # Runs on 0.0.0.0:5001 by default
```

## Key Files for Understanding Architecture
- **`app.py`**: Central Flask application with all API routes and session management
- **`static/js/app.js`**: Frontend game logic with dual-mode support  
- **`cloud_scoring.py`**: Database abstraction with automatic fallback patterns
- **`language_manager.py`**: Internationalization and localized AI prompt management
