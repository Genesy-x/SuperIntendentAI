import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  SafeAreaView,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { Ionicons } from '@expo/vector-icons';
import { useChatStore } from '../store/chatStore';
import Colors from '../constants/Colors';

export default function Index() {
  const {
    messages,
    personality,
    isLoading,
    error,
    setPersonality,
    sendMessage,
    clearMessages,
    loadPersistedData,
  } = useChatStore();

  const [inputMessage, setInputMessage] = useState('');
  const scrollViewRef = React.useRef<ScrollView>(null);

  useEffect(() => {
    loadPersistedData();
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      await sendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const togglePersonality = () => {
    const newPersonality = personality === 'superintendent' ? 'tharos' : 'superintendent';
    setPersonality(newPersonality);
  };

  const getPersonalityColor = () => {
    return personality === 'tharos' ? Colors.tharos : Colors.superintendent;
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <View style={[styles.statusIndicator, { backgroundColor: getPersonalityColor() }]} />
          <View>
            <Text style={styles.headerTitle}>
              {personality === 'superintendent' ? 'SuperIntendent' : 'Tharos'}
            </Text>
            <Text style={styles.headerSubtitle}>Personal AI Assistant</Text>
          </View>
        </View>
        
        <View style={styles.headerRight}>
          <TouchableOpacity
            style={styles.iconButton}
            onPress={clearMessages}
          >
            <Ionicons name="trash-outline" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.toggleButton, { borderColor: getPersonalityColor() }]}
            onPress={togglePersonality}
          >
            <Ionicons 
              name={personality === 'superintendent' ? 'business-outline' : 'chatbubbles-outline'} 
              size={20} 
              color={getPersonalityColor()} 
            />
          </TouchableOpacity>
        </View>
      </View>

      {/* Messages */}
      <KeyboardAvoidingView
        style={styles.chatContainer}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {messages.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons 
                name={personality === 'superintendent' ? 'shield-checkmark-outline' : 'heart-outline'} 
                size={64} 
                color={Colors.textMuted} 
              />
              <Text style={styles.emptyStateTitle}>
                {personality === 'superintendent' 
                  ? 'SuperIntendent at your service' 
                  : 'Yo what is up'}
              </Text>
              <Text style={styles.emptyStateSubtitle}>
                {personality === 'superintendent'
                  ? 'How may I assist you today'
                  : 'Lets chat bro I got you'}
              </Text>
            </View>
          ) : (
            messages.map((msg, index) => (
              <View
                key={index}
                style={[
                  styles.messageBubble,
                  msg.role === 'user' ? styles.userMessage : styles.assistantMessage,
                ]}
              >
                <Text
                  style={[
                    styles.messageText,
                    msg.role === 'user' ? styles.userMessageText : styles.assistantMessageText,
                  ]}
                >
                  {msg.content}
                </Text>
                {msg.model_used && (
                  <Text style={styles.modelBadge}>
                    {msg.model_used}
                  </Text>
                )}
              </View>
            ))
          )}
          
          {isLoading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color={getPersonalityColor()} />
              <Text style={styles.loadingText}>Thinking...</Text>
            </View>
          )}
          
          {error && (
            <View style={styles.errorContainer}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}
        </ScrollView>

        {/* Input Area */}
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder={
              personality === 'superintendent'
                ? 'How may I assist you?'
                : 'What's on your mind?'
            }
            placeholderTextColor={Colors.textMuted}
            value={inputMessage}
            onChangeText={setInputMessage}
            multiline
            maxLength={500}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              { backgroundColor: inputMessage.trim() ? getPersonalityColor() : Colors.buttonDisabled },
            ]}
            onPress={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
          >
            <Ionicons
              name="send"
              size={20}
              color={inputMessage.trim() ? Colors.background : Colors.textMuted}
            />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: Colors.textPrimary,
  },
  headerSubtitle: {
    fontSize: 12,
    color: Colors.textSecondary,
    marginTop: 2,
  },
  headerRight: {
    flexDirection: 'row',
    gap: 12,
  },
  iconButton: {
    padding: 8,
  },
  toggleButton: {
    padding: 8,
    borderWidth: 1.5,
    borderRadius: 8,
  },
  chatContainer: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 20,
    paddingBottom: 10,
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 100,
  },
  emptyStateTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: Colors.textPrimary,
    marginTop: 16,
  },
  emptyStateSubtitle: {
    fontSize: 14,
    color: Colors.textSecondary,
    marginTop: 8,
  },
  messageBubble: {
    marginBottom: 12,
    padding: 12,
    borderRadius: 16,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: Colors.userMessageBg,
    borderBottomRightRadius: 4,
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    backgroundColor: Colors.assistantMessageBg,
    borderBottomLeftRadius: 4,
    borderLeftWidth: 2,
    borderLeftColor: Colors.gold,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 20,
  },
  userMessageText: {
    color: Colors.textPrimary,
  },
  assistantMessageText: {
    color: Colors.textPrimary,
  },
  modelBadge: {
    fontSize: 10,
    color: Colors.textMuted,
    marginTop: 6,
    fontStyle: 'italic',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    gap: 8,
  },
  loadingText: {
    fontSize: 14,
    color: Colors.textSecondary,
    fontStyle: 'italic',
  },
  errorContainer: {
    padding: 12,
    backgroundColor: Colors.error + '20',
    borderRadius: 8,
    marginTop: 8,
  },
  errorText: {
    fontSize: 13,
    color: Colors.error,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: Colors.surface,
    borderTopWidth: 1,
    borderTopColor: Colors.border,
    gap: 12,
  },
  input: {
    flex: 1,
    backgroundColor: Colors.surfaceElevated,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    paddingTop: 10,
    fontSize: 15,
    color: Colors.textPrimary,
    maxHeight: 100,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
});