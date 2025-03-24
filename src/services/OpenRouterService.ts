import axios from 'axios';

const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';
const API_KEY = process.env.VITE_OPENROUTER_API_KEY || import.meta.env?.VITE_OPENROUTER_API_KEY;

if (!API_KEY) {
    throw new Error('OpenRouter API key not found in environment variables. Please add VITE_OPENROUTER_API_KEY to your .env file.');
}

export interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

export class OpenRouterService {
    static async getChatCompletion(messages: Message[]) {
        try {
            console.log('Sending request with messages:', messages);

            const response = await axios.post(
                OPENROUTER_API_URL,
                {
                    model: 'mistralai/mistral-7b-instruct',
                    messages,
                    stream: false,
                    temperature: 0.7,
                    max_tokens: 500,
                },
                {
                    headers: {
                        'Authorization': `Bearer ${API_KEY}`,
                        'HTTP-Referer': window.location.origin,
                        'X-Title': 'Image to Text Chat App',
                        'Content-Type': 'application/json',
                    }
                }
            );

            console.log('API Response:', response.data);

            // Check if response has an error
            if (response.data.error) {
                console.error('API returned error:', response.data.error);
                throw new Error(response.data.error.message || 'API returned an error');
            }

            // Check if response has the expected structure
            if (!response.data) {
                throw new Error('Empty response from OpenRouter API');
            }

            // Extract the message content from the response
            const messageContent = response.data.choices?.[0]?.message?.content;
            if (!messageContent) {
                console.error('Unexpected API response format:', response.data);
                throw new Error('Invalid response format from OpenRouter API');
            }

            return messageContent;
        } catch (error: any) {
            console.error('Error getting chat completion:', error);

            if (error.response?.data?.error) {
                // Handle structured API error response
                const apiError = error.response.data.error;
                console.error('API Error Details:', apiError);
                throw new Error(`API Error: ${apiError.message || 'Unknown API error'}`);
            } else if (error.response) {
                // Handle other API errors
                console.error('API Error Response:', error.response.data);
                const errorMessage = error.response.data?.message || 'Unknown API error';
                throw new Error(`API Error: ${errorMessage}`);
            } else if (error.request) {
                throw new Error('No response received from OpenRouter API');
            } else {
                throw new Error(error.message || 'Failed to process chat completion');
            }
        }
    }
} 