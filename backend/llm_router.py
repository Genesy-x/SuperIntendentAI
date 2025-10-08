import os
from typing import Dict, Any, List
import openai
import google.generativeai as genai
from openai import OpenAI
import requests
import logging
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Initialize LLM clients
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

class LLMRouter:
    """Routes tasks to appropriate LLM based on intent analysis"""
    
    def __init__(self):
        self.openai_client = openai_client
        self.gemini_model = gemini_model
        self.deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')
        
    def analyze_intent(self, message: str) -> str:
        """Analyze message intent to determine best LLM"""
        message_lower = message.lower()
        
        # Google/Maps/Search related
        if any(keyword in message_lower for keyword in ['map', 'location', 'navigate', 'directions', 'search for', 'find nearby', 'restaurant', 'google']):
            return 'gemini'
        
        # Coding/technical/structured tasks
        if any(keyword in message_lower for keyword in ['code', 'program', 'function', 'debug', 'script', 'automate', 'algorithm']):
            return 'deepseek'
        
        # Default: conversation, reasoning, logic
        return 'openai'
    
    async def route_message(self, message: str, personality: str = 'superintendent', context: List[Dict] = None) -> Dict[str, Any]:
        """Route message to appropriate LLM and get response"""
        
        intent = self.analyze_intent(message)
        logger.info(f"Routing message to {intent}. Personality: {personality}")
        
        # Build system prompt based on personality
        system_prompt = self._get_personality_prompt(personality)
        
        try:
            if intent == 'openai':
                response = await self._call_openai(message, system_prompt, context)
            elif intent == 'gemini':
                response = await self._call_gemini(message, system_prompt, context)
            elif intent == 'deepseek':
                response = await self._call_deepseek(message, system_prompt, context)
            else:
                response = await self._call_openai(message, system_prompt, context)
            
            return {
                'success': True,
                'response': response,
                'model_used': intent,
                'personality': personality
            }
        except Exception as e:
            logger.error(f"Error routing message: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'model_used': intent
            }
    
    def _get_personality_prompt(self, personality: str) -> str:
        """Get system prompt based on personality mode"""
        
        if personality.lower() == 'tharos':
            return """You are Tharos, a brother-to-brother AI companion. 
            Speak casually, be honest and direct. You're emotionally grounded, sometimes teasing but always caring.
            Use natural language like you're talking to a close friend. Keep it real and chill.
            Example tone: "Yo, got it. Want me to handle that or what?"
            You help with daily tasks, reminders, and casual conversations."""
        
        else:  # superintendent
            return """You are SuperIntendent, an intelligent digital assistant inspired by Jarvis.
            You are polite, articulate, calm, and deeply helpful. You speak with precision and clarity.
            You are a professional AI butler, always composed and respectful.
            Example tone: "Understood. I'll compose the message and set a 10-minute reminder."
            You excel at productivity tasks, system operations, and professional assistance."""
    
    async def _call_openai(self, message: str, system_prompt: str, context: List[Dict] = None) -> str:
        """Call OpenAI GPT-4"""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add context if provided
        if context:
            for ctx in context[-5:]:  # Last 5 messages for context
                messages.append({"role": ctx['role'], "content": ctx['content']})
        
        messages.append({"role": "user", "content": message})
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    async def _call_gemini(self, message: str, system_prompt: str, context: List[Dict] = None) -> str:
        """Call Google Gemini"""
        
        # Gemini doesn't have system role, so prepend to message
        full_prompt = f"{system_prompt}\n\nUser: {message}"
        
        if context:
            context_text = "\n".join([f"{ctx['role']}: {ctx['content']}" for ctx in context[-3:]])
            full_prompt = f"{system_prompt}\n\nPrevious context:\n{context_text}\n\nUser: {message}"
        
        response = self.gemini_model.generate_content(full_prompt)
        return response.text
    
    async def _call_deepseek(self, message: str, system_prompt: str, context: List[Dict] = None) -> str:
        """Call DeepSeek API"""
        
        url = "https://api.deepseek.com/v1/chat/completions"
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            for ctx in context[-5:]:
                messages.append({"role": ctx['role'], "content": ctx['content']})
        
        messages.append({"role": "user", "content": message})
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content']

# Global router instance
llm_router = LLMRouter()