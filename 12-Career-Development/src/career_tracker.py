"""
Career Development Tracker
Tracks skills, goals, and progress
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Skill definition"""
    name: str
    category: str
    proficiency: int  # 1-5 scale
    last_updated: str
    notes: str = ""


@dataclass
class Goal:
    """Career goal definition"""
    title: str
    description: str
    target_date: str
    status: str  # "not_started", "in_progress", "completed"
    progress: int  # 0-100
    milestones: List[str]


@dataclass
class Achievement:
    """Achievement record"""
    title: str
    description: str
    date: str
    category: str
    impact: str


class CareerTracker:
    """Career development tracker"""
    
    def __init__(self, data_file: str = "career_data.json"):
        """
        Initialize career tracker
        
        Args:
            data_file: Path to data file
        """
        self.data_file = Path(data_file)
        self.skills: Dict[str, Skill] = {}
        self.goals: Dict[str, Goal] = {}
        self.achievements: List[Achievement] = []
        self._load_data()
    
    def _load_data(self):
        """Load data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self._deserialize(data)
                logger.info(f"Loaded data from {self.data_file}")
            except Exception as e:
                logger.error(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save data to file"""
        try:
            data = self._serialize()
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved data to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
    
    def _serialize(self) -> Dict[str, Any]:
        """Serialize data to dict"""
        return {
            "skills": {k: asdict(v) for k, v in self.skills.items()},
            "goals": {k: asdict(v) for k, v in self.goals.items()},
            "achievements": [asdict(a) for a in self.achievements]
        }
    
    def _deserialize(self, data: Dict[str, Any]):
        """Deserialize data from dict"""
        if "skills" in data:
            self.skills = {
                k: Skill(**v) for k, v in data["skills"].items()
            }
        if "goals" in data:
            self.goals = {
                k: Goal(**v) for k, v in data["goals"].items()
            }
        if "achievements" in data:
            self.achievements = [
                Achievement(**a) for a in data["achievements"]
            ]
    
    def add_skill(
        self,
        name: str,
        category: str,
        proficiency: int,
        notes: str = ""
    ):
        """
        Add or update skill
        
        Args:
            name: Skill name
            category: Skill category
            proficiency: Proficiency level (1-5)
            notes: Additional notes
        """
        skill = Skill(
            name=name,
            category=category,
            proficiency=proficiency,
            last_updated=datetime.now().isoformat(),
            notes=notes
        )
        self.skills[name] = skill
        self._save_data()
        logger.info(f"Added/updated skill: {name}")
    
    def get_skills_by_category(self, category: str) -> List[Skill]:
        """Get skills by category"""
        return [s for s in self.skills.values() if s.category == category]
    
    def add_goal(
        self,
        goal_id: str,
        title: str,
        description: str,
        target_date: str,
        milestones: List[str] = None
    ):
        """
        Add or update goal
        
        Args:
            goal_id: Unique goal ID
            title: Goal title
            description: Goal description
            target_date: Target completion date
            milestones: List of milestones
        """
        goal = Goal(
            title=title,
            description=description,
            target_date=target_date,
            status="not_started",
            progress=0,
            milestones=milestones or []
        )
        self.goals[goal_id] = goal
        self._save_data()
        logger.info(f"Added/updated goal: {goal_id}")
    
    def update_goal_progress(
        self,
        goal_id: str,
        progress: int,
        status: Optional[str] = None
    ):
        """
        Update goal progress
        
        Args:
            goal_id: Goal ID
            progress: Progress percentage (0-100)
            status: Status (optional)
        """
        if goal_id not in self.goals:
            raise ValueError(f"Goal {goal_id} not found")
        
        self.goals[goal_id].progress = progress
        if status:
            self.goals[goal_id].status = status
        self._save_data()
        logger.info(f"Updated goal {goal_id} progress to {progress}%")
    
    def add_achievement(
        self,
        title: str,
        description: str,
        category: str,
        impact: str
    ):
        """
        Add achievement
        
        Args:
            title: Achievement title
            description: Achievement description
            category: Achievement category
            impact: Impact description
        """
        achievement = Achievement(
            title=title,
            description=description,
            date=datetime.now().isoformat(),
            category=category,
            impact=impact
        )
        self.achievements.append(achievement)
        self._save_data()
        logger.info(f"Added achievement: {title}")
    
    def get_skills_matrix(self) -> Dict[str, List[Skill]]:
        """Get skills organized by category"""
        matrix = {}
        for skill in self.skills.values():
            if skill.category not in matrix:
                matrix[skill.category] = []
            matrix[skill.category].append(skill)
        return matrix
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get overall progress summary"""
        total_goals = len(self.goals)
        completed_goals = sum(1 for g in self.goals.values() if g.status == "completed")
        in_progress_goals = sum(1 for g in self.goals.values() if g.status == "in_progress")
        
        avg_progress = (
            sum(g.progress for g in self.goals.values()) / total_goals
            if total_goals > 0 else 0
        )
        
        return {
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "in_progress_goals": in_progress_goals,
            "average_progress": avg_progress,
            "total_skills": len(self.skills),
            "total_achievements": len(self.achievements)
        }


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    tracker = CareerTracker("career_data.json")
    
    # Add skills
    tracker.add_skill("Python", "Programming", 5, "Expert level")
    tracker.add_skill("GCP", "Cloud", 4, "Certified")
    tracker.add_skill("MLOps", "ML", 3, "Learning")
    
    # Add goals
    tracker.add_goal(
        "get_70l_role",
        "Get ₹70L+ role",
        "Secure senior AI/Data Architect position",
        "2025-12-31",
        ["Complete POCs", "Get certifications", "Apply to roles"]
    )
    
    # Update progress
    tracker.update_goal_progress("get_70l_role", 60, "in_progress")
    
    # Add achievement
    tracker.add_achievement(
        "Completed ML Pipeline POC",
        "Built end-to-end ML pipeline on GCP",
        "Projects",
        "Demonstrated production ML capabilities"
    )
    
    # Get summary
    summary = tracker.get_progress_summary()
    print(f"Progress Summary: {summary}")
    
    print("Career tracking complete!")

