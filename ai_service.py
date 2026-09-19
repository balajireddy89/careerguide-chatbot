import os
import logging
import requests

logger = logging.getLogger("ai_service")

class AIService:
    def __init__(self, career_service):
        self.career_service = career_service

    def process_chat_request(self, user_message: str, history: list = None) -> dict:
        if not user_message or not user_message.strip():
            return {
                "response": "Please enter a valid career guidance question.",
                "model": "system",
                "fallbackUsed": False
            }

        # Build prompt payload
        messages = self._build_messages_payload(user_message, history)

        # Primary Configuration
        primary_api_key = os.getenv("PRIMARY_API_KEY", "").strip()
        primary_base_url = os.getenv("PRIMARY_BASE_URL", "https://api.groq.com/openai/v1").strip()
        primary_model_name = os.getenv("PRIMARY_MODEL_NAME", "openai/gpt-oss-20b").strip()

        # Step 1: Try Primary Model
        if primary_api_key:
            logger.info(f"Attempting primary AI model: {primary_model_name}")
            try:
                ai_text = self._call_openai_model(primary_base_url, primary_api_key, primary_model_name, messages)
                if ai_text and ai_text.strip():
                    logger.info(f"Primary AI model ({primary_model_name}) responded successfully.")
                    return {
                        "response": ai_text,
                        "model": primary_model_name,
                        "fallbackUsed": False
                    }
            except Exception as e:
                logger.warning(f"Primary AI model ({primary_model_name}) failed: {e}. Triggering fallback model...")
        else:
            logger.warning("Primary API key is empty. Triggering fallback model...")

        # Fallback Configuration
        fallback_api_key = os.getenv("FALLBACK_API_KEY", "").strip()
        fallback_base_url = os.getenv("FALLBACK_BASE_URL", "https://api.sambanova.ai/v1").strip()
        fallback_model_name = os.getenv("FALLBACK_MODEL_NAME", "Meta-Llama-3.3-70B-Instruct").strip()

        # Step 2: Try Fallback Model
        if fallback_api_key:
            logger.info(f"Attempting fallback AI model: {fallback_model_name}")
            try:
                ai_text = self._call_openai_model(fallback_base_url, fallback_api_key, fallback_model_name, messages)
                if ai_text and ai_text.strip():
                    logger.info(f"Fallback AI model ({fallback_model_name}) responded successfully.")
                    return {
                        "response": ai_text,
                        "model": fallback_model_name,
                        "fallbackUsed": True
                    }
            except Exception as e:
                logger.error(f"Fallback AI model ({fallback_model_name}) failed: {e}")
        else:
            logger.error("Fallback API key is empty.")

        # Step 3: Safety secondary fallback if SambaNova key is exhausted/rate limited
        if primary_api_key:
            backup_model = "openai/gpt-oss-120b"
            logger.info(f"Attempting secondary backup fallback model: {backup_model}")
            try:
                ai_text = self._call_openai_model(primary_base_url, primary_api_key, backup_model, messages)
                if ai_text and ai_text.strip():
                    return {
                        "response": ai_text,
                        "model": backup_model,
                        "fallbackUsed": True
                    }
            except Exception as e:
                logger.error(f"Secondary backup fallback model ({backup_model}) failed: {e}")

        # Step 4: All models failed
        return {
            "response": "Sorry, I'm unable to connect to the AI service right now. Please try again in a moment.",
            "model": "none",
            "fallbackUsed": False
        }

    def _build_messages_payload(self, current_message: str, history: list) -> list:
        career_context = self.career_service.get_career_context()

        system_prompt = f"""You are CareerGuide AI, a student career guidance assistant.

Your purpose is to help students understand technology careers, required skills, learning paths, programming languages, technologies, job roles and beginner-friendly roadmaps.

Give clear, practical and beginner-friendly answers.

When a student asks about a career, explain:
1. What the career is
2. What skills are required
3. What technologies should be learned
4. A beginner learning roadmap
5. Example projects they can build
6. Possible job roles

Use the provided career knowledge when relevant:
{career_context}

Do not claim that one career is universally best for everyone. Career choice depends on the student's interests, strengths, goals and circumstances.

If the student provides their interests or existing skills, use that information to make the guidance more relevant.

Do not provide medical, legal or financial advice.

If a question is unrelated to careers or education, politely explain that you are designed primarily for student career guidance.
"""
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            for item in history:
                role = item.get("role")
                content = item.get("content")
                if role and content:
                    messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": current_message})
        return messages

    def _call_openai_model(self, base_url: str, api_key: str, model_name: str, messages: list) -> str:
        endpoint = base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint += "/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.7
        }

        resp = requests.post(endpoint, json=payload, headers=headers, timeout=20)

        if resp.status_code == 200:
            data = resp.json()
            choices = data.get("choices", [])
            if choices and "message" in choices[0] and "content" in choices[0]["message"]:
                return choices[0]["message"]["content"]
            raise ValueError("API response contained no choice messages")
        else:
            raise RuntimeError(f"HTTP Status {resp.status_code}: {resp.text}")
