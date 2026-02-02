from pathlib import Path
from typing import Dict, List, Optional
from .models import Skill
from .parser import SkillParser

class SkillManager:
    def __init__(self, skills_dir: Path):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        
    def discover_skills(self):
        """Recursively scan for SKILL.md files."""
        if not self.skills_dir.exists():
            return
            
        for skill_file in self.skills_dir.rglob("SKILL.md"):
            try:
                skill = SkillParser.parse(skill_file)
                self.skills[skill.name] = skill
            except Exception as e:
                print(f"Error loading skill from {skill_file}: {e}")
                
    def get_skill(self, name: str) -> Optional[Skill]:
        return self.skills.get(name)
        
    def list_skills(self) -> List[Skill]:
        return list(self.skills.values())
