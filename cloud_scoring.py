"""
Enhanced scoring system with PostgreSQL integration for the AI-Powered Guessing Game
Provides fallback to local JSON if PostgreSQL is unavailable.
"""
import os
import logging
from typing import List, Dict, Optional, Any
from scoring import GameSession, ScoreKeeper as LocalScoreKeeper
from postgresql_db import PostgreSQLHandler

class CloudScoreKeeper:
    """Enhanced score keeper with PostgreSQL integration and local fallback."""
    
    def __init__(self):
        """Initialize with PostgreSQL and local fallback."""
        self.postgres_handler = PostgreSQLHandler()
        self.local_keeper = LocalScoreKeeper()  # Fallback to local JSON
        self.use_cloud = self.postgres_handler.is_connected()
        
        # Expose scoring system for compatibility
        self.scoring_system = self.local_keeper.scoring_system
        
        if self.use_cloud:
            logging.debug("Using PostgreSQL for score storage")
        else:
            logging.debug("Using local JSON for score storage (PostgreSQL unavailable)")
    
    def update_high_scores(self, session: GameSession):
        """Update scores in both cloud and local storage."""
        if self.use_cloud:
            success = self.postgres_handler.save_session(session)
            if not success:
                logging.warning("Failed to save to PostgreSQL, falling back to local storage")
                self.local_keeper.update_high_scores(session)
        else:
            self.local_keeper.update_high_scores(session)
    
    def get_top_scores_display(self, lang_manager=None) -> str:
        """Get formatted top scores display with cloud or local data."""
        if self.use_cloud:
            return self._get_cloud_top_scores_display(lang_manager)
        else:
            return self.local_keeper.get_top_scores_display(lang_manager)
    
    def _get_cloud_top_scores_display(self, lang_manager=None) -> str:
        """Get top scores from PostgreSQL."""
        is_polish = bool(lang_manager and lang_manager.current_language == 'pl')
        
        # Get data from PostgreSQL
        top_sessions = self.postgres_handler.get_top_sessions(10)
        global_stats = self.postgres_handler.get_global_stats()
        
        # Format sessions
        formatted_sessions = self._format_cloud_sessions(top_sessions)
        
        if not formatted_sessions:
            return self._get_cloud_no_scores_message(is_polish, lang_manager)
        
        # Build display components
        display = self._build_cloud_header(is_polish, lang_manager)
        display += self._build_cloud_sessions_list(formatted_sessions, is_polish, lang_manager)
        display += self._build_cloud_global_stats(global_stats, is_polish)
        
        return display
    
    def _format_cloud_sessions(self, sessions: List[Dict]) -> List[Dict]:
        """Format session data from database to display format."""
        formatted_sessions = []
        for session in sessions:
            rounds_won = session.get('rounds_won', 0)
            rounds_lost = session.get('rounds_lost', 0)
            total_rounds = rounds_won + rounds_lost
            
            # Extract average time from session data
            avg_time = self._extract_session_avg_time(session.get('session_data', {}))
            
            formatted_session = {
                'date': session['start_time'].isoformat() if session.get('start_time') else '',
                'player_name': session.get('player_name', 'Unknown'),
                'score': session.get('total_score', 0),
                'wins': rounds_won,
                'rounds': total_rounds,
                'grade': self._calculate_grade(session.get('total_score', 0), total_rounds, avg_time)
            }
            formatted_sessions.append(formatted_session)
        return formatted_sessions
    
    def _extract_session_avg_time(self, session_data: Dict) -> float:
        """Extract average time from session data."""
        if session_data and 'rounds' in session_data:
            times = [r.get('time_taken', 0) for r in session_data['rounds'] if r.get('time_taken', 0) > 0]
            return sum(times) / len(times) if times else 0.0
        return 0.0
    
    def _get_cloud_no_scores_message(self, is_polish: bool, lang_manager: Any) -> str:
        """Get no scores message for cloud display."""
        if is_polish and lang_manager:
            return lang_manager.get_text('no_scores_yet')
        else:
            return "📊 No scores recorded yet. Play a game to see your results here!"
    
    def _build_cloud_header(self, is_polish: bool, lang_manager: Any) -> str:
        """Build cloud leaderboard header."""
        if is_polish and lang_manager:
            return f"""
{lang_manager.get_text('top_scores_title')} 🌍
{'=' * 50}

🥇 Najlepsze Sesje (Globalnie):
"""
        else:
            title = "🏆 GLOBAL LEADERBOARD 🌍"
            if lang_manager:
                title = lang_manager.get_text('top_scores_title') + " 🌍"
            return f"""
{title}
{'=' * 50}

🥇 Top Sessions (Worldwide):
"""
    
    def _build_cloud_sessions_list(self, formatted_sessions: List[Dict], is_polish: bool, lang_manager: Any) -> str:
        """Build cloud sessions list display."""
        display = ""
        for i, session in enumerate(formatted_sessions, 1):
            if is_polish and lang_manager:
                session_data = session.copy()
                session_data['date'] = session['date'][:10]
                display += f"   {i:2d}. {lang_manager.get_text('session_details').format(**session_data)}\n"
            else:
                display += f"   {i:2d}. 📅 {session['date'][:10]} | 👤 {session['player_name']} | 🎯 {session['score']:,} pts | 📊 {session['wins']}/{session['rounds']} wins | 🏆 Grade {session['grade']}\n"
        return display
    
    def _build_cloud_global_stats(self, global_stats: Dict, is_polish: bool) -> str:
        """Build cloud global statistics display."""
        if not global_stats:
            return ""
            
        if is_polish:
            return f"""
🌍 Globalne Statystyki:
   🏆 Najlepsza Sesja: {global_stats.get('best_session_score', 0):,} punktów
   ⭐ Najlepsza Runda: {global_stats.get('best_round_score', 0):,} punktów
   ⚡ Najszybsza Runda: {global_stats.get('fastest_round', 0):.1f}s
   📊 Ogólne Statystyki: {global_stats.get('total_wins', 0)}/{global_stats.get('total_games', 0)} ({global_stats.get('total_wins', 0)/max(global_stats.get('total_games', 1), 1)*100:.1f}% wygranych)
"""
        else:
            fastest = global_stats.get('fastest_round', float('inf'))
            fastest_str = f"{fastest:.1f}s" if fastest and fastest != float('inf') else "N/A"
            
            return f"""
🌍 Global Statistics:
   🏆 Best Session: {global_stats.get('best_session_score', 0):,} points
   ⭐ Best Round: {global_stats.get('best_round_score', 0):,} points
   ⚡ Fastest Round: {fastest_str}
   📊 Overall Stats: {global_stats.get('total_wins', 0)}/{global_stats.get('total_games', 0)} ({global_stats.get('total_wins', 0)/max(global_stats.get('total_games', 1), 1)*100:.1f}% wins)
"""
    
    def _calculate_grade(self, score: int, total_rounds: int = 0, avg_time: float = 0.0) -> str:
        """Calculate grade based on average points per round and average time."""
        # Calculate average points per round
        avg_points = (score / total_rounds) if total_rounds > 0 else 0
        
        # Time factor: excellent < 20s, good < 30s, average < 45s, poor >= 45s
        # Time bonus threshold in scoring system is 30s
        if avg_time <= 20:
            time_factor = 1.2  # 20% bonus for very fast responses
        elif avg_time <= 30:
            time_factor = 1.1  # 10% bonus for fast responses (time bonus threshold)
        elif avg_time <= 45:
            time_factor = 1.0  # No bonus/penalty for reasonable time
        elif avg_time <= 60:
            time_factor = 0.9  # 10% penalty for slow responses
        else:
            time_factor = 0.8  # 20% penalty for very slow responses
        
        # Apply time factor to average points
        adjusted_avg_points = avg_points * time_factor
        
        # Determine grade based on time-adjusted average points
        if adjusted_avg_points >= 800:
            return "A+"
        elif adjusted_avg_points >= 700:
            return "A"
        elif adjusted_avg_points >= 600:
            return "B+"
        elif adjusted_avg_points >= 500:
            return "B"
        elif adjusted_avg_points >= 400:
            return "C+"
        elif adjusted_avg_points >= 300:
            return "C"
        elif adjusted_avg_points >= 200:
            return "D"
        else:
            return "F"
    
    def get_player_stats(self, player_name: str, lang_manager=None) -> str:
        """Get statistics for a specific player."""
        if not self.use_cloud:
            return "Player statistics require cloud database connection."
        
        is_polish = bool(lang_manager and lang_manager.current_language == 'pl')
        sessions = self.postgres_handler.get_player_sessions(player_name, 5)
        
        if not sessions:
            return self._get_no_player_data_message(player_name, is_polish)
        
        # Format sessions and calculate stats
        formatted_sessions = self._format_player_sessions(sessions)
        player_stats = self._calculate_player_stats(formatted_sessions)
        
        # Build display
        display = self._build_player_stats_header(player_name, player_stats, is_polish)
        display += self._build_recent_sessions_list(formatted_sessions, is_polish)
        
        return display
    
    def _get_no_player_data_message(self, player_name: str, is_polish: bool) -> str:
        """Get message when no player data is found."""
        if is_polish:
            return f"👤 Brak danych dla gracza: {player_name}"
        else:
            return f"👤 No data found for player: {player_name}"
    
    def _format_player_sessions(self, sessions: List[Dict]) -> List[Dict]:
        """Format player sessions for display."""
        formatted_sessions = []
        for session in sessions:
            rounds_won = session.get('rounds_won', 0)
            rounds_lost = session.get('rounds_lost', 0)
            total_rounds = rounds_won + rounds_lost
            
            avg_time = self._extract_session_avg_time(session.get('session_data', {}))
            
            formatted_session = {
                'date': session['start_time'].isoformat() if session.get('start_time') else '',
                'score': session.get('total_score', 0),
                'wins': rounds_won,
                'rounds': total_rounds,
                'grade': self._calculate_grade(session.get('total_score', 0), total_rounds, avg_time)
            }
            formatted_sessions.append(formatted_session)
        return formatted_sessions
    
    def _calculate_player_stats(self, formatted_sessions: List[Dict]) -> Dict:
        """Calculate player statistics from sessions."""
        return {
            'total_score': sum(s['score'] for s in formatted_sessions),
            'total_wins': sum(s['wins'] for s in formatted_sessions),
            'total_rounds': sum(s['rounds'] for s in formatted_sessions),
            'best_score': max(s['score'] for s in formatted_sessions),
            'session_count': len(formatted_sessions)
        }
    
    def _build_player_stats_header(self, player_name: str, stats: Dict, is_polish: bool) -> str:
        """Build player statistics header."""
        win_rate = (stats['total_wins'] / stats['total_rounds'] * 100) if stats['total_rounds'] > 0 else 0
        
        if is_polish:
            return f"""
👤 Statystyki Gracza: {player_name}
{'=' * 40}
🎯 Łączny Wynik: {stats['total_score']:,} punktów
📊 Współczynnik Wygranych: {win_rate:.1f}% ({stats['total_wins']}/{stats['total_rounds']})
⭐ Najlepszy Wynik: {stats['best_score']:,} punktów
🎮 Ostatnie Sesje: {stats['session_count']}

📋 Ostatnie Gry:
"""
        else:
            return f"""
👤 Player Stats: {player_name}
{'=' * 40}
🎯 Total Score: {stats['total_score']:,} points
📊 Win Rate: {win_rate:.1f}% ({stats['total_wins']}/{stats['total_rounds']})
⭐ Best Score: {stats['best_score']:,} points
🎮 Recent Sessions: {stats['session_count']}

📋 Recent Games:
"""
    
    def _build_recent_sessions_list(self, formatted_sessions: List[Dict], is_polish: bool) -> str:
        """Build recent sessions list display."""
        display = ""
        for i, session in enumerate(formatted_sessions, 1):
            date_str = session['date'][:10] if len(session['date']) > 10 else session['date']
            if is_polish:
                display += f"   {i}. 📅 {date_str} | 🎯 {session['score']:,} pkt | 📊 {session['wins']}/{session['rounds']} wygranych | 🏆 Ocena {session['grade']}\n"
            else:
                display += f"   {i}. 📅 {date_str} | 🎯 {session['score']:,} pts | 📊 {session['wins']}/{session['rounds']} wins | 🏆 Grade {session['grade']}\n"
        return display

    def get_score_summary(self, session: GameSession, lang_manager=None) -> str:
        """Get formatted score summary with language support."""
        # Always use local scoring system for score summary as it handles the session analysis
        return self.local_keeper.get_score_summary(session, lang_manager)
    
    def close(self):
        """Close database connections."""
        if self.postgres_handler:
            self.postgres_handler.close()
