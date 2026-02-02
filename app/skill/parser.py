import yaml
import re
from pathlib import Path
from .models import Skill

class SkillParser:
    @staticmethod
    def parse(file_path: Path) -> Skill:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Match YAML frontmatter
        match = re.search(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
        if not match:
            raise ValueError(f"Invalid SKILL.md format in {file_path}: Missing frontmatter")
        
        frontmatter_raw = match.group(1)
        instructions = match.group(2).strip()
        
        frontmatter = yaml.safe_load(frontmatter_raw)
        
        if not isinstance(frontmatter, dict):
            raise ValueError(f"Invalid YAML frontmatter in {file_path}")
            
        name = frontmatter.get('name')
        description = frontmatter.get('description')
        version = str(frontmatter.get('version', '1.0.0'))
        
        if not name or not description:
            raise ValueError(f"Missing required fields (name, description) in {file_path}")
            
        return Skill(
            name=name,
            description=description,
            instructions=instructions,
            version=version,
            metadata=frontmatter
        )
