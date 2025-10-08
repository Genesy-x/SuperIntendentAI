from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)

class DeviceActionParser:
    """Parse user messages to detect device control intents"""
    
    @staticmethod
    def parse_message(message: str) -> Dict[str, Any]:
        """
        Parse user message to detect device control commands
        Returns action type and parameters
        """
        message_lower = message.lower()
        
        # SMS/Text message detection
        if any(keyword in message_lower for keyword in ['text', 'message', 'sms', 'send']):
            # Extract phone number
            phone_match = re.search(r'\d{10,}', message)
            phone_number = phone_match.group(0) if phone_match else None
            
            # Extract contact name
            name_match = re.search(r'(?:text|message|sms)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message)
            contact_name = name_match.group(1) if name_match else None
            
            # Extract message content
            message_content = DeviceActionParser._extract_message_content(message)
            
            if phone_number or contact_name:
                return {
                    'action': 'sms',
                    'phone_number': phone_number,
                    'contact_name': contact_name,
                    'message': message_content,
                    'needs_confirmation': True,
                }
        
        # Call detection
        if 'call' in message_lower and 'called' not in message_lower:
            phone_match = re.search(r'\d{10,}', message)
            name_match = re.search(r'call\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message)
            
            if phone_match or name_match:
                return {
                    'action': 'call',
                    'phone_number': phone_match.group(0) if phone_match else None,
                    'contact_name': name_match.group(1) if name_match else None,
                    'needs_confirmation': True,
                }
        
        # Camera
        if any(keyword in message_lower for keyword in ['camera', 'photo', 'picture', 'take a pic']):
            return {
                'action': 'camera',
                'needs_confirmation': False,
            }
        
        # Contacts
        if 'contact' in message_lower or 'phone number' in message_lower:
            name_match = re.search(r'(?:for|of|find)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', message)
            return {
                'action': 'contacts',
                'contact_name': name_match.group(1) if name_match else None,
                'needs_confirmation': False,
            }
        
        # Music
        if any(keyword in message_lower for keyword in ['play music', 'play song', 'open spotify', 'open youtube music']):
            song_match = re.search(r'play\s+(.+?)(?:\s+on|\s+from|$)', message_lower)
            return {
                'action': 'music',
                'query': song_match.group(1) if song_match else None,
                'needs_confirmation': False,
            }
        
        # No device action detected
        return {'action': 'none'}
    
    @staticmethod
    def _extract_message_content(text: str) -> Optional[str]:
        """Extract message content from quotes or after keywords"""
        patterns = [
            r'["\'](.+?)["\']',  # Content in quotes
            r'(?:saying|say|tell them|tell him|tell her)\s+(.+)',  # After keywords
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def generate_confirmation_message(action_data: Dict[str, Any], personality: str) -> str:
        """
        Generate AI response that includes device action confirmation
        """
        action = action_data.get('action')
        
        if personality == 'tharos':
            if action == 'sms':
                contact = action_data.get('contact_name') or action_data.get('phone_number')
                message = action_data.get('message', '')
                return f"Yo, got it! I'll help you text {contact}. Want me to send: '{message}'? Just say yes and I'll open it for you."
            
            elif action == 'call':
                contact = action_data.get('contact_name') or action_data.get('phone_number')
                return f"Alright bro, calling {contact} now. Hold on..."
            
            elif action == 'camera':
                return "Opening the camera for you. Smile!"
            
            elif action == 'contacts':
                return "Let me check your contacts for you..."
            
            elif action == 'music':
                query = action_data.get('query', 'music')
                return f"Yo, playing {query} for you now!"
        
        else:  # superintendent
            if action == 'sms':
                contact = action_data.get('contact_name') or action_data.get('phone_number')
                message = action_data.get('message', '')
                return f"Understood. I will compose a message to {contact}: '{message}'. Shall I proceed?"
            
            elif action == 'call':
                contact = action_data.get('contact_name') or action_data.get('phone_number')
                return f"Initiating call to {contact} now, sir."
            
            elif action == 'camera':
                return "Opening the camera application for you."
            
            elif action == 'contacts':
                return "Accessing your contacts directory..."
            
            elif action == 'music':
                query = action_data.get('query', 'your music')
                return f"Playing {query} for you now."
        
        return ""