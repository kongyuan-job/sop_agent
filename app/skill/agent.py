from typing import List, Optional
from .models import Skill

class Agent:
    def __init__(self, name: str, base_prompt: str = "You are a helpful AI coding assistant."):
        self.name = name
        self.base_prompt = base_prompt
        self.active_skills: List[Skill] = []
        
    def add_skill(self, skill: Skill):
        if skill not in self.active_skills:
            self.active_skills.append(skill)
            
    def remove_skill(self, skill_name: str):
        self.active_skills = [s for s in self.active_skills if s.name != skill_name]
        
    def get_system_prompt(self) -> str:
        prompt = self.base_prompt
        
        if self.active_skills:
            prompt += "\n\nYou have the following additional skills activated:\n"
            for skill in self.active_skills:
                prompt += f"--- SKILL: {skill.name} ---\n"
                prompt += f"{skill.instructions}\n"
                
        return prompt
        
    def chat(self, message: str):
        """
        Simulate sending a message to the agent.
        In a real implementation, this would call an LLM API.
        """
        system_prompt = self.get_system_prompt()
        print(f"DEBUG: System Prompt used:\n{system_prompt}\n")
        print(f"Agent {self.name} received message: {message}")
        return f"Response from {self.name} to: {message}"
