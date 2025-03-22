<template>
    <div class="chat-container">
        <h1>AI Assistant Chat</h1>

        <div class="chat-card">
            <!-- Chat messages -->
            <div class="chat-messages" ref="messagesContainer">
                <div v-for="(msg, index) in messages" :key="index" class="message"
                    :class="{ 'user-message': msg.role === 'user', 'assistant-message': msg.role === 'assistant', 'system-message': msg.role === 'system' }">
                    <div class="message-role">{{ formatRole(msg.role) }}</div>
                    <div class="message-content">
                        <p>{{ msg.content }}</p>
                    </div>
                    <div v-if="msg.metadata" class="message-metadata">
                        <span>{{ msg.metadata.source === 'api' ? 'Claude API' : 'Local Model' }}</span>
                        <span v-if="msg.metadata.latency"> | {{ msg.metadata.latency }}s</span>
                    </div>
                </div>
                <div v-if="isTyping" class="message assistant-message typing">
                    <div class="message-role">Assistant</div>
                    <div class="message-content typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>

            <!-- Input area -->
            <div class="chat-input-area">
                <textarea v-model="userInput" @keydown.enter.prevent="sendMessage"
                    placeholder="Type your message here..." :disabled="isTyping" class="chat-input" rows="3"></textarea>
                <button @click="sendMessage" class="btn primary send-btn" :disabled="isTyping || !userInput.trim()">
                    <span v-if="isTyping" class="loader small"></span>
                    <span v-else>Send</span>
                </button>
            </div>

            <!-- Settings panel -->
            <div class="chat-settings">
                <button @click="showSettings = !showSettings" class="settings-toggle">
                    ⚙️ Settings
                    <span class="toggle-arrow">{{ showSettings ? '▼' : '►' }}</span>
                </button>

                <div class="settings-panel" v-if="showSettings">
                    <div class="settings-group">
                        <label>Model Source:</label>
                        <div class="radio-group">
                            <label class="radio-label">
                                <input type="radio" v-model="useLocalModel" :value="false" :disabled="!apiAvailable">
                                <span>Claude API</span>
                            </label>
                            <label class="radio-label">
                                <input type="radio" v-model="useLocalModel" :value="true" :disabled="!localAvailable">
                                <span>Local Model</span>
                            </label>
                        </div>
                    </div>

                    <div class="settings-group" v-if="!useLocalModel">
                        <label for="api-key">API Key:</label>
                        <input type="password" id="api-key" v-model="apiKey" placeholder="Enter Claude API key"
                            class="settings-input" />
                        <div class="api-status" :class="{ available: apiAvailable, unavailable: !apiAvailable }">
                            {{ apiAvailable ? 'API Available' : 'API Unavailable' }}
                        </div>
                    </div>

                    <div class="settings-group">
                        <label for="system-message">System Message:</label>
                        <textarea id="system-message" v-model="systemMessage"
                            placeholder="Instructions for the AI assistant..." class="settings-input system-prompt"
                            rows="3"></textarea>
                        <button @click="updateSystemMessage" class="btn secondary update-btn">
                            Update System Message
                        </button>
                    </div>

                    <button @click="resetChat" class="btn warning reset-btn">
                        Reset Chat
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';

interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    metadata?: any;
}

