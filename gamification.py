"""
Gamification system for AI Chef
Tracks cooking streaks, badges/achievements, and weekly challenges
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class CookingStreak:
    """Track user's cooking streak."""
    
    def __init__(self, filename="cooking_streak.json"):
        self.filename = filename
        self.data = self.load_streak()
    
    def load_streak(self):
        """Load streak data from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._default_data()
        return self._default_data()
    
    def _default_data(self):
        """Return default streak data structure."""
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "last_cooked_date": None,
            "total_meals_cooked": 0,
            "quick_meals": 0,
            "vegetarian_meals": 0,
            "vegan_meals": 0,
            "cuisine_counts": {}
        }
    
    def save_streak(self):
        """Save streak data to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_meal_cooked(self, cuisine: str = None, cooking_time: int = None, is_vegetarian: bool = False, is_vegan: bool = False):
        """Record that a meal was cooked today."""
        today = datetime.now().date().isoformat()
        last_date = self.data.get("last_cooked_date")
        
        self.data["total_meals_cooked"] += 1
        
        if last_date is None:
            # First meal ever
            self.data["current_streak"] = 1
            self.data["last_cooked_date"] = today
        else:
            last_cooked = datetime.fromisoformat(last_date).date()
            today_date = datetime.now().date()
            days_diff = (today_date - last_cooked).days
            
            if days_diff == 0:
                # Already cooked today, don't increment streak
                pass
            elif days_diff == 1:
                # Cooked consecutive day, increase streak
                self.data["current_streak"] += 1
                self.data["last_cooked_date"] = today
            else:
                # Streak broken, reset
                self.data["current_streak"] = 1
                self.data["last_cooked_date"] = today
        
        # Update longest streak if needed
        if self.data["current_streak"] > self.data.get("longest_streak", 0):
            self.data["longest_streak"] = self.data["current_streak"]

        # Track cooking metadata for achievements/challenges
        if cooking_time and cooking_time <= 30:
            self.data["quick_meals"] = self.data.get("quick_meals", 0) + 1

        if is_vegetarian:
            self.data["vegetarian_meals"] = self.data.get("vegetarian_meals", 0) + 1

        if is_vegan:
            self.data["vegan_meals"] = self.data.get("vegan_meals", 0) + 1

        if cuisine:
            cuisine_key = cuisine.strip().lower()
            counts = self.data.get("cuisine_counts", {})
            counts[cuisine_key] = counts.get(cuisine_key, 0) + 1
            self.data["cuisine_counts"] = counts
        
        self.save_streak()
    
    def get_streak_info(self):
        """Get current streak information."""
        return {
            "current_streak": self.data["current_streak"],
            "longest_streak": self.data["longest_streak"],
            "total_meals": self.data["total_meals_cooked"]
        }


class Achievement:
    """Represents a single achievement/badge."""
    
    def __init__(self, id: str, name: str, description: str, icon: str, unlocked: bool = False, unlock_date: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.unlocked = unlocked
        self.unlock_date = unlock_date
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "unlocked": self.unlocked,
            "unlock_date": self.unlock_date
        }


