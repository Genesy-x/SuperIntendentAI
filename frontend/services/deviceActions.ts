import * as SMS from 'expo-sms';
import * as Contacts from 'expo-contacts';
import * as Camera from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import { Linking, Alert, Platform } from 'react-native';

// Device action types
export type DeviceAction = {
  type: 'sms' | 'call' | 'contacts' | 'camera' | 'music' | 'open_app' | 'none';
  params?: any;
};

export type DeviceActionResult = {
  success: boolean;
  message: string;
  error?: string;
};

/**
 * Parse AI response to detect device control commands
 */
export function parseDeviceAction(aiResponse: string, userMessage: string): DeviceAction {
  const lowerMessage = userMessage.toLowerCase();
  const lowerResponse = aiResponse.toLowerCase();
  
  // SMS/Text message detection
  if (lowerMessage.includes('text') || lowerMessage.includes('message') || lowerMessage.includes('sms')) {
    // Extract phone number and message
    const phoneMatch = userMessage.match(/\d{10,}/);
    if (phoneMatch) {
      return {
        type: 'sms',
        params: {
          phoneNumber: phoneMatch[0],
          message: extractMessageContent(userMessage),
        },
      };
    }
    
    // Check if AI response suggests sending a message
    if (lowerResponse.includes('send') || lowerResponse.includes('text')) {
      return {
        type: 'sms',
        params: {},
      };
    }
  }
  
  // Call detection
  if (lowerMessage.includes('call') && !lowerMessage.includes('called')) {
    const phoneMatch = userMessage.match(/\d{10,}/);
    if (phoneMatch) {
      return {
        type: 'call',
        params: { phoneNumber: phoneMatch[0] },
      };
    }
  }
  
  // Contact search
  if (lowerMessage.includes('contact') || lowerMessage.includes('phone number')) {
    return {
      type: 'contacts',
      params: {},
    };
  }
  
  return { type: 'none' };
}

function extractMessageContent(text: string): string {
  // Try to extract message content after keywords
  const patterns = [
    /(?:text|message|sms).*?"([^"]+)"/i,
    /(?:text|message|sms).*?'([^']+)'/i,
    /(?:say|tell).*?"([^"]+)"/i,
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1];
  }
  
  return '';
}

/**
 * Execute device actions
 */
export async function executeDeviceAction(action: DeviceAction): Promise<DeviceActionResult> {
  try {
    switch (action.type) {
      case 'sms':
        return await sendSMS(action.params);
      
      case 'call':
        return await makeCall(action.params);
      
      case 'contacts':
        return await searchContacts(action.params);
      
      case 'camera':
        return await openCamera(action.params);
      
      case 'music':
        return await openMusic(action.params);
      
      case 'open_app':
        return await openApp(action.params?.url || action.params);
      
      default:
        return {
          success: false,
          message: 'Unknown action type',
        };
    }
  } catch (error: any) {
    return {
      success: false,
      message: 'Action failed',
      error: error.message,
    };
  }
}

/**
 * Send SMS
 */
async function sendSMS(params: { phoneNumber?: string; message?: string }): Promise<DeviceActionResult> {
  try {
    // Check if SMS is available
    const isAvailable = await SMS.isAvailableAsync();
    if (!isAvailable) {
      return {
        success: false,
        message: 'SMS is not available on this device',
      };
    }
    
    const { phoneNumber, message } = params;
    
    if (!phoneNumber) {
      return {
        success: false,
        message: 'Phone number is required',
      };
    }
    
    // Open SMS composer
    const result = await SMS.sendSMSAsync(
      [phoneNumber],
      message || ''
    );
    
    return {
      success: true,
      message: 'SMS composer opened',
    };
  } catch (error: any) {
    return {
      success: false,
      message: 'Failed to open SMS composer',
      error: error.message,
    };
  }
}

/**
 * Make phone call
 */
