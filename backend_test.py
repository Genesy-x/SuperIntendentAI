#!/usr/bin/env python3
"""
SuperIntendent Backend API Test Suite
Tests all backend endpoints with comprehensive scenarios
"""

import requests
import json
import time
from typing import Dict, Any, Optional
import uuid

# API Configuration
BASE_URL = "https://personal-ai-os.preview.emergentagent.com/api"

class SuperIntendentTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.test_results = []
        self.conversation_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n=== Testing Health Check ===")
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    llm_providers = data.get("llm_providers", {})
                    provider_status = []
                    for provider, status in llm_providers.items():
                        provider_status.append(f"{provider}: {'✅' if status else '❌'}")
                    
                    self.log_test(
                        "Health Check", 
                        True, 
                        f"API healthy, LLM providers: {', '.join(provider_status)}", 
                        data
                    )
                else:
                    self.log_test("Health Check", False, f"Unhealthy status: {data}", data)
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Health Check", False, f"Exception: {str(e)}")
    
    def test_personality_system(self):
        """Test personality toggle and retrieval"""
        print("\n=== Testing Personality System ===")
        
        # Test getting current personality
        try:
            response = self.session.get(f"{self.base_url}/personality")
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_personality", "unknown")
                self.log_test("Get Personality", True, f"Current personality: {current}", data)
            else:
                self.log_test("Get Personality", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Personality", False, f"Exception: {str(e)}")
        
        # Test switching to Tharos
        try:
            payload = {"personality": "tharos"}
            response = self.session.post(f"{self.base_url}/personality/toggle", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("personality") == "tharos":
                    self.log_test("Switch to Tharos", True, f"Successfully switched: {data.get('message')}", data)
                else:
                    self.log_test("Switch to Tharos", False, f"Unexpected response: {data}", data)
            else:
                self.log_test("Switch to Tharos", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Switch to Tharos", False, f"Exception: {str(e)}")
        
        # Test switching to SuperIntendent
        try:
            payload = {"personality": "superintendent"}
            response = self.session.post(f"{self.base_url}/personality/toggle", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("personality") == "superintendent":
                    self.log_test("Switch to SuperIntendent", True, f"Successfully switched: {data.get('message')}", data)
                else:
                    self.log_test("Switch to SuperIntendent", False, f"Unexpected response: {data}", data)
            else:
                self.log_test("Switch to SuperIntendent", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Switch to SuperIntendent", False, f"Exception: {str(e)}")
        
        # Test invalid personality
        try:
            payload = {"personality": "invalid_personality"}
            response = self.session.post(f"{self.base_url}/personality/toggle", json=payload)
            
            if response.status_code == 400:
                self.log_test("Invalid Personality Error", True, "Correctly rejected invalid personality")
            else:
                self.log_test("Invalid Personality Error", False, f"Should return 400, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Personality Error", False, f"Exception: {str(e)}")
    
    def test_chat_with_personalities(self):
        """Test chat functionality with different personalities"""
        print("\n=== Testing Chat with Personalities ===")
        
        # Test chat with SuperIntendent personality
        try:
            payload = {
                "message": "Hello, please help me organize my schedule for tomorrow",
                "personality": "superintendent"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    conv_id = data.get("conversation_id")
                    self.conversation_ids.append(conv_id)
                    model_used = data.get("model_used")
                    personality = data.get("personality")
                    
                    # Check if response has professional tone (SuperIntendent)
                    response_text = data.get("response", "").lower()
                    professional_indicators = ["certainly", "i'll", "assist", "help", "organize", "schedule"]
                    has_professional_tone = any(word in response_text for word in professional_indicators)
                    
                    self.log_test(
                        "Chat SuperIntendent", 
                        True, 
                        f"Response received (model: {model_used}, personality: {personality}, professional tone: {has_professional_tone})", 
                        {"response_length": len(data.get("response", "")), "conversation_id": conv_id}
                    )
                else:
                    self.log_test("Chat SuperIntendent", False, f"Invalid response structure: {data}", data)
            else:
                self.log_test("Chat SuperIntendent", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Chat SuperIntendent", False, f"Exception: {str(e)}")
        
        # Test chat with Tharos personality
        try:
            payload = {
                "message": "Hey, what's up? Can you help me with something quick?",
                "personality": "tharos"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    conv_id = data.get("conversation_id")
                    self.conversation_ids.append(conv_id)
                    model_used = data.get("model_used")
                    personality = data.get("personality")
                    
                    # Check if response has casual tone (Tharos)
                    response_text = data.get("response", "").lower()
                    casual_indicators = ["yo", "hey", "what's", "sure", "yeah", "got it"]
                    has_casual_tone = any(word in response_text for word in casual_indicators)
                    
                    self.log_test(
                        "Chat Tharos", 
                        True, 
                        f"Response received (model: {model_used}, personality: {personality}, casual tone: {has_casual_tone})", 
                        {"response_length": len(data.get("response", "")), "conversation_id": conv_id}
                    )
                else:
                    self.log_test("Chat Tharos", False, f"Invalid response structure: {data}", data)
            else:
                self.log_test("Chat Tharos", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Chat Tharos", False, f"Exception: {str(e)}")
    
    def test_llm_routing(self):
        """Test LLM routing based on intent"""
        print("\n=== Testing LLM Routing ===")
        
        # Test Gemini routing (maps/location intent)
        try:
            payload = {
                "message": "Find a good Italian restaurant nearby",
                "personality": "superintendent"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                model_used = data.get("model_used")
                expected_model = "gemini"
                
                if model_used == expected_model:
                    self.log_test("LLM Routing - Gemini", True, f"Correctly routed to {model_used} for location query")
                else:
                    self.log_test("LLM Routing - Gemini", False, f"Expected {expected_model}, got {model_used}")
                    
                if data.get("conversation_id"):
                    self.conversation_ids.append(data.get("conversation_id"))
            else:
                self.log_test("LLM Routing - Gemini", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("LLM Routing - Gemini", False, f"Exception: {str(e)}")
        
        # Test DeepSeek routing (coding intent)
        try:
            payload = {
                "message": "Write a Python function to calculate fibonacci numbers",
                "personality": "superintendent"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                model_used = data.get("model_used")
                expected_model = "deepseek"
                
                if model_used == expected_model:
                    self.log_test("LLM Routing - DeepSeek", True, f"Correctly routed to {model_used} for coding query")
                else:
                    self.log_test("LLM Routing - DeepSeek", False, f"Expected {expected_model}, got {model_used}")
                    
                if data.get("conversation_id"):
                    self.conversation_ids.append(data.get("conversation_id"))
            else:
                self.log_test("LLM Routing - DeepSeek", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("LLM Routing - DeepSeek", False, f"Exception: {str(e)}")
        
        # Test OpenAI routing (default/conversation intent)
        try:
            payload = {
                "message": "Tell me a funny joke about programming",
                "personality": "tharos"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                model_used = data.get("model_used")
                expected_model = "openai"
                
                if model_used == expected_model:
                    self.log_test("LLM Routing - OpenAI", True, f"Correctly routed to {model_used} for general query")
                else:
                    self.log_test("LLM Routing - OpenAI", False, f"Expected {expected_model}, got {model_used}")
                    
                if data.get("conversation_id"):
                    self.conversation_ids.append(data.get("conversation_id"))
            else:
                self.log_test("LLM Routing - OpenAI", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("LLM Routing - OpenAI", False, f"Exception: {str(e)}")
    
    def test_conversation_history(self):
        """Test conversation history persistence"""
        print("\n=== Testing Conversation History ===")
        
        # Create a new conversation with multiple messages
        conversation_id = None
        
        # First message
        try:
            payload = {
                "message": "Hi, I'm planning a trip to Paris. Can you help me?",
                "personality": "superintendent"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                conversation_id = data.get("conversation_id")
                self.log_test("Conversation Start", True, f"Started conversation: {conversation_id}")
            else:
                self.log_test("Conversation Start", False, f"HTTP {response.status_code}: {response.text}")
                return
        except Exception as e:
            self.log_test("Conversation Start", False, f"Exception: {str(e)}")
            return
        
        # Second message in same conversation
        try:
            payload = {
                "message": "What are the best museums to visit there?",
                "conversation_id": conversation_id,
                "personality": "superintendent"
            }
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                returned_conv_id = data.get("conversation_id")
                if returned_conv_id == conversation_id:
                    self.log_test("Conversation Continue", True, "Successfully continued conversation with context")
                else:
                    self.log_test("Conversation Continue", False, f"Conversation ID mismatch: {returned_conv_id} vs {conversation_id}")
            else:
                self.log_test("Conversation Continue", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Conversation Continue", False, f"Exception: {str(e)}")
        
        # Retrieve conversation history
        if conversation_id:
            try:
                response = self.session.get(f"{self.base_url}/conversations/{conversation_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get("messages", [])
                    if len(messages) >= 4:  # 2 user + 2 assistant messages
                        self.log_test("Get Conversation History", True, f"Retrieved {len(messages)} messages")
                        self.conversation_ids.append(conversation_id)
                    else:
                        self.log_test("Get Conversation History", False, f"Expected at least 4 messages, got {len(messages)}")
                else:
                    self.log_test("Get Conversation History", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test("Get Conversation History", False, f"Exception: {str(e)}")
        
        # Test listing all conversations
        try:
            response = self.session.get(f"{self.base_url}/conversations")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.log_test("List Conversations", True, f"Retrieved {len(data)} conversations")
                else:
                    self.log_test("List Conversations", False, f"Expected list with conversations, got: {type(data)}")
            else:
                self.log_test("List Conversations", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("List Conversations", False, f"Exception: {str(e)}")
    
    def test_memory_system(self):
        """Test memory storage and retrieval"""
        print("\n=== Testing Memory System ===")
        
        # Create a memory
        memory_key = f"test_memory_{int(time.time())}"
        try:
            payload = {
                "key": memory_key,
                "value": "User prefers morning meetings and Italian food",
                "context": "User preferences from conversation"
            }
            response = self.session.post(f"{self.base_url}/memory", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Create Memory", True, f"Created memory with key: {memory_key}")
                else:
                    self.log_test("Create Memory", False, f"Unexpected response: {data}")
            else:
                self.log_test("Create Memory", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Memory", False, f"Exception: {str(e)}")
        
        # Retrieve the memory
        try:
            response = self.session.get(f"{self.base_url}/memory/{memory_key}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("key") == memory_key and data.get("value"):
                    self.log_test("Get Memory", True, f"Retrieved memory: {data.get('value')}")
                else:
                    self.log_test("Get Memory", False, f"Unexpected memory data: {data}")
            else:
                self.log_test("Get Memory", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Memory", False, f"Exception: {str(e)}")
        
        # List all memories
        try:
            response = self.session.get(f"{self.base_url}/memories")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    memory_found = any(mem.get("key") == memory_key for mem in data)
                    if memory_found:
                        self.log_test("List Memories", True, f"Found {len(data)} memories including test memory")
                    else:
                        self.log_test("List Memories", False, f"Test memory not found in list of {len(data)} memories")
                else:
                    self.log_test("List Memories", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("List Memories", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("List Memories", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n=== Testing Error Handling ===")
        
        # Test chat with missing message
        try:
            payload = {"personality": "superintendent"}  # Missing message
            response = self.session.post(f"{self.base_url}/chat", json=payload)
            
            if response.status_code == 422:  # Validation error
                self.log_test("Missing Message Error", True, "Correctly rejected request with missing message")
            else:
                self.log_test("Missing Message Error", False, f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_test("Missing Message Error", False, f"Exception: {str(e)}")
        
        # Test get non-existent conversation
        try:
            fake_id = str(uuid.uuid4())
            response = self.session.get(f"{self.base_url}/conversations/{fake_id}")
            
            if response.status_code == 404:
                self.log_test("Non-existent Conversation", True, "Correctly returned 404 for non-existent conversation")
            else:
                self.log_test("Non-existent Conversation", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Non-existent Conversation", False, f"Exception: {str(e)}")
        
        # Test get non-existent memory
        try:
            fake_key = f"non_existent_key_{int(time.time())}"
            response = self.session.get(f"{self.base_url}/memory/{fake_key}")
            
            if response.status_code == 404:
                self.log_test("Non-existent Memory", True, "Correctly returned 404 for non-existent memory")
            else:
                self.log_test("Non-existent Memory", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Non-existent Memory", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"🚀 Starting SuperIntendent Backend API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)
        
        # Run test suites in order
        self.test_health_check()
        self.test_personality_system()
        self.test_chat_with_personalities()
        self.test_llm_routing()
        self.test_conversation_history()
        self.test_memory_system()
        self.test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print(f"\n🗂️  Created {len(self.conversation_ids)} test conversations")
        
        return {
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed/len(self.test_results)*100,
            "results": self.test_results,
            "conversation_ids": self.conversation_ids
        }

if __name__ == "__main__":
    tester = SuperIntendentTester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        exit(1)
    else:
        print("\n🎉 All tests passed!")
        exit(0)