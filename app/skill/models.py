from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class Skill:
    name: str
    description: str
    instructions: str
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