async function makeCall(params: { phoneNumber: string }): Promise<DeviceActionResult> {
  try {
    const { phoneNumber } = params;
    
    if (!phoneNumber) {
      return {
        success: false,
        message: 'Phone number is required',
      };
    }
    
    const url = `tel:${phoneNumber}`;
    const canOpen = await Linking.canOpenURL(url);
    
    if (!canOpen) {
      return {
        success: false,
        message: 'Cannot make calls on this device',
      };
    }
    
    await Linking.openURL(url);
    
    return {
      success: true,
      message: `Calling ${phoneNumber}`,
    };
  } catch (error: any) {
    return {
      success: false,
      message: 'Failed to initiate call',
      error: error.message,
    };
  }
}

/**
 * Search contacts
 */
async function searchContacts(params: { query?: string }): Promise<DeviceActionResult> {
  try {
    // Request permission
    const { status } = await Contacts.requestPermissionsAsync();
    
    if (status !== 'granted') {
      return {
        success: false,
        message: 'Contacts permission denied',
      };
    }
    
    // Get all contacts
    const { data } = await Contacts.getContactsAsync({
      fields: [Contacts.Fields.PhoneNumbers, Contacts.Fields.Name],
    });
    
    if (data.length > 0) {
      const contactList = data.slice(0, 5).map((contact, index) => {
        const phone = contact.phoneNumbers?.[0]?.number || 'No phone';
        return `${index + 1}. ${contact.name}: ${phone}`;
      }).join('\n');
      
      return {
        success: true,
        message: `Found ${data.length} contacts. First 5:\n${contactList}`,
      };
    }
    
    return {
      success: true,
      message: 'No contacts found',
    };
  } catch (error: any) {
    return {
      success: false,
      message: 'Failed to access contacts',
      error: error.message,
    };
  }
}

/**
 * Open camera
 */
async function openCamera(params: any): Promise<DeviceActionResult> {
  try {
    // Request camera permission
    const { status } = await Camera.Camera.requestCameraPermissionsAsync();
    
    if (status !== 'granted') {
      return {
        success: false,
        message: 'Camera permission denied. Please enable camera access in settings.',
      };
    }
    
    // Note: Opening camera requires navigation to a camera screen
    // For now, we'll just confirm permission is granted
    return {
      success: true,
      message: 'Camera permission granted. Camera feature ready!',
    };
  } catch (error: any) {
    return {
      success: false,
      message: 'Failed to access camera',
      error: error.message,
    };
  }
}

/**
 * Open music apps
 */
async function openMusic(params: { query?: string; app?: string }): Promise<DeviceActionResult> {
  try {
    const { query, app } = params || {};
    
    let url = '';
    
    // Determine which music app to open
    if (app && app.toLowerCase().includes('spotify')) {
      url = query ? `spotify:search:${encodeURIComponent(query)}` : 'spotify:';
    } else if (app && app.toLowerCase().includes('youtube')) {
      url = query 
        ? `vnd.youtube://results?search_query=${encodeURIComponent(query)}`
        : 'vnd.youtube://';
    } else {
      // Default: Try to search on YouTube Music or regular YouTube
      url = query 
        ? `https://music.youtube.com/search?q=${encodeURIComponent(query)}`
        : 'https://music.youtube.com';
    }
    
    const canOpen = await Linking.canOpenURL(url);
    
    if (!canOpen) {
      // Fallback to web URL
      const webUrl = query 
        ? `https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`
        : 'https://www.youtube.com';
      
      await Linking.openURL(webUrl);
      return {
        success: true,
        message: query ? `Searching for "${query}" on YouTube` : 'Opening YouTube',
      };
    }
    
    await Linking.openURL(url);
    
    return {
      success: true,
      message: query ? `Playing "${query}"` : 'Opening music app',
    };
  } catch (error: any) {
    return {
      success: false,
      message: 'Failed to open music app',
      error: error.message,
    };
  }
}

/**
 * Open app by URL scheme (Android/iOS)
 */
export async function openApp(appScheme: string): Promise<DeviceActionResult> {
  try {
    const canOpen = await Linking.canOpenURL(appScheme);
    
    if (!canOpen) {
      return {
        success: false,
        message: `Cannot open ${appScheme}`,
      };
    }
    
    await Linking.openURL(appScheme);
    
    return {
      success: true,
      message: `Opened ${appScheme}`,
    };
  } catch (error: any) {
    return {
      success: false,
      message: 'Failed to open app',
      error: error.message,
    };
  }
}