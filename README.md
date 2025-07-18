# 🎮 AI-Powered Guessing Game with Scoring

A sophisticated multilingual guessing game powered by Azure OpenAI that generates dynamic facts and challenges players to guess items from various categories.

## ✨ Features

### 🎯 **Core Gameplay**
- **AI-Generated Content**: Uses Azure OpenAI to create unique items and progressive facts
- **Dynamic Scoring System**: Points based on speed, accuracy, and number of facts used
- **Multiple Difficulty Levels**: Easy, Normal, and Hard with different scoring multipliers
- **Category-Based Hints**: 40+ categories with hundreds of subcategory examples
- **Smart Answer Matching**: Fuzzy matching using Jaro-Winkler algorithm

### 🌍 **Multilingual Support**
- **Full Localization**: Complete English and Polish language support
- **Dynamic Translation**: All categories, examples, and UI elements translated
- **Cultural Adaptation**: Localized prompts and feedback messages

### 🎲 **Flexible Game Modes**
- **Round Selection**: Choose 1-50 rounds or play unlimited
- **Progress Tracking**: Real-time round progress and statistics
- **Comprehensive Results**: Detailed final statistics with win rates and averages

### 📊 **Advanced Scoring**
- **Streak Bonuses**: Consecutive wins multiply your score
- **Time Bonuses**: Quick answers earn extra points
- **Difficulty Multipliers**: Higher difficulty = higher rewards
- **Personal Records**: Track your best performances

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI subscription
- Required Python packages (see `requirements.txt`)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd GuessGame
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Azure OpenAI and Database**
   Create a `.env` file with your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=your_endpoint_here
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
   AZURE_OPENAI_API_VERSION=2024-02-01
   
   # Optional: For cloud leaderboards (Supabase PostgreSQL)
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_PASSWORD=your-database-password-here
   ```

4. **Run the game**
   ```bash
   python guess_game_scored.py
   ```

## 🎮 How to Play

1. **Language Selection**: Choose English or Polish
2. **Difficulty Selection**: Pick Easy, Normal, or Hard difficulty
3. **Round Selection**: Choose 1-50 rounds or unlimited play
4. **Category Selection**: 
   - Type a category name or number
   - Use `list` to see all categories
   - Press Enter for random category
5. **Gameplay**: 
   - Read progressive facts about an item
   - Guess at any time or see the next fact
   - Earn points based on speed and accuracy
6. **Final Results**: View comprehensive statistics and total score

## 📁 Project Structure

```
GuessGame/
├── guess_game_scored.py      # Main game engine
├── language_manager.py       # Multilingual support system
├── scoring.py               # Local scoring and statistics system
├── cloud_scoring.py         # Cloud/local score keeper abstraction  
├── postgresql_db.py         # PostgreSQL database integration (Supabase)
├── categories.json          # Category definitions and examples
├── languages.json          # All translations and localizations
├── supabase_schema.sql     # Database schema for Supabase setup
├── test_postgresql.py      # PostgreSQL connection test script
├── requirements.txt         # Python dependencies
├── .env                    # Environment configuration (not in repo)
├── .env.template           # Template for environment setup
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🌐 Supported Languages

- **English (en)** 🇺🇸 - Complete support
- **Polish (pl)** 🇵🇱 - Complete support with 400+ translated examples

## 📊 Categories

The game includes 40+ main categories with hundreds of subcategory examples:

- **Animals**: Mammals, birds, reptiles, sea creatures, insects
- **Food**: Fruits, vegetables, desserts, international cuisine, beverages
- **Technology**: Gadgets, software, inventions, communication devices
- **Entertainment**: Movies, music, books, games, sports
- **Science**: Physics, chemistry, biology, astronomy, mathematics
- **Geography**: Countries, cities, landmarks, natural features
- **Culture**: Art, history, mythology, philosophy, religion
- And many more...

## 🎯 Scoring System

### Base Scoring
- **Starting Points**: 1,000 points per round
- **Fact Penalty**: -150 points per fact shown
- **Guess Penalty**: -50 points per wrong guess
- **Time Bonus**: +200 points for answers under 30 seconds

### Multipliers
- **Difficulty**: Easy (1.0x), Normal (1.2x), Hard (1.5x)
- **Streak Bonus**: Up to 2.0x for consecutive wins
- **Similarity Bonus**: +100 points for exact matches

### Grading
- **A+**: 90%+ win rate
- **A**: 80-89% win rate
- **B**: 70-79% win rate
- **C**: 60-69% win rate
- **D**: 50-59% win rate
- **F**: Below 50% win rate

## 🛠️ Technical Features

- **Azure OpenAI Integration**: GPT-4 powered content generation
- **Fuzzy Matching**: 90% similarity threshold for answer matching
- **Robust Error Handling**: Graceful fallbacks and error recovery
- **Clean Architecture**: Modular design with separation of concerns
- **Type Safety**: Comprehensive type hints and validation
- **Persistent Storage**: High scores and statistics tracking

## ☁️ Cloud Leaderboards (PostgreSQL/Supabase)

You can enable a global, cloud-based leaderboard and player statistics using Supabase's PostgreSQL database (completely free):

### How it works
- **Direct PostgreSQL connection** using psycopg2 (no API limits)
- **All scores and sessions are stored in the cloud** (if configured)
- **Global leaderboard**: See top scores from all players
- **Player statistics**: View your own or any player's stats
- **Automatic fallback**: If PostgreSQL is not available, the game uses local JSON storage

### Setup Instructions

1. **Create a free Supabase account**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project (completely free, no credit card required)
   - Set a strong database password when prompted
   - Wait for the project to be ready

2. **Set up the database**
   - In your Supabase dashboard, go to the SQL Editor
   - Copy and paste the contents of `supabase_schema.sql` into the editor
   - Run the SQL to create the tables and indexes

3. **Get your project credentials**
   - In your project settings, go to "Database"
   - Note your project URL (looks like: `https://abc123.supabase.co`)
   - You'll need the database password you set during project creation

4. **Test your connection**
   ```bash
   python test_postgresql.py
   ```
   This will verify your configuration is correct.

5. **Update your `.env` file**
   ```env
   # Your existing Azure OpenAI config...
   
   # Add these for cloud leaderboards
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_PASSWORD=your-database-password-here
   ```

6. **Run the game**
   ```bash
   python guess_game_scored.py
   ```

- If PostgreSQL is configured, you'll see a 🌍 global leaderboard and can view player stats from the main menu.
- If not, the game will use local storage as before.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Azure OpenAI**: For providing the AI capabilities
- **Jellyfish**: For fuzzy string matching algorithms
- **Community**: For testing and feedback

## 📧 Support

If you have questions or need help:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

**Happy Gaming! 🎮**
