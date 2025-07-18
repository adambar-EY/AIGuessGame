"""
Scoring system for the AI-Powered Guessing Game
"""
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

@dataclass
class GameRound:
    """Represents a single game round result"""
    item_name: str
    category: str
    subcategory: Optional[str]
    facts_shown: int  # Number of facts shown before correct guess
    total_facts: int  # Total facts available (usually 5)
    correct: bool
    guess_attempts: int  # Number of wrong guesses before correct
    similarity_score: float  # Final similarity score (0.0 to 1.0)
    match_type: str  # "exact", "similar", "different"
    time_taken: float  # Time in seconds for the round
    round_score: int  # Points scored for this round

@dataclass
class GameSession:
    """Represents a complete game session"""
    start_time: datetime
    end_time: Optional[datetime]
    rounds: List[GameRound]
    total_score: int
    rounds_won: int
    rounds_lost: int
    average_facts_used: float
    average_time_per_round: float
    player_name: str = "Anonymous Player"

class ScoringSystem:
    """Handles all scoring calculations and statistics"""
    
    def __init__(self):
        self.base_points = 1000  # Starting points for each round
        self.fact_penalty = 150  # Points lost per fact shown
        self.guess_penalty = 50   # Points lost per wrong guess
        self.similarity_bonus = 100  # Bonus for exact matches
        self.time_bonus_threshold = 30  # Seconds for time bonus
        self.time_bonus_points = 200  # Bonus for quick answers
        self.streak_multiplier = 1.1  # Multiplier for consecutive wins
        
    def calculate_round_score(self, round_result: GameRound) -> int:
        """Calculate score for a single round"""
        if not round_result.correct:
            return 0
        
        score = self.base_points
        
        # Penalty for facts shown (reward guessing early)
        facts_penalty = (round_result.facts_shown - 1) * self.fact_penalty
        score -= facts_penalty
        
        # Penalty for wrong guesses
        guess_penalty = round_result.guess_attempts * self.guess_penalty
        score -= guess_penalty
        
        # Bonus for exact matches
        if round_result.match_type == "exact":
            score += self.similarity_bonus
        
        # Time bonus for quick answers
        if round_result.time_taken <= self.time_bonus_threshold:
            score += self.time_bonus_points
        
        # Ensure minimum score
        return max(score, 50)  # Minimum 50 points for any correct answer
    
    def calculate_streak_bonus(self, consecutive_wins: int) -> float:
        """Calculate streak multiplier based on consecutive wins"""
        if consecutive_wins <= 1:
            return 1.0
        return min(self.streak_multiplier ** (consecutive_wins - 1), 3.0)  # Cap at 3x
    
    def get_performance_grade(self, session: GameSession) -> str:
        """Get letter grade based on performance"""
        if session.rounds_won == 0:
            return "F"
        
        win_rate = session.rounds_won / len(session.rounds)
        avg_efficiency = 1 - (session.average_facts_used - 1) / 4  # Efficiency based on facts used
        
        performance_score = (win_rate * 0.6 + avg_efficiency * 0.4) * 100
        
        if performance_score >= 90:
            return "A+"
        elif performance_score >= 85:
            return "A"
        elif performance_score >= 80:
            return "A-"
        elif performance_score >= 75:
            return "B+"
        elif performance_score >= 70:
            return "B"
        elif performance_score >= 65:
            return "B-"
        elif performance_score >= 60:
            return "C+"
        elif performance_score >= 55:
            return "C"
        elif performance_score >= 50:
            return "C-"
        elif performance_score >= 45:
            return "D"
        else:
            return "F"
    
    def get_achievements(self, session: GameSession) -> List[str]:
        """Get list of achievements earned"""
        achievements = []
        
        # Add different types of achievements
        achievements.extend(self._get_streak_achievements(session.rounds))
        achievements.extend(self._get_speed_achievements(session.rounds))
        achievements.extend(self._get_efficiency_achievements(session.rounds))
        achievements.extend(self._get_accuracy_achievements(session.rounds))
        achievements.extend(self._get_category_achievements(session.rounds))
        achievements.extend(self._get_session_achievements(session))
        
        return achievements
    
    def _get_streak_achievements(self, rounds: List[GameRound]) -> List[str]:
        """Get win streak achievements"""
        achievements = []
        consecutive_wins = self._get_max_consecutive_wins(rounds)
        if consecutive_wins >= 10:
            achievements.append("🔥 Unstoppable (10+ win streak)")
        elif consecutive_wins >= 5:
            achievements.append("🎯 On Fire (5+ win streak)")
        elif consecutive_wins >= 3:
            achievements.append("⚡ Hot Streak (3+ win streak)")
        return achievements
    
    def _get_speed_achievements(self, rounds: List[GameRound]) -> List[str]:
        """Get speed-based achievements"""
        achievements = []
        quick_rounds = sum(1 for r in rounds if r.correct and r.time_taken <= 15)
        if quick_rounds >= 5:
            achievements.append("⚡ Lightning Fast (5+ quick answers)")
        elif quick_rounds >= 3:
            achievements.append("🚀 Speedy (3+ quick answers)")
        return achievements
    
    def _get_efficiency_achievements(self, rounds: List[GameRound]) -> List[str]:
        """Get efficiency-based achievements"""
        achievements = []
        first_guess_wins = sum(1 for r in rounds if r.correct and r.facts_shown == 1)
        if first_guess_wins >= 3:
            achievements.append("🧠 Mind Reader (3+ first-fact wins)")
        return achievements
    
    def _get_accuracy_achievements(self, rounds: List[GameRound]) -> List[str]:
        """Get accuracy-based achievements"""
        achievements = []
        exact_matches = sum(1 for r in rounds if r.correct and r.match_type == "exact")
        if exact_matches >= 5:
            achievements.append("📝 Perfect Speller (5+ exact matches)")
        return achievements
    
    def _get_category_achievements(self, rounds: List[GameRound]) -> List[str]:
        """Get category mastery achievements"""
        achievements = []
        category_wins = {}
        for round_result in rounds:
            if round_result.correct:
                category_wins[round_result.category] = category_wins.get(round_result.category, 0) + 1
        
        for category, wins in category_wins.items():
            if wins >= 3:
                achievements.append(f"🏆 {category.title()} Expert (3+ wins)")
        return achievements
    
    def _get_session_achievements(self, session: GameSession) -> List[str]:
        """Get session-based achievements"""
        achievements = []
        if session.rounds_won == len(session.rounds) and len(session.rounds) >= 5:
            achievements.append("👑 Flawless Victory (Perfect session)")
        return achievements
    
    def _get_max_consecutive_wins(self, rounds: List[GameRound]) -> int:
        """Get maximum consecutive wins in the session"""
        max_streak = 0
        current_streak = 0
        
        for round_result in rounds:
            if round_result.correct:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak

