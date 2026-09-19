import json
import os
import logging

logger = logging.getLogger("career_service")

class CareerKnowledgeService:
    def __init__(self, json_path="careers.json"):
        self.formatted_knowledge = ""
        self.load_knowledge(json_path)

    def load_knowledge(self, path):
        # Look for careers.json in current dir or src/main/resources/
        possible_paths = [
            path,
            os.path.join(os.path.dirname(__file__), path)
        ]
        
        found = False
        for p in possible_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.formatted_knowledge = json.dumps(data, indent=2)
                        logger.info(f"Loaded {len(data)} career entries from {p}")
                        found = True
                        break
                except Exception as e:
                    logger.error(f"Error loading {p}: {e}")
        
        if not found:
            logger.warning("careers.json knowledge file could not be found.")

    def get_career_context(self) -> str:
        return self.formatted_knowledge
