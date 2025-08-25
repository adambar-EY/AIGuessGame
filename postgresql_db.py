"""
PostgreSQL database handler for the AI-Powered Guessing Game
Provides direct connection to Supabase PostgreSQL using psycopg2.
"""
import os
import logging
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PostgreSQLHandler:
    """Direct PostgreSQL connection handler for Supabase."""
    
    # Constants to avoid duplication
    _CONNECTION_TEST_SQL = "SELECT 1"
    _CATEGORY_FILTER_SQL = " AND LOWER(category) = LOWER(%s)"
    
    def __init__(self):
        """Initialize PostgreSQL connection."""
        # Use simple assignments here to avoid introspection/type-annotation issues
        self.connection = None
        self.is_connected_flag = False
        self._connect_attempted = False
        self._setup_logging()
        # Defer connecting until first use to avoid blocking app startup
        # The actual connection will be attempted lazily in is_connected() or other methods
    
    def _get_connection(self) -> psycopg2.extensions.connection:
        """Get the connection, asserting it's not None for type checking."""
        assert self.connection is not None
        return self.connection
    
    def _setup_logging(self):
        """Setup logging for database operations."""
        logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.ERROR)  # Only show errors for database operations
    
    def _connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            # Try DATABASE_URL first
            if self._try_database_url_connection():
                return
                
            # Fallback to Supabase connection
            self._try_supabase_connection()
                    
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to PostgreSQL: {e}")
            self.is_connected_flag = False
    
    def _try_database_url_connection(self):
        """Try to connect using DATABASE_URL environment variable."""
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            return False
            
        self.logger.debug("Using DATABASE_URL for connection")
        try:
            self.connection = psycopg2.connect(
                database_url,
                sslmode='require',
                connect_timeout=10
            )
            self.connection.autocommit = True
            
            if self._test_connection():
                self.is_connected_flag = True
                self.logger.debug("Successfully connected to PostgreSQL database using DATABASE_URL")
                self._ensure_tables_exist()
                self._run_migrations()
                return True
                        
        except psycopg2.Error as e:
            self.logger.error(f"Failed to connect using DATABASE_URL: {e}")
            self._close_connection()
            
        return False
    
    def _try_supabase_connection(self):
        """Try to connect using Supabase environment variables."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_password = os.getenv('SUPABASE_PASSWORD')
        
        if not self._validate_supabase_env(supabase_url, supabase_password):
            return
            
        host_formats = self._get_supabase_hosts(supabase_url)
        base_params = self._get_supabase_connection_params(supabase_password)
        
        for host in host_formats:
            if self._try_host_connection(host, base_params):
                return
        
        # If we get here, all connection attempts failed
        self.logger.error("All PostgreSQL connection attempts failed")
        self.is_connected_flag = False
    
    def _validate_supabase_env(self, supabase_url, supabase_password):
        """Validate Supabase environment variables."""
        if not supabase_url:
            self.logger.error("SUPABASE_URL not found in environment variables")
            return False
            
        if not supabase_password:
            self.logger.error("SUPABASE_PASSWORD not found in environment variables")
            return False
            
        return True
    
    def _get_supabase_hosts(self, supabase_url):
        """Get list of possible Supabase host formats."""
        supabase_host = os.getenv('SUPABASE_HOST')
        
        if supabase_host:
            self.logger.debug(f"Using manual SUPABASE_HOST: {supabase_host}")
            return [supabase_host]
            
        # Parse the Supabase URL to extract project reference
        parsed = urlparse(supabase_url)
        project_ref = parsed.netloc.split('.')[0] if parsed.netloc else ""
        
        if not project_ref:
            self.logger.error("Could not extract project reference from SUPABASE_URL")
            return []
        
        # Return different possible Supabase database host formats
        return [
            f"db.{project_ref}.supabase.co",
            f"{project_ref}.pooler.supabase.com",
            f"{project_ref}.db.supabase.co",
            f"aws-0-{project_ref}.pooler.supabase.com",
            f"pooler.{project_ref}.supabase.co",
            f"{project_ref}-pooler.supabase.co"
        ]
    
    def _get_supabase_connection_params(self, supabase_password):
        """Get base connection parameters for Supabase."""
        return {
            'database': 'postgres',
            'user': 'postgres',
            'password': supabase_password,
            'port': 5432,
            'sslmode': 'require',
            'connect_timeout': 10
        }
    
    def _try_host_connection(self, host, base_params):
        """Try to connect to a specific host."""
        try:
            self.logger.debug(f"Attempting to connect to PostgreSQL at {host}")
            
            conn_params = {**base_params, 'host': host}
            self.connection = psycopg2.connect(**conn_params)
            self.connection.autocommit = True
            
            if self._test_connection():
                self.is_connected_flag = True
                self.logger.debug(f"Successfully connected to PostgreSQL database at {host}")
                self._ensure_tables_exist()
                self._run_migrations()
                return True
                
        except psycopg2.Error as e:
            self.logger.debug(f"Failed to connect to {host}: {e}")
            self._close_connection()
            
        return False
    
    def _test_connection(self):
        """Test database connection with a simple query."""
        if not self.connection:
            return False
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(self._CONNECTION_TEST_SQL)
                result = cursor.fetchone()
                return result is not None
        except Exception:
            return False
    
    def _close_connection(self):
        """Safely close the database connection."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
    
    def _ensure_tables_exist(self):
        """Create tables if they don't exist."""
        if not self.connection:
            return
            
        try:
            with self.connection.cursor() as cursor:
                # Create game_sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id SERIAL PRIMARY KEY,
                        player_name VARCHAR(255) NOT NULL,
                        start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        end_time TIMESTAMP WITH TIME ZONE,
                        total_score INTEGER DEFAULT 0,
                        rounds_won INTEGER DEFAULT 0,
                        rounds_lost INTEGER DEFAULT 0,
                        session_data JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                # Create generated_questions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS generated_questions (
                        id SERIAL PRIMARY KEY,
                        item_name VARCHAR(255) NOT NULL,
                        category VARCHAR(100),
                        subcategory VARCHAR(100),
                        difficulty VARCHAR(50),
                        facts JSONB,
                        language VARCHAR(10) DEFAULT 'en',
                        session_id VARCHAR(255),
                        player_name VARCHAR(255),
                        ai_model VARCHAR(100),
                        generation_time_ms INTEGER,
                        prompt_tokens INTEGER,
                        completion_tokens INTEGER,
                        used_in_round BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );
                """)
                
                # Create game_rounds table with comprehensive tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS game_rounds (
                        id SERIAL PRIMARY KEY,
                        session_id INTEGER,
                        question_id INTEGER,
                        player_name VARCHAR(255) NOT NULL,
                        item_name VARCHAR(255) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        subcategory VARCHAR(100),
                        difficulty VARCHAR(50) DEFAULT 'normal',
                        language VARCHAR(10) DEFAULT 'en',
                        facts_revealed INTEGER DEFAULT 0,
                        total_facts INTEGER DEFAULT 5,
                        hints_used INTEGER DEFAULT 0,
                        max_hints INTEGER DEFAULT 3,
                        guessed_correctly BOOLEAN DEFAULT FALSE,
                        guess_attempts INTEGER DEFAULT 0,
                        final_guess VARCHAR(500),
                        all_guesses TEXT,
                        similarity_score DECIMAL(5,4) DEFAULT 0.0,
                        match_type VARCHAR(50),
                        time_taken DECIMAL(10,3) DEFAULT 0.0,
                        round_score INTEGER DEFAULT 0,
                        base_score INTEGER DEFAULT 0,
                        score_multiplier DECIMAL(3,2) DEFAULT 1.0,
                        gave_up BOOLEAN DEFAULT FALSE,
                        auto_revealed BOOLEAN DEFAULT FALSE,
                        game_mode VARCHAR(20) DEFAULT 'online',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE SET NULL,
                        FOREIGN KEY (question_id) REFERENCES generated_questions(id) ON DELETE SET NULL
                    );
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_sessions_player_name 
                    ON game_sessions(player_name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_sessions_total_score 
                    ON game_sessions(total_score DESC);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_sessions_start_time 
                    ON game_sessions(start_time DESC);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_questions_item_name 
                    ON generated_questions(item_name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_questions_category 
                    ON generated_questions(category);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_questions_subcategory 
                    ON generated_questions(subcategory);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_questions_difficulty 
                    ON generated_questions(difficulty);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_questions_session_id 
                    ON generated_questions(session_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_generated_questions_player_name 
                    ON generated_questions(player_name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_rounds_question_id 
                    ON game_rounds(question_id);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_rounds_player_name 
                    ON game_rounds(player_name);
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_game_rounds_category 
                    ON game_rounds(category);
                """)
                
                self.logger.debug("Database tables and indexes ensured")
                
        except psycopg2.Error as e:
            self.logger.error(f"Error creating tables: {e}")
    
    def _run_migrations(self):
        """Run database migrations to update schema."""
        if not self.connection:
            return
            
        try:
            with self.connection.cursor() as cursor:
                # Check if used_in_round column exists in generated_questions table
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'generated_questions' 
                    AND column_name = 'used_in_round'
                """)
                
                if not cursor.fetchone():
                    # Add the used_in_round column if it doesn't exist
                    cursor.execute("""
                        ALTER TABLE generated_questions 
                        ADD COLUMN used_in_round BOOLEAN DEFAULT FALSE
                    """)
                    self.logger.info("Added used_in_round column to generated_questions table")
                    
                    # Update the updated_at timestamp for existing records
                    cursor.execute("""
                        UPDATE generated_questions 
                        SET updated_at = NOW() 
                        WHERE used_in_round IS NULL
                    """)
                    
                self.connection.commit()
                self.logger.debug("Database migrations completed")
                
        except psycopg2.Error as e:
            self.logger.error(f"Error running migrations: {e}")
            if self.connection:
                self.connection.rollback()
    
    def upgrade_game_rounds_table(self) -> bool:
        """Drop and recreate the game_rounds table with improved structure."""
        if not self.is_connected():
            self.logger.warning("Not connected to database, cannot upgrade table")
            return False
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor() as cursor:
                self.logger.info("Upgrading game_rounds table structure...")
                
                # Backup existing data if any
                cursor.execute("SELECT COUNT(*) FROM game_rounds")
                result = cursor.fetchone()
                existing_count = result[0] if result else 0
                
                if existing_count > 0:
                    self.logger.warning(f"Found {existing_count} existing rounds. Creating backup...")
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS game_rounds_backup AS 
                        SELECT * FROM game_rounds
                    """)
                    self.logger.info("Backup created as game_rounds_backup")
                
                # Drop the existing table
                cursor.execute("DROP TABLE IF EXISTS game_rounds CASCADE")
                
                # Create the new improved table
                cursor.execute("""
                    CREATE TABLE game_rounds (
                        id SERIAL PRIMARY KEY,
                        session_id INTEGER,
                        question_id INTEGER,
                        player_name VARCHAR(255) NOT NULL,
                        item_name VARCHAR(255) NOT NULL,
                        category VARCHAR(100) NOT NULL,
                        subcategory VARCHAR(100),
                        difficulty VARCHAR(50) DEFAULT 'normal',
                        language VARCHAR(10) DEFAULT 'en',
                        facts_revealed INTEGER DEFAULT 0,
                        total_facts INTEGER DEFAULT 5,
                        hints_used INTEGER DEFAULT 0,
                        max_hints INTEGER DEFAULT 3,
                        guessed_correctly BOOLEAN DEFAULT FALSE,
                        guess_attempts INTEGER DEFAULT 0,
                        final_guess VARCHAR(500),
                        all_guesses TEXT,
                        similarity_score DECIMAL(5,4) DEFAULT 0.0,
                        match_type VARCHAR(50),
                        time_taken DECIMAL(10,3) DEFAULT 0.0,
                        round_score INTEGER DEFAULT 0,
                        base_score INTEGER DEFAULT 0,
                        score_multiplier DECIMAL(3,2) DEFAULT 1.0,
                        gave_up BOOLEAN DEFAULT FALSE,
                        auto_revealed BOOLEAN DEFAULT FALSE,
                        game_mode VARCHAR(20) DEFAULT 'online',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE SET NULL,
                        FOREIGN KEY (question_id) REFERENCES generated_questions(id) ON DELETE SET NULL
                    );
                """)
                
                # Create optimized indexes
                cursor.execute("CREATE INDEX idx_game_rounds_session_id ON game_rounds(session_id)")
                cursor.execute("CREATE INDEX idx_game_rounds_player_name ON game_rounds(player_name)")
                cursor.execute("CREATE INDEX idx_game_rounds_category ON game_rounds(category)")
                cursor.execute("CREATE INDEX idx_game_rounds_difficulty ON game_rounds(difficulty)")
                cursor.execute("CREATE INDEX idx_game_rounds_language ON game_rounds(language)")
                cursor.execute("CREATE INDEX idx_game_rounds_created_at ON game_rounds(created_at)")
                cursor.execute("CREATE INDEX idx_game_rounds_guessed_correctly ON game_rounds(guessed_correctly)")
                cursor.execute("CREATE INDEX idx_game_rounds_game_mode ON game_rounds(game_mode)")
                
                # Create composite indexes for common queries
                cursor.execute("CREATE INDEX idx_game_rounds_player_category ON game_rounds(player_name, category)")
                cursor.execute("CREATE INDEX idx_game_rounds_player_difficulty ON game_rounds(player_name, difficulty)")
                cursor.execute("CREATE INDEX idx_game_rounds_player_language ON game_rounds(player_name, language)")
                
                # Create trigger for updated_at
                cursor.execute("""
                    CREATE OR REPLACE FUNCTION update_updated_at_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = NOW();
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';
                """)
                
                cursor.execute("""
                    CREATE TRIGGER update_game_rounds_updated_at 
                    BEFORE UPDATE ON game_rounds 
                    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                """)
                
                # Restore data if backup exists
                if existing_count > 0:
                    self.logger.info("Attempting to restore data from backup...")
                    cursor.execute("""
                        INSERT INTO game_rounds (
                            session_id, question_id, player_name, item_name, category, 
                            subcategory, difficulty, language, facts_revealed, total_facts,
                            guessed_correctly, guess_attempts, final_guess, similarity_score,
                            match_type, time_taken, round_score, created_at
                        )
                        SELECT 
                            session_id, question_id, player_name, item_name, category,
                            subcategory, difficulty, language, facts_revealed, total_facts,
                            guessed_correctly, guess_attempts, final_guess, similarity_score,
                            match_type, time_taken, round_score, created_at
                        FROM game_rounds_backup
                    """)
                    
                    restored_count = cursor.rowcount
                    self.logger.info(f"Restored {restored_count} rounds from backup")
                
                self.connection.commit()
                self.logger.info("Game rounds table upgrade completed successfully")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"Error upgrading game_rounds table: {e}")
            self.connection.rollback()
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error upgrading game_rounds table: {e}")
            self.connection.rollback()
            return False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        # Attempt to connect on first call (lazy connection)
        if not self._connect_attempted:
            self._connect_attempted = True
            self._connect()
        
        if not self.is_connected_flag or not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(self._CONNECTION_TEST_SQL)
                return True
        except Exception:
            self.is_connected_flag = False
            return False
    
    def save_session(self, session) -> bool:
        """Save a game session to the database."""
        if not self.is_connected() or not self.connection:
            self.logger.warning("Not connected to database, cannot save session")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Prepare session data
                session_data = {
                    'rounds': []
                }
                
                # Convert GameRound objects to dictionary format
                for round_obj in session.rounds:
                    if hasattr(round_obj, 'get'):
                        # Already a dictionary
                        round_data = {
                            'word': round_obj.get('word', ''),
                            'score': round_obj.get('score', 0),
                            'time_taken': round_obj.get('time_taken', 0),
                            'won': round_obj.get('won', False),
                            'guesses': round_obj.get('guesses', [])
                        }
                    else:
                        # GameRound object, convert to dictionary
                        round_data = {
                            'word': round_obj.item_name,
                            'category': round_obj.category,
                            'subcategory': round_obj.subcategory,
                            'facts_shown': round_obj.facts_shown,
                            'total_facts': round_obj.total_facts,
                            'correct': round_obj.correct,
                            'guess_attempts': round_obj.guess_attempts,
                            'similarity_score': round_obj.similarity_score,
                            'match_type': round_obj.match_type,
                            'time_taken': round_obj.time_taken,
                            'score': round_obj.round_score,
                            'won': round_obj.correct
                        }
                    session_data['rounds'].append(round_data)
                
                # Calculate stats
                rounds_won = sum(1 for r in session.rounds if (hasattr(r, 'correct') and r.correct) or (hasattr(r, 'get') and r.get('won', False)))
                rounds_lost = len(session.rounds) - rounds_won
                
                # Insert session
                cursor.execute("""
                    INSERT INTO game_sessions 
                    (player_name, start_time, end_time, total_score, rounds_won, rounds_lost, session_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    session.player_name,
                    session.start_time,
                    session.end_time,
                    session.total_score,
                    rounds_won,
                    rounds_lost,
                    psycopg2.extras.Json(session_data)
                ))
                
                result = cursor.fetchone()
                if result:
                    session_id = result[0]
                    self.logger.debug(f"Saved session {session_id} for player {session.player_name}")
                    
                    # Now save individual rounds to game_rounds table
                    rounds_saved = 0
                    for round_obj in session.rounds:
                        round_data = {}
                        
                        if hasattr(round_obj, 'get'):
                            # Already a dictionary
                            round_data = {
                                'player_name': session.player_name,
                                'item_name': round_obj.get('word', ''),
                                'category': round_obj.get('category', ''),
                                'subcategory': round_obj.get('subcategory', ''),
                                'difficulty': round_obj.get('difficulty', 'normal'),
                                'language': round_obj.get('language', 'en'),
                                'facts_revealed': round_obj.get('facts_shown', 0),
                                'total_facts': round_obj.get('total_facts', 5),
                                'guessed_correctly': round_obj.get('won', False),
                                'guess_attempts': len(round_obj.get('guesses', [])),
                                'final_guess': round_obj.get('guesses', [''])[-1] if round_obj.get('guesses') else '',
                                'similarity_score': round_obj.get('similarity_score', 0.0),
                                'match_type': round_obj.get('match_type', ''),
                                'time_taken': round_obj.get('time_taken', 0.0),
                                'round_score': round_obj.get('score', 0)
                            }
                        else:
                            # GameRound object, convert to dictionary
                            round_data = {
                                'player_name': session.player_name,
                                'item_name': round_obj.item_name,
                                'category': round_obj.category,
                                'subcategory': round_obj.subcategory,
                                'difficulty': getattr(round_obj, 'difficulty', 'normal'),
                                'language': getattr(round_obj, 'language', 'en'),
                                'facts_revealed': round_obj.facts_shown,
                                'total_facts': round_obj.total_facts,
                                'guessed_correctly': round_obj.correct,
                                'guess_attempts': round_obj.guess_attempts,
                                'final_guess': getattr(round_obj, 'final_guess', ''),
                                'similarity_score': round_obj.similarity_score,
                                'match_type': round_obj.match_type,
                                'time_taken': round_obj.time_taken,
                                'round_score': round_obj.round_score
                            }
                        
                        # Save this round to game_rounds table
                        if self.save_round(session_id, round_data):
                            rounds_saved += 1
                    
                    self.logger.debug(f"Saved {rounds_saved}/{len(session.rounds)} rounds to game_rounds table")
                    
                    # Also link any orphaned rounds (saved during gameplay) to this session
                    orphaned_rounds_updated = self.update_rounds_with_session_id(session_id, session.player_name)
                    if orphaned_rounds_updated > 0:
                        self.logger.debug(f"Linked {orphaned_rounds_updated} orphaned rounds to session {session_id}")
                    
                    return True
                else:
                    self.logger.error("Failed to get session ID after insert")
                    return False
                
        except psycopg2.Error as e:
            self.logger.error(f"Error saving session: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error saving session: {e}")
            return False
    
    def save_round(self, session_id: Optional[int], round_data: Dict, question_id: Optional[int] = None) -> bool:
        """Save an individual round to the game_rounds table with enhanced tracking."""
        if not self.is_connected() or not self.connection:
            self.logger.warning("Not connected to database, cannot save round")
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Extract all guesses as JSON string
                all_guesses = round_data.get('all_guesses', [])
                if isinstance(all_guesses, list):
                    import json
                    all_guesses_str = json.dumps(all_guesses) if all_guesses else None
                else:
                    all_guesses_str = str(all_guesses) if all_guesses else None
                
                cursor.execute("""
                    INSERT INTO game_rounds 
                    (session_id, question_id, player_name, item_name, category, subcategory, 
                     difficulty, language, facts_revealed, total_facts, hints_used, max_hints,
                     guessed_correctly, guess_attempts, final_guess, all_guesses, 
                     similarity_score, match_type, time_taken, round_score, base_score, 
                     score_multiplier, gave_up, auto_revealed, game_mode)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    session_id,
                    question_id,
                    round_data.get('player_name', ''),
                    round_data.get('item_name', ''),
                    round_data.get('category', ''),
                    round_data.get('subcategory', ''),
                    round_data.get('difficulty', 'normal'),
                    round_data.get('language', 'en'),
                    round_data.get('facts_revealed', 0),
                    round_data.get('total_facts', 5),
                    round_data.get('hints_used', 0),
                    round_data.get('max_hints', 3),
                    round_data.get('guessed_correctly', False),
                    round_data.get('guess_attempts', 0),
                    round_data.get('final_guess', ''),
                    all_guesses_str,
                    round_data.get('similarity_score', 0.0),
                    round_data.get('match_type', ''),
                    round_data.get('time_taken', 0.0),
                    round_data.get('round_score', 0),
                    round_data.get('base_score', 0),
                    round_data.get('score_multiplier', 1.0),
                    round_data.get('gave_up', False),
                    round_data.get('auto_revealed', False),
                    round_data.get('game_mode', 'online')
                ))
                
                result = cursor.fetchone()
                if result:
                    round_id = result[0]
                    self.logger.debug(f"Saved enhanced round {round_id} for session {session_id}")
                    return True
                else:
                    self.logger.error("Failed to get round ID after insert")
                    return False
                
        except psycopg2.Error as e:
            self.logger.error(f"Error saving round: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error saving round: {e}")
            return False
    
    def update_rounds_with_session_id(self, session_id: int, player_name: str) -> int:
        """Update rounds without session_id to link them to a completed session."""
        if not self.is_connected() or not self.connection:
            self.logger.warning("Not connected to database, cannot update rounds")
            return 0
        
        try:
            with self.connection.cursor() as cursor:
                # Update rounds that don't have a session_id but match the player
                cursor.execute("""
                    UPDATE game_rounds 
                    SET session_id = %s 
                    WHERE session_id IS NULL 
                    AND player_name = %s 
                    AND created_at >= NOW() - INTERVAL '1 hour'
                    ORDER BY created_at DESC
                """, (session_id, player_name))
                
                updated_count = cursor.rowcount
                self.logger.debug(f"Updated {updated_count} rounds with session_id {session_id}")
                return updated_count
                
        except psycopg2.Error as e:
            self.logger.error(f"Error updating rounds with session_id: {e}")
            return 0
        except Exception as e:
            self.logger.error(f"Unexpected error updating rounds with session_id: {e}")
            return 0
    
    def get_player_round_stats(self, player_name: str) -> Dict:
        """Get enhanced detailed round statistics for a player using new tracking fields."""
        if not self.is_connected() or not self.connection:
            return {}
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get comprehensive round statistics with new fields
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_rounds,
                        COUNT(*) FILTER (WHERE guessed_correctly = true) as rounds_won,
                        COUNT(*) FILTER (WHERE guessed_correctly = false) as rounds_lost,
                        COUNT(*) FILTER (WHERE gave_up = true) as rounds_gave_up,
                        COUNT(*) FILTER (WHERE auto_revealed = true) as rounds_auto_revealed,
                        AVG(round_score) as avg_score,
                        AVG(base_score) as avg_base_score,
                        AVG(score_multiplier) as avg_multiplier,
                        AVG(time_taken) as avg_time,
                        AVG(facts_revealed) as avg_facts_used,
                        AVG(hints_used) as avg_hints_used,
                        AVG(guess_attempts) as avg_attempts,
                        MAX(round_score) as best_round_score,
                        MIN(time_taken) FILTER (WHERE guessed_correctly = true) as fastest_win_time,
                        COUNT(*) FILTER (WHERE game_mode = 'online') as online_rounds,
                        COUNT(*) FILTER (WHERE game_mode = 'offline') as offline_rounds,
                        SUM(round_score) as total_score
                    FROM game_rounds 
                    WHERE player_name = %s
                """, (player_name,))
                
                stats = dict(cursor.fetchone() or {})
                
                # Get category breakdown with enhanced metrics
                cursor.execute("""
                    SELECT 
                        category,
                        COUNT(*) as rounds,
                        COUNT(*) FILTER (WHERE guessed_correctly = true) as wins,
                        AVG(round_score) as avg_score,
                        AVG(hints_used) as avg_hints,
                        AVG(facts_revealed) as avg_facts,
                        AVG(score_multiplier) as avg_multiplier
                    FROM game_rounds 
                    WHERE player_name = %s
                    GROUP BY category
                    ORDER BY rounds DESC
                """, (player_name,))
                
                categories = [dict(row) for row in cursor.fetchall()]
                stats['categories'] = categories
                
                # Get difficulty breakdown with enhanced metrics
                cursor.execute("""
                    SELECT 
                        difficulty,
                        COUNT(*) as rounds,
                        COUNT(*) FILTER (WHERE guessed_correctly = true) as wins,
                        AVG(round_score) as avg_score,
                        AVG(base_score) as avg_base_score,
                        AVG(score_multiplier) as avg_multiplier,
                        AVG(hints_used) as avg_hints,
                        AVG(time_taken) as avg_time
                    FROM game_rounds 
                    WHERE player_name = %s
                    GROUP BY difficulty
                    ORDER BY 
                        CASE difficulty 
                            WHEN 'easy' THEN 1 
                            WHEN 'normal' THEN 2 
                            WHEN 'hard' THEN 3 
                            ELSE 4 
                        END
                """, (player_name,))
                
                difficulties = [dict(row) for row in cursor.fetchall()]
                stats['difficulties'] = difficulties
                
                # Get hint usage statistics
                cursor.execute("""
                    SELECT 
                        hints_used,
                        COUNT(*) as rounds,
                        COUNT(*) FILTER (WHERE guessed_correctly = true) as wins,
                        AVG(round_score) as avg_score
                    FROM game_rounds 
                    WHERE player_name = %s
                    GROUP BY hints_used
                    ORDER BY hints_used
                """, (player_name,))
                
                hint_stats = [dict(row) for row in cursor.fetchall()]
                stats['hint_usage'] = hint_stats
                
                # Get game mode statistics
                cursor.execute("""
                    SELECT 
                        game_mode,
                        COUNT(*) as rounds,
                        COUNT(*) FILTER (WHERE guessed_correctly = true) as wins,
                        AVG(round_score) as avg_score,
                        AVG(time_taken) as avg_time
                    FROM game_rounds 
                    WHERE player_name = %s
                    GROUP BY game_mode
                """, (player_name,))
                
                game_modes = [dict(row) for row in cursor.fetchall()]
                stats['game_modes'] = game_modes
                
                return stats
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting player round stats: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting player round stats: {e}")
            return {}
    
    def get_recent_rounds(self, player_name: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent rounds, optionally filtered by player."""
        if not self.is_connected() or not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if player_name:
                    cursor.execute("""
                        SELECT * FROM game_rounds 
                        WHERE player_name = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (player_name, limit))
                else:
                    cursor.execute("""
                        SELECT * FROM game_rounds 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting recent rounds: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting recent rounds: {e}")
            return []
    
    def get_top_sessions(self, limit: int = 10) -> List[Dict]:
        """Get top scoring sessions."""
        if not self.is_connected() or not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT player_name, start_time, end_time, total_score, 
                           rounds_won, rounds_lost, session_data
                    FROM game_sessions
                    ORDER BY total_score DESC, start_time DESC
                    LIMIT %s
                """, (limit,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting top sessions: {e}")
            return []
    
    def get_player_sessions(self, player_name: str, limit: int = 5) -> List[Dict]:
        """Get recent sessions for a specific player."""
        if not self.is_connected() or not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT player_name, start_time, end_time, total_score,
                           rounds_won, rounds_lost, session_data
                    FROM game_sessions
                    WHERE player_name = %s
                    ORDER BY start_time DESC
                    LIMIT %s
                """, (player_name, limit))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting player sessions: {e}")
            return []
    
    def get_global_stats(self) -> Dict:
        """Get global game statistics."""
        if not self.is_connected() or not self.connection:
            return {}
        
        try:
            with self.connection.cursor() as cursor:
                basic_stats = self._get_basic_stats(cursor)
                
                if not basic_stats or basic_stats[0] is None:
                    return {}
                
                best_round_score, fastest_round = self._get_best_round_stats(cursor)
                
                return {
                    'best_session_score': basic_stats[0] or 0,
                    'best_round_score': best_round_score,
                    'fastest_round': fastest_round if fastest_round != float('inf') else 0,
                    'total_wins': basic_stats[1] or 0,
                    'total_games': basic_stats[2] or 0,
                    'total_sessions': basic_stats[3] or 0
                }
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting global stats: {e}")
            return {}
    
    def _get_basic_stats(self, cursor):
        """Get basic statistics from the database."""
        cursor.execute("""
            SELECT 
                MAX(total_score) as best_session_score,
                SUM(rounds_won) as total_wins,
                SUM(rounds_won + rounds_lost) as total_games,
                COUNT(*) as total_sessions
            FROM game_sessions
        """)
        return cursor.fetchone()
    
    def _get_best_round_stats(self, cursor):
        """Get best round statistics from session data."""
        cursor.execute("""
            SELECT session_data
            FROM game_sessions
            WHERE session_data IS NOT NULL
        """)
        
        best_round_score = 0
        fastest_round = float('inf')
        
        for row in cursor.fetchall():
            session_data = row[0]
            if session_data and 'rounds' in session_data:
                round_best_score, round_fastest_time = self._process_round_data(session_data['rounds'])
                best_round_score = max(best_round_score, round_best_score)
                fastest_round = min(fastest_round, round_fastest_time)
        
        return best_round_score, fastest_round
    
    def _process_round_data(self, rounds):
        """Process individual round data to find best score and fastest time."""
        best_score = 0
        fastest_time = float('inf')
        
        for round_data in rounds:
            # Best round score
            round_score = round_data.get('score', 0)
            if round_score > best_score:
                best_score = round_score
            
            # Fastest round
            time_taken = round_data.get('time_taken', float('inf'))
            if time_taken < fastest_time:
                fastest_time = time_taken
        
        return best_score, fastest_time
    
    def close(self):
        """Close database connection."""
        if self.connection:
            try:
                self.connection.close()
                self.logger.debug("Database connection closed")
            except Exception:
                pass
        self.is_connected_flag = False

    def check_item_exists(self, item_name: str, category: Optional[str] = None, language: Optional[str] = None, time_window_hours: int = 24) -> bool:
        """Check if an item was recently generated to prevent duplicates."""
        if not self.is_connected() or not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                # Simple query without parameterized intervals to avoid SQL syntax issues
                base_query = "SELECT COUNT(*) FROM generated_questions WHERE LOWER(item_name) = LOWER(%s)"
                params = [item_name]
                
                if category:
                    base_query += self._CATEGORY_FILTER_SQL
                    params.append(category)
                
                if language:
                    base_query += " AND language = %s"
                    params.append(language)
                
                # Add time filter if specified (using simple approach)
                if time_window_hours > 0:
                    base_query += f" AND created_at >= NOW() - INTERVAL '{time_window_hours} hours'"
                
                cursor.execute(base_query, params)
                result = cursor.fetchone()
                count = result[0] if result else 0
                
                exists = count > 0
                if exists:
                    self.logger.info(f"Duplicate detected: '{item_name}' was generated {count} time(s) recently")
                
                return exists
                
        except Exception as e:
            self.logger.error(f"Error checking item existence: {e}")
            return False

    def get_recent_items_for_category(self, category: str, subcategory: Optional[str] = None, 
                                    language: Optional[str] = None, hours_back: int = 48, limit: int = 50) -> List[str]:
        """Get list of recently generated items for a category to help AI avoid duplicates."""
        if not self.is_connected() or not self.connection:
            return []
        
        try:
            with self.connection.cursor() as cursor:
                base_query = """
                    SELECT item_name 
                    FROM generated_questions 
                    WHERE LOWER(category) = LOWER(%s)
                """
                params = [category]
                
                if subcategory:
                    base_query += " AND LOWER(subcategory) = LOWER(%s)"
                    params.append(subcategory)
                
                if language:
                    base_query += " AND language = %s"
                    params.append(language)
                
                if hours_back > 0:
                    base_query += f" AND created_at >= NOW() - INTERVAL '{hours_back} hours'"
                
                base_query += f" ORDER BY created_at DESC LIMIT {limit}"
                
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                # Remove duplicates while preserving order
                items = []
                seen = set()
                for row in results:
                    item_name = row[0]
                    if item_name not in seen:
                        items.append(item_name)
                        seen.add(item_name)
                
                self.logger.info(f"Found {len(items)} recent items for category '{category}'" + 
                               (f"/{subcategory}" if subcategory else ""))
                
                return items
                
        except Exception as e:
            self.logger.error(f"Error getting recent items for category: {e}")
            return []

    def save_generated_question(self, question_data: Dict) -> Optional[int]:
        """Save a generated question to the database."""
        if not self.is_connected() or not self.connection:
            self.logger.warning("Not connected to database, cannot save question")
            return None
        
        try:
            with self.connection.cursor() as cursor:
                # Insert question data using correct column names
                cursor.execute("""
                    INSERT INTO generated_questions (
                        item_name, category, subcategory, difficulty, facts, 
                        language, session_id, player_name, ai_model, 
                        generation_time_ms, prompt_tokens, completion_tokens
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    question_data.get('item_name'),
                    question_data.get('category'),
                    question_data.get('subcategory'),
                    question_data.get('difficulty'),
                    psycopg2.extras.Json(question_data.get('facts', [])),
                    question_data.get('language', 'en'),
                    question_data.get('session_id'),
                    question_data.get('player_name'),
                    question_data.get('ai_model', 'gpt-4o'),
                    question_data.get('generation_time_ms'),
                    question_data.get('prompt_tokens'),
                    question_data.get('completion_tokens')
                ))
                
                result = cursor.fetchone()
                question_id = result[0] if result else None
                
                self.logger.info(f"Saved generated question '{question_data.get('item_name')}' with ID {question_id}")
                
                if question_id:
                    self.logger.debug(f"Saved generated question {question_id}: {question_data['item_name']}")
                else:
                    self.logger.error("Failed to get question ID after insert")
                
                return question_id
                
        except psycopg2.Error as e:
            self.logger.error(f"Error saving generated question: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error saving generated question: {e}")
            return None
    
    def get_offline_questions(self, 
                             category: Optional[str] = None, 
                             difficulty: Optional[str] = None, 
                             language: str = 'en',
                             exclude_used: bool = True,
                             limit: int = 50) -> List[Dict]:
        """
        Get questions from database for offline mode.
        
        Args:
            category: Filter by category (None for any)
            difficulty: Filter by difficulty (None for any)
            language: Language filter
            exclude_used: Exclude questions already used in rounds
            limit: Maximum number of questions to return
        """
        if not self.is_connected() or not self.connection:
            return []
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build query based on filters
                base_query = """
                    SELECT 
                        id, item_name, category, subcategory, difficulty,
                        facts, language, created_at
                    FROM generated_questions 
                    WHERE language = %s
                """
                params: List[Any] = [language]
                
                if category:
                    base_query += self._CATEGORY_FILTER_SQL
                    params.append(category)
                
                if difficulty:
                    base_query += " AND LOWER(difficulty) = LOWER(%s)"
                    params.append(difficulty)
                
                if exclude_used:
                    base_query += " AND used_in_round = FALSE"
                
                # Order by creation date for variety
                base_query += " ORDER BY created_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(base_query, params)
                questions = cursor.fetchall()
                
                # Convert to list of dicts and ensure facts are properly parsed
                result = []
                for q in questions:
                    question_dict = dict(q)
                    # Ensure facts is a list
                    if isinstance(question_dict.get('facts'), str):
                        import json
                        try:
                            question_dict['facts'] = json.loads(question_dict['facts'])
                        except (json.JSONDecodeError, TypeError):
                            question_dict['facts'] = []
                    elif not isinstance(question_dict.get('facts'), list):
                        question_dict['facts'] = []
                    
                    result.append(question_dict)
                
                self.logger.info(f"Retrieved {len(result)} offline questions for category={category}, difficulty={difficulty}")
                return result
                
        except psycopg2.Error as e:
            self.logger.error(f"Error retrieving offline questions: {e}")
            return []

    def get_random_offline_question(self, 
                                   category: Optional[str] = None, 
                                   difficulty: Optional[str] = None,
                                   language: str = 'en',
                                   exclude_used: bool = True) -> Optional[Dict]:
        """
        Get a single random question from database for offline mode.
        """
        if not self.is_connected() or not self.connection:
            return None
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build query with random selection
                base_query = """
                    SELECT 
                        id, item_name, category, subcategory, difficulty,
                        facts, language, created_at
                    FROM generated_questions 
                    WHERE language = %s
                """
                params: List[Any] = [language]
                
                if category:
                    base_query += self._CATEGORY_FILTER_SQL
                    params.append(category)
                
                if difficulty:
                    base_query += " AND LOWER(difficulty) = LOWER(%s)"
                    params.append(difficulty)
                
                if exclude_used:
                    base_query += " AND used_in_round = FALSE"
                
                # Random selection
                base_query += " ORDER BY RANDOM() LIMIT 1"
                
                cursor.execute(base_query, params)
                question = cursor.fetchone()
                
                if question:
                    question_dict = dict(question)
                    # Ensure facts is a list
                    if isinstance(question_dict.get('facts'), str):
                        import json
                        try:
                            question_dict['facts'] = json.loads(question_dict['facts'])
                        except (json.JSONDecodeError, TypeError):
                            question_dict['facts'] = []
                    elif not isinstance(question_dict.get('facts'), list):
                        question_dict['facts'] = []
                    
                    self.logger.info(f"Retrieved random offline question: {question_dict['item_name']}")
                    return question_dict
                else:
                    self.logger.warning(f"No offline questions found for category={category}, difficulty={difficulty}")
                    return None
                
        except psycopg2.Error as e:
            self.logger.error(f"Error retrieving random offline question: {e}")
            return None

    def mark_question_as_used(self, question_id: int) -> bool:
        """Mark a question as used in a round."""
        if not self.is_connected() or not self.connection:
            return False
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE generated_questions 
                    SET used_in_round = TRUE, updated_at = NOW()
                    WHERE id = %s
                """, (question_id,))
                
                self.logger.debug(f"Marked question {question_id} as used")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"Error marking question as used: {e}")
            return False

    def get_offline_question_count(self, category: Optional[str] = None, 
                                  difficulty: Optional[str] = None, 
                                  language: str = 'en', 
                                  exclude_used: bool = True) -> int:
        """Get count of available questions for offline mode."""
        if not self.is_connected():
            self.logger.warning("Not connected to database, cannot count offline questions")
            return 0
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor() as cursor:
                # Build query with optional filters
                where_conditions = ["language = %s"]
                params: List[Any] = [language]
                
                if category:
                    # Case-insensitive comparison for category
                    where_conditions.append("LOWER(category) = LOWER(%s)")
                    params.append(category)
                
                if difficulty:
                    # Case-insensitive comparison for difficulty
                    where_conditions.append("LOWER(difficulty) = LOWER(%s)")
                    params.append(difficulty)
                
                if exclude_used:
                    where_conditions.append("(used_in_round IS FALSE OR used_in_round IS NULL)")
                
                where_clause = " AND ".join(where_conditions)
                
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM generated_questions 
                    WHERE {where_clause}
                """, params)
                
                result = cursor.fetchone()
                return result[0] if result else 0
                
        except psycopg2.Error as e:
            self.logger.error(f"Error counting offline questions: {e}")
            return 0

    def get_random_question(self, category: Optional[str] = None, difficulty: Optional[str] = None, 
                           language: str = 'en', exclude_recent_hours: int = 24) -> Optional[Dict]:
        """Get a random question from the database for offline mode."""
        if not self.is_connected():
            self.logger.warning("Not connected to database, cannot get random question")
            return None
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build query with optional filters
                where_conditions = ["language = %s"]
                params: List[Any] = [language]
                
                if category:
                    where_conditions.append("category = %s")
                    params.append(category)
                
                if difficulty:
                    where_conditions.append("difficulty = %s")
                    params.append(difficulty)
                
                # Exclude recently used questions
                if exclude_recent_hours > 0:
                    where_conditions.append("created_at < NOW() - INTERVAL '%s hours'")
                    params.append(exclude_recent_hours)
                
                where_clause = " AND ".join(where_conditions)
                
                cursor.execute(f"""
                    SELECT id, item_name, category, subcategory, difficulty, 
                           facts, language, created_at, used_in_round
                    FROM generated_questions 
                    WHERE {where_clause}
                    ORDER BY RANDOM() 
                    LIMIT 1
                """, params)
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting random question: {e}")
            return None
    
    def get_questions_by_category(self, category: str, language: str = 'en', 
                                 limit: int = 10) -> List[Dict]:
        """Get questions by category for offline mode."""
        if not self.is_connected():
            self.logger.warning("Not connected to database, cannot get questions by category")
            return []
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT id, item_name, category, subcategory, difficulty, 
                           facts, language, created_at, used_in_round
                    FROM generated_questions 
                    WHERE category = %s AND language = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (category, language, limit))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting questions by category: {e}")
            return []
    
    def get_available_offline_categories(self, language: str = 'en') -> List[Dict]:
        """Get categories that have available questions for offline mode."""
        if not self.is_connected():
            self.logger.warning("Not connected to database, cannot get available categories")
            return []
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT category, COUNT(*) as question_count,
                           COUNT(DISTINCT difficulty) as difficulty_count,
                           MIN(created_at) as first_question,
                           MAX(created_at) as latest_question
                    FROM generated_questions 
                    WHERE language = %s
                    GROUP BY category
                    HAVING COUNT(*) > 0
                    ORDER BY question_count DESC, category ASC
                """, (language,))
                
                results = cursor.fetchall()
                return [dict(row) for row in results]
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting available categories: {e}")
            return []
    
    def mark_question_used(self, question_id: int) -> bool:
        """Mark a question as used in a round."""
        if not self.is_connected():
            return False
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE generated_questions 
                    SET used_in_round = TRUE, updated_at = NOW()
                    WHERE id = %s
                """, (question_id,))
                
                self.connection.commit()
                return cursor.rowcount > 0
                
        except psycopg2.Error as e:
            self.logger.error(f"Error marking question as used: {e}")
            return False
    
    def get_offline_stats(self, language: str = 'en') -> Dict:
        """Get statistics about available offline questions."""
        if not self.is_connected():
            return {}
        
        assert self.connection is not None  # Type hint for type checker
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_questions,
                        COUNT(DISTINCT category) as total_categories,
                        COUNT(DISTINCT difficulty) as total_difficulties,
                        COUNT(CASE WHEN used_in_round = TRUE THEN 1 END) as used_questions,
                        MIN(created_at) as oldest_question,
                        MAX(created_at) as newest_question
                    FROM generated_questions 
                    WHERE language = %s
                """, (language,))
                
                result = cursor.fetchone()
                return dict(result) if result else {}
                
        except psycopg2.Error as e:
            self.logger.error(f"Error getting offline stats: {e}")
            return {}