class ScoreKeeper:
    """Manages score tracking and persistence"""
    
    def __init__(self, scores_file="scores.json"):
        self.scores_file = scores_file
        self.scoring_system = ScoringSystem()
        self.high_scores = self.load_high_scores()
    
    def load_high_scores(self) -> Dict:
        """Load high scores from file"""
        try:
            with open(self.scores_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "best_session_score": 0,
                "best_round_score": 0,
                "longest_streak": 0,
                "fastest_round": float('inf'),
                "total_games": 0,
                "total_wins": 0,
                "sessions": []
            }
    
    def save_high_scores(self):
        """Save high scores to file"""
        with open(self.scores_file, 'w') as f:
            json.dump(self.high_scores, f, indent=2, default=str)
    
    def update_high_scores(self, session: GameSession):
        """Update high scores with new session"""
        # Update session high score
        if session.total_score > self.high_scores["best_session_score"]:
            self.high_scores["best_session_score"] = session.total_score
        
        # Update round high scores
        for round_result in session.rounds:
            if round_result.round_score > self.high_scores["best_round_score"]:
                self.high_scores["best_round_score"] = round_result.round_score
            
            if round_result.correct and round_result.time_taken < self.high_scores["fastest_round"]:
                self.high_scores["fastest_round"] = round_result.time_taken
        
        # Update streak
        max_streak = self.scoring_system._get_max_consecutive_wins(session.rounds)
        if max_streak > self.high_scores["longest_streak"]:
            self.high_scores["longest_streak"] = max_streak
        
        # Update totals
        self.high_scores["total_games"] += len(session.rounds)
        self.high_scores["total_wins"] += session.rounds_won
        
        # Save recent sessions (keep last 10)
        session_data = {
            "date": session.start_time.isoformat(),
            "player_name": session.player_name,
            "score": session.total_score,
            "rounds": len(session.rounds),
            "wins": session.rounds_won,
            "grade": self.scoring_system.get_performance_grade(session)
        }
        
        self.high_scores["sessions"].append(session_data)
        if len(self.high_scores["sessions"]) > 10:
            self.high_scores["sessions"] = self.high_scores["sessions"][-10:]
        
        self.save_high_scores()
    
    def get_score_summary(self, session: GameSession, lang_manager=None) -> str:
        """Get formatted score summary with language support"""
        grade = self.scoring_system.get_performance_grade(session)
        achievements = self.scoring_system.get_achievements(session)
        
        # Check if we should use Polish translations
        is_polish = lang_manager and lang_manager.current_language == 'pl'
        
        if is_polish:
            summary = f"""
🎯 Sesja Gry Zakończona!
{'=' * 40}
📊 Wynik: {session.total_score:,} punktów
🏆 Ocena: {grade}
📈 Rundy: {session.rounds_won}/{len(session.rounds)} wygranych
⏱️  Śr. Czas: {session.average_time_per_round:.1f}s na rundę
📋 Śr. Fakty: {session.average_facts_used:.1f}/5 faktów użytych

🏅 Osiągnięcia:
"""
        else:
            summary = f"""
🎯 Game Session Complete!
{'=' * 40}
📊 Score: {session.total_score:,} points
🏆 Grade: {grade}
📈 Rounds: {session.rounds_won}/{len(session.rounds)} won
⏱️  Avg Time: {session.average_time_per_round:.1f}s per round
📋 Avg Facts: {session.average_facts_used:.1f}/5 facts used

🏅 Achievements:
"""
        
        if achievements:
            for achievement in achievements:
                summary += f"   {achievement}\n"
        else:
            if is_polish:
                summary += "   Graj dalej, aby odblokować osiągnięcia!\n"
            else:
                summary += "   Keep playing to unlock achievements!\n"
        
        # Show high scores
        if is_polish:
            summary += f"""
🎖️  Rekordy Osobiste:
   Najlepsza Sesja: {self.high_scores['best_session_score']:,} punktów
   Najlepsza Runda: {self.high_scores['best_round_score']:,} punktów
   Najdłuższa Seria: {self.high_scores['longest_streak']} wygrane
   Najszybsza Runda: {self.high_scores['fastest_round']:.1f}s
   Ogólny Wsp. Wygranych: {self.high_scores['total_wins']}/{self.high_scores['total_games']} ({self.high_scores['total_wins']/max(self.high_scores['total_games'], 1)*100:.1f}%)
"""
        else:
            summary += f"""
🎖️  Personal Records:
   Best Session: {self.high_scores['best_session_score']:,} points
   Best Round: {self.high_scores['best_round_score']:,} points
   Longest Streak: {self.high_scores['longest_streak']} wins
   Fastest Round: {self.high_scores['fastest_round']:.1f}s
   Total Win Rate: {self.high_scores['total_wins']}/{self.high_scores['total_games']} ({self.high_scores['total_wins']/max(self.high_scores['total_games'], 1)*100:.1f}%)
"""
        
        return summary

    def get_top_scores_display(self, lang_manager=None) -> str:
        """Get formatted top scores/leaderboard display with language support"""
        is_polish = bool(lang_manager and lang_manager.current_language == 'pl')
        
        if not self.high_scores["sessions"]:
            return self._get_no_scores_message(is_polish, lang_manager)
        
        # Sort sessions by score (highest first)
        sorted_sessions = sorted(self.high_scores["sessions"], key=lambda x: x["score"], reverse=True)
        
        display = self._get_leaderboard_header(is_polish, lang_manager)
        display += self._get_top_sessions_display(sorted_sessions[:10], is_polish, lang_manager)
        display += self._get_personal_records_display(is_polish)
        
        return display
    
    def _get_no_scores_message(self, is_polish: bool, lang_manager: Any) -> str:
        """Get message when no scores are available"""
        if is_polish and lang_manager:
            return lang_manager.get_text('no_scores_yet')
        else:
            return "📊 No scores recorded yet. Play a game to see your results here!"
    
    def _get_leaderboard_header(self, is_polish: bool, lang_manager: Any) -> str:
        """Get leaderboard header text"""
        if is_polish and lang_manager:
            return f"""
{lang_manager.get_text('top_scores_title')}
{'=' * 50}

🥇 Najlepsze Sesje:
"""
        else:
            title = "🏆 TOP SCORES LEADERBOARD"
            if lang_manager:
                title = lang_manager.get_text('top_scores_title')
            return f"""
{title}
{'=' * 50}

🥇 Top Sessions:
"""
    
    def _get_top_sessions_display(self, sorted_sessions: List[Dict], is_polish: bool, lang_manager: Any) -> str:
        """Get display text for top sessions"""
        display = ""
        for i, session in enumerate(sorted_sessions, 1):
            date_str = session["date"][:10] if len(session["date"]) > 10 else session["date"]
            player_name = session.get("player_name", "Anonymous Player")
            
            if is_polish and lang_manager:
                session_data = session.copy()
                session_data['date'] = date_str
                session_data['player_name'] = player_name
                display += f"   {i:2d}. {lang_manager.get_text('session_details').format(**session_data)}\n"
            else:
                display += f"   {i:2d}. 📅 {date_str} | 👤 {player_name} | 🎯 {session['score']:,} pts | 📊 {session['wins']}/{session['rounds']} wins | 🏆 Grade {session['grade']}\n"
        
        return display
    
    def _get_personal_records_display(self, is_polish: bool) -> str:
        """Get personal records display text"""
        if is_polish:
            return f"""
🎖️  Rekordy Osobiste:
   🏆 Najlepsza Sesja: {self.high_scores['best_session_score']:,} punktów
   ⭐ Najlepsza Runda: {self.high_scores['best_round_score']:,} punktów
   🔥 Najdłuższa Seria: {self.high_scores['longest_streak']} wygranych
   ⚡ Najszybsza Runda: {self.high_scores['fastest_round']:.1f}s
   📊 Ogólne Statystyki: {self.high_scores['total_wins']}/{self.high_scores['total_games']} ({self.high_scores['total_wins']/max(self.high_scores['total_games'], 1)*100:.1f}% wygranych)
   🎮 Sesje Zagrane: {len(self.high_scores['sessions'])}
"""
        else:
            return f"""
🎖️  Personal Records:
   🏆 Best Session: {self.high_scores['best_session_score']:,} points
   ⭐ Best Round: {self.high_scores['best_round_score']:,} points
   🔥 Longest Streak: {self.high_scores['longest_streak']} wins
   ⚡ Fastest Round: {self.high_scores['fastest_round']:.1f}s
   📊 Overall Stats: {self.high_scores['total_wins']}/{self.high_scores['total_games']} ({self.high_scores['total_wins']/max(self.high_scores['total_games'], 1)*100:.1f}% wins)
   🎮 Sessions Played: {len(self.high_scores['sessions'])}
"""