class AchievementTracker:
    """Track user achievements and badges."""
    
    # Define all possible achievements
    ACHIEVEMENTS = {
        "first_recipe": Achievement(
            "first_recipe",
            "👨‍🍳 Your First Dish",
            "Cook your first recipe",
            "👨‍🍳"
        ),
        "italian_explorer": Achievement(
            "italian_explorer",
            "🇮🇹 Italian Explorer",
            "Cook 3 Italian recipes",
            "🇮🇹"
        ),
        "asian_master": Achievement(
            "asian_master",
            "🍜 Asian Master",
            "Cook 3 Asian recipes",
            "🍜"
        ),
        "mexican_fiesta": Achievement(
            "mexican_fiesta",
            "🌮 Mexican Fiesta",
            "Cook 3 Mexican recipes",
            "🌮"
        ),
        "vegetarian_champion": Achievement(
            "vegetarian_champion",
            "🥗 Vegetarian Champion",
            "Cook 5 vegetarian recipes",
            "🥗"
        ),
        "vegan_virtuoso": Achievement(
            "vegan_virtuoso",
            "🌱 Vegan Virtuoso",
            "Cook 5 vegan recipes",
            "🌱"
        ),
        "speed_cook": Achievement(
            "speed_cook",
            "⚡ Speed Cook",
            "Cook 5 recipes under 30 minutes",
            "⚡"
        ),
        "gourmet_chef": Achievement(
            "gourmet_chef",
            "👑 Gourmet Chef",
            "Cook 10 recipes",
            "👑"
        ),
        "master_chef": Achievement(
            "master_chef",
            "🏆 Master Chef",
            "Cook 25 recipes",
            "🏆"
        ),
        "culinary_legend": Achievement(
            "culinary_legend",
            "⭐ Culinary Legend",
            "Cook 50 recipes",
            "⭐"
        ),
        "week_warrior": Achievement(
            "week_warrior",
            "🔥 Week Warrior",
            "Maintain a 7-day cooking streak",
            "🔥"
        ),
    }
    
    def __init__(self, filename="achievements.json"):
        self.filename = filename
        self.achievements = self.load_achievements()
    
    def load_achievements(self):
        """Load achievements from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    return {aid: Achievement(**a) for aid, a in data.items()}
            except (json.JSONDecodeError, IOError):
                return self._default_achievements()
        return self._default_achievements()
    
    def _default_achievements(self):
        """Return all achievements in unlocked=False state."""
        return {aid: Achievement(**a.to_dict()) for aid, a in self.ACHIEVEMENTS.items()}
    
    def save_achievements(self):
        """Save achievements to file."""
        data = {aid: a.to_dict() for aid, a in self.achievements.items()}
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement if it exists and isn't already unlocked."""
        if achievement_id in self.achievements and not self.achievements[achievement_id].unlocked:
            self.achievements[achievement_id].unlocked = True
            self.achievements[achievement_id].unlock_date = datetime.now().isoformat()
            self.save_achievements()
            return True
        return False
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements."""
        return [a for a in self.achievements.values() if not a.unlocked]


class WeeklyChallenges:
    """Manage weekly cooking challenges."""
    
    CHALLENGES = [
        {
            "id": "cook_five",
            "name": "🎯 Cook 5 Recipes",
            "description": "Cook 5 different recipes this week",
            "target": 5,
            "reward": "50 points"
        },
        {
            "id": "try_new_cuisine",
            "name": "🌍 Try a New Cuisine",
            "description": "Cook a recipe from a cuisine you haven't tried before",
            "target": 1,
            "reward": "25 points"
        },
        {
            "id": "healthy_week",
            "name": "💪 Healthy Week",
            "description": "Cook 3 vegetarian or vegan recipes",
            "target": 3,
            "reward": "35 points"
        },
    ]
    
    def __init__(self, filename="weekly_challenges.json"):
        self.filename = filename
        self.challenges = self.load_challenges()
    
    def load_challenges(self):
        """Load weekly challenges from file."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._reset_challenges()
        return self._reset_challenges()
    
    def _reset_challenges(self):
        """Reset challenges for the week."""
        week_start = self._get_week_start()
        return {
            "week_start": week_start,
            "challenges": [
                {
                    **challenge,
                    "progress": 0,
                    "completed": False
                }
                for challenge in self.CHALLENGES
            ]
        }
    
    def _get_week_start(self):
        """Get the start date of the current week (Monday)."""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        return week_start.isoformat()
    
    def save_challenges(self):
        """Save challenges to file."""
        with open(self.filename, 'w') as f:
            json.dump(self.challenges, f, indent=2)
    
    def check_week_reset(self):
        """Check if a new week has started and reset if needed."""
        current_week_start = self._get_week_start()
        if self.challenges.get("week_start") != current_week_start:
            self.challenges = self._reset_challenges()
            self.save_challenges()
    
    def update_challenge_progress(self, challenge_id: str, increment: int = 1):
        """Update progress on a challenge."""
        self.check_week_reset()
        for challenge in self.challenges["challenges"]:
            if challenge["id"] == challenge_id and not challenge["completed"]:
                challenge["progress"] += increment
                if challenge["progress"] >= challenge["target"]:
                    challenge["completed"] = True
                self.save_challenges()
                break
    
    def get_active_challenges(self):
        """Get all active challenges for this week."""
        self.check_week_reset()
        return self.challenges["challenges"]
    
    def get_completed_challenges(self):
        """Get completed challenges for this week."""
        return [c for c in self.get_active_challenges() if c["completed"]]
    
    def get_progress_percent(self, challenge_id: str) -> int:
        """Get progress percentage for a challenge."""
        for challenge in self.get_active_challenges():
            if challenge["id"] == challenge_id:
                target = challenge["target"]
                progress = min(challenge["progress"], target)
                return int((progress / target) * 100)
        return 0


