# AI-Powered Multilingual Guessing Game

An advanced Flask web app where players guess items based on progressive, AI-generated facts. Features bilingual support (English/Polish), Azure OpenAI integration, PostgreSQL/Supabase storage, and robust offline fallback.

## Features
- Progressive fact-based guessing game
- Azure OpenAI-powered fact generation (with DB and static fallback)
- Dual-mode: Online (AI) and Offline (database)
- Bilingual UI and prompts (EN/PL)
- Responsive, mobile-first design (carousel facts on mobile)
- PostgreSQL/Supabase integration (psycopg2, not REST)
- Graceful degradation: local JSON fallback if cloud unavailable
- Fuzzy answer matching (Jaro-Winkler, 90% threshold)
- Leaderboards, player stats, and session management

## Quick Start

### 1. Environment Setup
```pwsh
python -m venv .venv
.venv\Scripts\activate
copy .env.example .env  # Set your environment variables
```

### 2. Install Dependencies
```pwsh
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Edit `.env` and set:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `AZURE_OPENAI_API_KEY` (optional in production)
- `DATABASE_URL` (PostgreSQL connection string)

### 4. Run the App
```pwsh
python app.py
```
App runs on `http://0.0.0.0:5001` by default.

## Architecture
- **app.py**: Main Flask app, API routes, session management, Azure OpenAI
- **language_manager.py**: Bilingual support, translation, prompt localization
- **postgresql_db.py**: PostgreSQL/Supabase integration (psycopg2, connection pooling)
- **cloud_scoring.py**: Database abstraction, fallback to local JSON
- **scoring.py**: Game logic, scoring, session management
- **static/js/app.js**: Frontend logic, carousel, translation, UI state
- **static/css/style.css**: Responsive, mobile-first design


## Game Flow
1. **Start Game**: Create session, select language, category, difficulty
2. **Fact Generation**: AI → DB → Static fallback
3. **Guessing**: Fuzzy matching (Jaro-Winkler, 90%)
4. **Hints**: Fact hints (max 5), letter hints (max 3)
5. **Session/Score**: Leaderboards, stats, multi-round support


## Dual Mode
- **Online**: `/api/start_game` (AI via Azure OpenAI)
- **Offline**: `/api/start_offline_game` (DB fallback)
- Auto-detects availability, suggests alternatives


## Mobile & UI
- Carousel facts on mobile
- All controls visible, no scrolling required
- Hamburger menu hidden on mobile
- Responsive, modern CSS (Flexbox/Grid)


## Error Handling
- Graceful fallback: AI → DB → Static
- Localized error messages
- Logging: WARNING for normal, ERROR for failures


## Testing & Debugging
```pwsh
.venv\Scripts\activate
python -c "from postgresql_db import PostgreSQLHandler; db = PostgreSQLHandler(); print('Connected:', db.is_connected())"
python -c "import os; print('OpenAI:', bool(os.getenv('AZURE_OPENAI_ENDPOINT')))"
python app.py
```

## License
MIT License

---
For more details, see in-code documentation and `.github/copilot-instructions.md`.
