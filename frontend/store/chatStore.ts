import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { executeDeviceAction, DeviceAction } from '../services/deviceActions';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model_used?: string;
};

type Personality = 'tharos' | 'superintendent';

interface ChatState {
  messages: Message[];
  personality: Personality;
  conversationId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setPersonality: (personality: Personality) => void;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  loadPersistedData: () => Promise<void>;
}

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  personality: 'superintendent',
  conversationId: null,
  isLoading: false,
  error: null,
  
  setPersonality: async (personality: Personality) => {
    set({ personality });
    await AsyncStorage.setItem('personality', personality);
    
    // Call backend to update personality
    try {
      await axios.post(`${API_URL}/api/personality/toggle`, { personality });
    } catch (error) {
      console.error('Error updating personality:', error);
    }
  },
  
  sendMessage: async (message: string) => {
    const { personality, conversationId, messages } = get();
    
    // Add user message immediately
    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    
    set({ 
      messages: [...messages, userMessage],
      isLoading: true,
      error: null 
    });
    
    try {
      const response = await axios.post(`${API_URL}/api/chat`, {
        message,
        personality,
        conversation_id: conversationId,
      });
      
      const { data } = response;
      
      if (data.success) {
        const assistantMessage: Message = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          model_used: data.model_used,
        };
        
        set(state => ({
          messages: [...state.messages, assistantMessage],
          conversationId: data.conversation_id,
          isLoading: false,
        }));
        
        // Persist conversation ID
        await AsyncStorage.setItem('conversationId', data.conversation_id);
        
        // Execute device action if present
        if (data.device_action && data.device_action.action !== 'none') {
          console.log('Executing device action:', data.device_action);
          const result = await executeDeviceAction(data.device_action as DeviceAction);
          console.log('Device action result:', result);
          
          // Optionally add feedback message about action result
          if (!result.success && result.error) {
            const errorMessage: Message = {
              role: 'assistant',
              content: `Device action failed: ${result.message}`,
              timestamp: new Date(),
            };
            set(state => ({
              messages: [...state.messages, errorMessage],
            }));
          }
        }
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      set({ 
        error: error.response?.data?.detail || error.message || 'Failed to send message',
        isLoading: false 
      });
    }
  },
  
  clearMessages: async () => {
    set({ 
      messages: [], 
      conversationId: null,
      error: null 
    });
    await AsyncStorage.removeItem('conversationId');
  },
  
  loadPersistedData: async () => {
    try {
      const [savedPersonality, savedConversationId] = await Promise.all([
        AsyncStorage.getItem('personality'),
        AsyncStorage.getItem('conversationId'),
      ]);
      
      if (savedPersonality) {
        set({ personality: savedPersonality as Personality });
      }
      
      if (savedConversationId) {
        // Load conversation history from backend
        try {
          const response = await axios.get(`${API_URL}/api/conversations/${savedConversationId}`);
          const conversation = response.data;
          
          const loadedMessages: Message[] = conversation.messages.map((msg: any) => ({
            role: msg.role,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            model_used: msg.model_used,
          }));
          
          set({ 
            messages: loadedMessages,
            conversationId: savedConversationId,
            personality: conversation.personality,
          });
        } catch (error) {
          console.error('Error loading conversation:', error);
          // Clear invalid conversation ID
          await AsyncStorage.removeItem('conversationId');
        }
      }
    } catch (error) {
      console.error('Error loading persisted data:', error);
    }
  },
}));