export default defineComponent({
    name: 'ChatApp',
    setup() {
        const messages = ref<ChatMessage[]>([
            { role: 'system', content: 'You are Claude, an AI assistant by Anthropic. Be helpful, harmless, and honest.' }
        ]);
        const userInput = ref('');
        const systemMessage = ref('You are Claude, an AI assistant by Anthropic. Be helpful, harmless, and honest.');
        const isTyping = ref(false);
        const showSettings = ref(false);
        const apiKey = ref('');
        const useLocalModel = ref(false);
        const apiAvailable = ref(false);
        const localAvailable = ref(false);
        const messagesContainer = ref<HTMLElement | null>(null);

        const SERVER_URL = 'http://localhost:5000';

        // Check chat service health on component mount
        onMounted(async () => {
            await checkServiceStatus();

            // Scroll to bottom of messages
            scrollToBottom();
        });

        // Watch messages and scroll to bottom when they change
        watch(messages, () => {
            nextTick(() => {
                scrollToBottom();
            });
        });

        const checkServiceStatus = async () => {
            try {
                const response = await axios.get(`${SERVER_URL}/chat/health`);
                apiAvailable.value = response.data.api_available;
                localAvailable.value = response.data.local_available;

                // Default to API if available, otherwise local if available
                if (!apiAvailable.value && localAvailable.value) {
                    useLocalModel.value = true;
                }

                return response.data;
            } catch (error) {
                console.error('Failed to check chat service status:', error);
                return { api_available: false, local_available: false };
            }
        };

        const formatRole = (role: string) => {
            if (role === 'user') return 'You';
            if (role === 'assistant') return 'Assistant';
            if (role === 'system') return 'System';
            return role;
        };

        const scrollToBottom = () => {
            if (messagesContainer.value) {
                messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
            }
        };

        const sendMessage = async () => {
            const content = userInput.value.trim();
            if (!content || isTyping.value) return;

            // Add user message
            messages.value.push({ role: 'user', content });
            userInput.value = '';
            isTyping.value = true;

            try {
                // Get all messages including system message
                const messageHistory = messages.value.map(({ role, content }) => ({ role, content }));

                // Send request to backend
                const response = await axios.post(`${SERVER_URL}/chat/message`, {
                    messages: messageHistory,
                    api_key: apiKey.value || undefined,
                    use_local: useLocalModel.value
                });

                // Add assistant response
                messages.value.push({
                    role: 'assistant',
                    content: response.data.message,
                    metadata: response.data.metadata
                });
            } catch (error: any) {
                console.error('Failed to get response:', error);
                messages.value.push({
                    role: 'assistant',
                    content: `Sorry, I encountered an error: ${error.response?.data?.error || error.message || 'Unknown error'}`
                });
            } finally {
                isTyping.value = false;
            }
        };

        const updateSystemMessage = () => {
            // Find existing system message
            const systemIndex = messages.value.findIndex(msg => msg.role === 'system');

            if (systemIndex >= 0) {
                // Update existing system message
                messages.value[systemIndex].content = systemMessage.value;
            } else {
                // Add system message at the beginning
                messages.value.unshift({ role: 'system', content: systemMessage.value });
            }
        };

        const resetChat = () => {
            // Keep only the system message
            const systemMsg = messages.value.find(msg => msg.role === 'system');
            messages.value = systemMsg ? [systemMsg] : [];

            // If no system message exists anymore, add default
            if (messages.value.length === 0) {
                messages.value.push({ role: 'system', content: systemMessage.value });
            }
        };

        return {
            messages,
            userInput,
            systemMessage,
            isTyping,
            showSettings,
            apiKey,
            useLocalModel,
            apiAvailable,
            localAvailable,
            messagesContainer,
            formatRole,
            sendMessage,
            updateSystemMessage,
            resetChat,
            scrollToBottom,
            checkServiceStatus
        };
    }
});
</script>

<style scoped>
.chat-container {
    max-width: 800px;
    width: 90%;
    margin: 0 auto;
    padding: 20px 0;
}

h1 {
    text-align: center;
    color: var(--primary-dark);
    margin-bottom: 20px;
    font-weight: 600;
    font-size: 28px;
}

.chat-card {
    background-color: var(--bg-card);
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    display: flex;
    flex-direction: column;
    height: calc(100vh - 150px);
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.message {
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 85%;
    position: relative;
}

.user-message {
    background-color: var(--primary-light);
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

.assistant-message {
    background-color: #f1f3f5;
    color: var(--text-dark);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

.system-message {
    background-color: #fffde7;
    color: #6d4c41;
    align-self: center;
    width: 90%;
    border-radius: 8px;
    border: 1px dashed #ffe082;
}

.message-role {
    font-weight: 600;
    font-size: 12px;
    margin-bottom: 4px;
    opacity: 0.7;
}

.message-content {
    font-size: 15px;
    line-height: 1.5;
    white-space: pre-wrap;
}

.message-metadata {
    font-size: 11px;
    text-align: right;
    opacity: 0.7;
    margin-top: 6px;
}

.chat-input-area {
    padding: 15px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 10px;
    background-color: white;
}

.chat-input {
    flex: 1;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 10px 15px;
    resize: none;
    font-size: 15px;
    outline: none;
    transition: border-color 0.2s;
    font-family: inherit;
}

.chat-input:focus {
    border-color: var(--primary-light);
    box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.1);
}

.send-btn {
    align-self: flex-end;
    padding: 10px 20px;
}

/* Settings panel */
.chat-settings {
    border-top: 1px solid #eee;
    background-color: white;
}

.settings-toggle {
    width: 100%;
    background: none;
    border: none;
    padding: 12px;
    text-align: left;
    font-weight: 500;
    color: var(--text-dark);
    display: flex;
    justify-content: space-between;
    cursor: pointer;
}

.toggle-arrow {
    font-size: 10px;
    opacity: 0.7;
}

.settings-panel {
    padding: 15px;
    border-top: 1px solid #eee;
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.settings-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.radio-group {
    display: flex;
    gap: 15px;
}

.radio-label {
    display: flex;
    align-items: center;
    gap: 5px;
    cursor: pointer;
}

.settings-input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
}

.system-prompt {
    resize: vertical;
    min-height: 60px;
}

.update-btn {
    align-self: flex-start;
    margin-top: 5px;
    background-color: #6c757d;
    color: white;
}

.reset-btn {
    align-self: flex-start;
    background-color: #f44336;
    color: white;
}

.api-status {
    font-size: 12px;
    margin-top: 4px;
}

.api-status.available {
    color: #4caf50;
}

.api-status.unavailable {
    color: #f44336;
}

/* Typing indicator */
.typing-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 5px 0;
}

.typing-indicator span {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #aaa;
    border-radius: 50%;
    animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
    animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-5px);
    }
}

.loader.small {
    width: 12px;
    height: 12px;
    border-width: 2px;
}

.btn.secondary {
    background-color: #6c757d;
    color: white;
}

.btn.warning {
    background-color: #f44336;
    color: white;
}
</style>