class GamificationManager:
    """Central manager for all gamification features."""
    
    def __init__(self):
        self.streak = CookingStreak()
        self.achievements = AchievementTracker()
        self.challenges = WeeklyChallenges()
    
    def record_recipe_cooked(self, recipe_name: str, cuisine: str = None, cooking_time: int = None, is_vegetarian: bool = False, is_vegan: bool = False):
        """
        Record that a recipe was cooked and update all gamification systems.
        
        Args:
            recipe_name: Name of the recipe cooked
            cuisine: Cuisine type (e.g., 'Italian', 'Asian')
            cooking_time: Time taken to cook in minutes
            is_vegetarian: Whether recipe is vegetarian
            is_vegan: Whether recipe is vegan
        """
        # Update streak
        self.streak.record_meal_cooked(
            cuisine=cuisine,
            cooking_time=cooking_time,
            is_vegetarian=is_vegetarian,
            is_vegan=is_vegan
        )
        
        # Unlock achievements
        streak_info = self.streak.get_streak_info()
        if streak_info["total_meals"] == 1:
            self.achievements.unlock_achievement("first_recipe")
        
        if streak_info["current_streak"] >= 7:
            self.achievements.unlock_achievement("week_warrior")
        
        if streak_info["total_meals"] >= 10:
            self.achievements.unlock_achievement("gourmet_chef")
        if streak_info["total_meals"] >= 25:
            self.achievements.unlock_achievement("master_chef")
        if streak_info["total_meals"] >= 50:
            self.achievements.unlock_achievement("culinary_legend")

        streak_data = self.streak.data
        cuisine_counts = streak_data.get("cuisine_counts", {})
        quick_meals = streak_data.get("quick_meals", 0)
        vegetarian_meals = streak_data.get("vegetarian_meals", 0)
        vegan_meals = streak_data.get("vegan_meals", 0)

        if cuisine_counts.get("italian", 0) >= 3:
            self.achievements.unlock_achievement("italian_explorer")

        if cuisine_counts.get("asian", 0) >= 3:
            self.achievements.unlock_achievement("asian_master")

        if cuisine_counts.get("mexican", 0) >= 3:
            self.achievements.unlock_achievement("mexican_fiesta")

        if vegetarian_meals >= 5:
            self.achievements.unlock_achievement("vegetarian_champion")

        if vegan_meals >= 5:
            self.achievements.unlock_achievement("vegan_virtuoso")

        if quick_meals >= 5:
            self.achievements.unlock_achievement("speed_cook")
        
        if is_vegetarian or is_vegan:
            self.challenges.update_challenge_progress("healthy_week")

        if cuisine:
            cuisine_key = cuisine.strip().lower()
            if cuisine_counts.get(cuisine_key, 0) == 1:
                self.challenges.update_challenge_progress("try_new_cuisine")
        
        # Update weekly challenges
        self.challenges.update_challenge_progress("cook_five")
    
    def get_gamification_status(self):
        """Get complete gamification status."""
        return {
            "streak": self.streak.get_streak_info(),
            "achievements": {
                "unlocked": [a.to_dict() for a in self.achievements.get_unlocked_achievements()],
                "locked": [a.to_dict() for a in self.achievements.get_locked_achievements()]
            },
            "challenges": self.challenges.get_active_challenges()
        }
