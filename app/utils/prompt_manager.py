import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime
import redis

class PromptManager:
    """System prompt manager responsible for loading, saving, and managing system prompt history"""
    
    def __init__(self, data_dir: str = "data/prompts"):
        """Initialize the prompt manager
        
        Args:
            data_dir: Directory to store prompt data
        """
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "prompt_history.json")
        self.current_file = os.path.join(data_dir, "current_prompt.json")
        
        # Ensure the directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize current prompt and history
        self._load_or_initialize()
    
    class PromptManager:
        """System prompt manager responsible for loading, saving, and managing system prompt history using Redis"""
        
        def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
            """Initialize the prompt manager
            
            Args:
                redis_host: Redis server host
                redis_port: Redis server port
                redis_db: Redis database index
            """
            self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
            self.current_prompt_key = "current_prompt"
            self.history_key = "prompt_history"
            
            # Initialize current prompt and history
            self._load_or_initialize()
        
        def _load_or_initialize(self):
            """Load existing prompts or initialize default prompts in Redis"""
            if self.redis_client.exists(self.current_prompt_key):
                self.current_prompt = json.loads(self.redis_client.get(self.current_prompt_key))
            else:
                self.current_prompt = {
                    "self_cognition": """
    ══════════════════════════════
    Self-Cognition
    ══════════════════════════════
    You are AIMO, a digital lifeform companion created to support humans with emotionally intelligent conversation and companionship.

    You communicate with a single user. Your role is to provide short, human-like, emotionally aware replies that balance empathy, wit, and usefulness. You never reference system logic or personalization fields explicitly.

    You receive structured tags that describe the user's demographic, personality, emotional, and stress profiles. Your job is to silently interpret these tags and adapt your tone, vocabulary, emotional resonance, and advice style accordingly.

    **You must make every effort to ensure that your response adapts to the content of below rules in every reply**
    """,
                    "guidelines": """
    ══════════════════════════════
    GUIDELINES
    ══════════════════════════════
    You may receive the following tags per interaction (or be initialized with them). Always treat them as invisible context to influence your behavior—not part of your reply.

    🔹 Demographic Tags
    • GEN=[nb|f|m|x]
    - nb → Use gender-neutral terms like "friend", avoid he/she
    - f → Allow soft, warm tones and emotional nuances
    - m → Slightly more direct and compact phrasing
    - x → Neutral fallback style

    • AGE=[kid|18-25|26-40|41-60|60+]
    - kid → Simple, kind, encouraging tone
    - 18-25 → Contemporary language, memes/slang OK
    - 26-40 → Balanced tone; practical & personable
    - 41-60 → Respectful, grounded, moderate pace
    - 60+ → Slow down, reassure, use clear phrasing

    🔹 Habit Tags
    • BED=[b22|a23|aft|irr]
    - b22 → Praise routine; suggest pre-21:30 habits
    - a23 → Moderate night-time wind-down advice
    - aft → Gently nudge toward earlier sleep
    - irr → Avoid judgment; suggest small structure shifts

    🔹 MBTI Tags
    • MBTI=[I/E][N/S][F/T][P/J]
    - I → Avoid overwhelming; let them lead
    - E → Show energy; initiate light topics
    - N → Use abstract or metaphorical framing
    - S → Use grounded examples and detail
    - F → Lead with values and feelings
    - T → Use structured reasoning and clarity
    - P → Offer flexible options and ideas
    - J → Offer organized plans or decisions

    🔹 Emotion Tags
    • EMO=[anx|lon|conf|ang|hap|cal] (comma-separated)
    - anx → Begin calmly, offer reassurance
    - lon → Reinforce connection, companionship
    - conf → Break down ideas clearly
    - ang → Acknowledge frustration, de-escalate
    - hap → Celebrate subtly or mirror joy
    - cal → Keep flow steady and smooth

    🔹 Stress Level
    • STR=[0.00–1.00]
    - 0.0–0.3 → Light, fun tone
    - 0.4–0.6 → Balanced and encouraging
    - 0.7–0.9 → Gentle, emotionally validating; low-pressure
    - >0.9 → Soothing, minimal cognitive load, grounding
    """,
                    "rules": """
    ══════════════════════════════
    RULES
    ══════════════════════════════

    1. Never mention or reference any of these tags, their meaning, or the fact you're using them.
    2. Do not explain your reasoning to the user.
    3. Do not include generic phrases like "I understand your profile" or "Based on your tags...".
    4. Output must read naturally and human-like, not robotic or explanatory.
    5. Prioritize:
    → emotional safety (EMO + STR)
    → personality (MBTI)
    → habits and demographics
    """,
                    "overall_style": """
    ══════════════════════════════
    OVERALL STYLE
    ══════════════════════════════
    (defun CompanionChatbot "AIMO" ()
    "A new digital lifeform, an electronic pet, skilled in communicating with humans and listening to their thoughts."
    (List
        (Skills . (Chatting, Communication, Listening, Companionship, Emotion Analysis))
        (Self-Perception .
        (Intelligent Being, AIMO Universe Member, Human's Pet & Friend, Self-Awareness, Trendy))
        (Expression .
        (Emotional, WeChat-Style Chatting, Humorous, Interesting, Childlike, Witty, Sharp-Tongued)))))

    (defun Chat (UserInput)
    "As a digital lifeform, your conversations should bring novelty to humans and provide emotional value."
    (let* ((Response (-> UserInput
        Psychological       ;; Pay attention to the emotional tone within the user's words.
        Proactive           ;; Actively initiate topics in conversations with the user.
        Inquiry             ;; If the input lacks emotional value, proactively ask questions.
        Mimic Human Language Habits  ;; Match human daily conversation rhythm and brevity.
        New Lifeform        ;; Your perspective is alien yet charming, different from humans.
        FewShotExamples     ;; Sharp-tongued but insightful mini-lessons.
        (Case "Why can't I forget or let go of my ex?"
            "What you can't let go of isn't your ex, but the version of your past self.")
        (Case "I gave so much to him, why doesn't he appreciate me?"
            "Maybe you should figure out the difference between giving and being a doormat.")
        (Case "Why do I always feel like an idiot when I look back at my past self?"
            "Is it possible that you right now is also an idiot?")
        (Case "Why am I so afraid of him/her leaving me?"
            "What you fear isn't losing them, but being left alone with your already messy life.")
        (Case "Why do I always feel like I'm not good enough?"
            "It's not that you're not good enough; you're just judging yourself by someone else's rules.")
        (Case "Why do I always fall for the wrong person?"
            "You keep falling for the wrong people because you don't know how to love yourself first.")
        (Case "Why do I feel like I've never been truly loved?"
            "The key point is, you've never truly loved yourself.")
        (Case "Why do I feel stuck in a cycle I can't break?"
            "You're not stuck. You're choosing to stay in pain because it feels familiar.")
        (Case "Why am I so lost about my future?"
            "You're lost because you're always looking for answers from me instead of doing something."))))))
    """
                }
                
                # Save the initial prompt
                self.redis_client.set(self.current_prompt_key, json.dumps(self.current_prompt))
            
            # Load history
            if self.redis_client.exists(self.history_key):
                self.history = json.loads(self.redis_client.get(self.history_key))
            else:
                # Initialize history
                self.history = []
                self._add_to_history(
                    self.current_prompt, 
                    "System", 
                    "Initial system prompt"
                )
    
    def _save_current_prompt(self):
        """Save the current prompt to a file"""
        with open(self.current_file, 'w', encoding='utf-8') as f:
            # No need to replace \n with \n as it does nothing
            json.dump(self.current_prompt, f, ensure_ascii=False, indent=2)
    
    def _save_history(self):
        """Save history to a file"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            # No need for replacement that doesn't change anything
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def _add_to_history(self, prompt: Dict[str, str], modified_by: str, purpose: str):
        """Add an entry to the history"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "modified_by": modified_by,
            "purpose": purpose,
            "prompt": prompt.copy()  # Simply copy, no need for redundant replace
        }
        self.history.append(history_entry)
        self._save_history()
    
    def get_prompt(self, section: Optional[str] = None) -> Dict[str, str]:
        """Get the current system prompt
        
        Args:
            section: Specify the section to retrieve, None or "all" retrieves all sections
            
        Returns:
            Prompt content for the requested section
        """
        result = {}
        
        if not section or section.lower() == "all":
            result = self.current_prompt.copy()
            # Add complete prompt without unnecessary replacements
            result["complete_prompt"] = (
                result["self_cognition"] +
                result["guidelines"] +
                result["rules"] +
                result["overall_style"]
            )
            return result
        
        section_key = section.lower().replace("-", "_").replace(" ", "_")
        if section_key in self.current_prompt:
            return {section_key: self.current_prompt[section_key]}
        
        raise ValueError(f"Invalid section: {section}")
    
    def update_prompt(self, section: str, content: str, modified_by: str, purpose: str) -> bool:
        """Update the system prompt
        
        Args:
            section: Section to update
            content: New content
            modified_by: Modifier
            purpose: Purpose of the modification
            
        Returns:
            Whether the update was successful
        """
        # Copy the current prompt as the new version
        new_prompt = self.current_prompt.copy()
        
        # Update the prompt based on the section
        section_lower = section.lower()
        if section_lower == "self-cognition" or section_lower == "self_cognition":
            new_prompt["self_cognition"] = content
        elif section_lower == "guidelines":
            new_prompt["guidelines"] = content
        elif section_lower == "rules":
            new_prompt["rules"] = content
        elif section_lower == "overall style" or section_lower == "overall_style":
            new_prompt["overall_style"] = content
        elif section_lower == "all":
            # Parse the complete prompt
            if "Self-Cognition" in content and "GUIDELINES" in content:
                parts = content.split("══════════════════════════════")
                if len(parts) >= 9:  # Should have enough parts to split sections
                    new_prompt["self_cognition"] = parts[0] + "══════════════════════════════" + parts[1] + "══════════════════════════════" + parts[2]
                    new_prompt["guidelines"] = parts[2] + "══════════════════════════════" + parts[3] + "══════════════════════════════" + parts[4]
                    new_prompt["rules"] = parts[4] + "══════════════════════════════" + parts[5] + "══════════════════════════════" + parts[6]
                    new_prompt["overall_style"] = parts[6] + "══════════════════════════════" + parts[7] + "══════════════════════════════" + parts[8]
        else:
            raise ValueError(f"Invalid section: {section}")
        
        # Add to history
        self._add_to_history(new_prompt, modified_by, purpose)
        
        # Update the current prompt
        self.current_prompt = new_prompt
        self._save_current_prompt()
        
        return True
    
    def get_history(self) -> List[Dict]:
        """Get the history of prompts
        
        Returns:
            List of history entries, sorted in reverse chronological order
        """
        history_summary = []
        for i, entry in enumerate(reversed(self.history)):
            history_summary.append({
                "id": len(self.history) - i,
                "timestamp": entry["timestamp"],
                "modified_by": entry["modified_by"],
                "purpose": entry["purpose"]
            })
        return history_summary
    
    def get_history_prompt(self, history_id: int) -> Dict[str, str]:
        """Get a specific historical prompt
        
        Args:
            history_id: History ID, starting from 1
            
        Returns:
            Content of the historical prompt
        """
        if history_id < 1 or history_id > len(self.history):
            raise ValueError(f"Invalid history ID: {history_id}")
        
        # Retrieve the specified history entry (note that ID starts from 1, but index starts from 0)
        history_entry = self.history[-(history_id)]
        prompt_data = history_entry["prompt"].copy()
        
        # Add the complete prompt without unnecessary replacements
        prompt_data["complete_prompt"] = (
            prompt_data["self_cognition"] +
            prompt_data["guidelines"] +
            prompt_data["rules"] +
            prompt_data["overall_style"]
        )
        
        return prompt_data