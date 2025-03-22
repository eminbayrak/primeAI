<template>
    <div class="h-screen flex">
        <!-- Sidebar -->
        <div class="w-64 bg-[#202123] flex flex-col">
            <!-- New Chat Button -->
            <button class="m-3 flex py-3 px-3 items-center gap-3 rounded-md hover:bg-[#2A2B32] transition-colors duration-200 text-white cursor-pointer text-sm mb-2 border border-[#4E4F60]/20">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                New chat
            </button>

            <!-- Chat History -->
            <div class="flex-1 overflow-y-auto">
                <div class="flex flex-col gap-2 text-gray-100 text-sm">
                    <div class="flex flex-col gap-1">
                        <h3 class="text-xs text-gray-500 font-medium px-3 pt-3">Today</h3>
                        <div v-for="(chat, index) in todayChats" :key="index"
                            class="py-3 px-3 hover:bg-[#2A2B32] cursor-pointer rounded-md mx-2 text-[#ECECF1] flex items-center gap-2">
                            <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                            </svg>
                            {{ chat.title }}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 flex flex-col bg-[#343541] overflow-hidden">
            <!-- Top Navigation -->
            <div class="h-12 border-b border-[#4E4F60]/20 flex items-center justify-between px-4 bg-[#343541]">
                <div class="flex items-center gap-2">
                    <!-- Mobile Menu Button -->
                    <button class="md:hidden p-2 hover:bg-[#2A2B32] rounded-md">
                        <svg stroke="currentColor" fill="none" stroke-width="1.5" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-6 w-6 text-[#ECECF1]" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                            <line x1="3" y1="12" x2="21" y2="12"></line>
                            <line x1="3" y1="6" x2="21" y2="6"></line>
                            <line x1="3" y1="18" x2="21" y2="18"></line>
                        </svg>
                    </button>
                    <span class="text-[#ECECF1]">New Chat</span>
                </div>
                <div class="flex items-center gap-2">
                    <button class="p-2 hover:bg-[#2A2B32] rounded-md">
                        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-5 w-5 text-[#ECECF1]" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="1"></circle>
                            <circle cx="19" cy="12" r="1"></circle>
                            <circle cx="5" cy="12" r="1"></circle>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Chat Container -->
            <div class="flex-1 overflow-hidden flex flex-col">
                <!-- Chat Messages -->
                <div class="flex-1 overflow-y-auto">
                    <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center">
                        <h1 class="text-4xl font-semibold text-center text-[#ECECF1] mb-6">What can I help with?</h1>
                    </div>
                    <div v-else v-for="(message, index) in messages" :key="index" 
                        class="border-b border-[#4E4F60]/20"
                        :class="{ 'bg-[#343541]': message.isUser, 'bg-[#444654]': !message.isUser }">
                        <div class="max-w-3xl mx-auto flex gap-4 px-4 py-6">
                            <!-- Avatar -->
                            <div class="w-8 h-8 rounded-sm flex items-center justify-center text-sm shrink-0"
                                :class="{ 'bg-[#5436DA]': message.isUser, 'bg-[#10A37F]': !message.isUser }">
                                {{ message.isUser ? 'U' : 'C' }}
                            </div>
                            <!-- Message Content -->
                            <div class="flex-1 text-[#ECECF1]">
                                <!-- Message Header -->
                                <div v-if="!message.isUser" class="text-[14px] leading-5 mb-1 text-[#8E8EA0]">
                                    Received your message with {{ message.images?.length || 0 }} images. Here's what I found in the images:
                                </div>
                                <!-- Message Text with Actions -->
                                <div class="group relative">
                                    <div class="max-h-[450px] overflow-y-auto pr-10 custom-scrollbar">
                                        <p class="whitespace-pre-wrap text-[16px] leading-6">
                                            <template v-for="(part, idx) in splitTextWithHighlights(message.text)" :key="idx">
                                                <span v-if="part.highlight" class="border-b-2 border-red-500">{{ part.text }}</span>
                                                <span v-else>{{ part.text }}</span>
                                            </template>
                                        </p>
                                    </div>
                                    
                                    <!-- Edit Button (Top Right) -->
                                    <div v-if="!message.isUser" 
                                        class="absolute -top-1 right-0 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button @click="editMessage(index)"
                                            class="p-1.5 text-gray-400 hover:text-[#ECECF1] rounded-md">
                                            <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                                <path d="M12 20h9"></path>
                                                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                                            </svg>
                                        </button>
                                    </div>

                                    <!-- Bottom Action Buttons -->
                                    <div v-if="!message.isUser" class="flex items-center gap-2 mt-4">
                                        <button @click="copyMessage(message.text)"
                                            class="p-1 text-gray-400 hover:text-[#ECECF1] rounded-md flex items-center gap-2 text-sm"
                                            :class="{ 'text-green-500': message.isCopied }">
                                            <svg v-if="message.isCopied" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                                                <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                            </svg>
                                            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                                <path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z" />
                                                <path d="M3 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm12 14a1 1 0 01-1 1H6a1 1 0 01-1-1V6a1 1 0 011-1h8a1 1 0 011 1v13z" />
                                            </svg>
                                            Copy
                                        </button>
                                        <button @click="regenerateResponse(index)"
                                            class="p-1 text-gray-400 hover:text-[#ECECF1] rounded-md flex items-center gap-2 text-sm">
                                            <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                                                <path d="M3 3v5h5"></path>
                                            </svg>
                                            Regenerate
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="border-t border-[#4E4F60]/20 bg-[#343541]">
                    <div class="max-w-3xl mx-auto p-4">
                        <!-- Attached Files Preview -->
                        <div v-if="attachedFiles.length > 0" class="mb-3">
                            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2 max-w-xs">
                                <div v-for="(file, index) in attachedFiles" :key="index" 
                                    class="relative group aspect-square bg-[#444654] rounded-md overflow-hidden border border-[#4E4F60]/20">
                                    <img :src="file.url" alt="Attached file" class="w-full h-full object-cover" />
                                    <button @click="removeFile(index)" 
                                        class="absolute top-1 right-1 bg-[#343541] p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-[#ECECF1]" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Text Input Area -->
                        <div class="relative flex items-end gap-2 bg-[#40414F] rounded-xl shadow-[0_0_15px_rgba(0,0,0,0.1)] border border-[#4E4F60]/20">
                            <div class="flex-1">
                                <textarea 
                                    v-model="userInput"
                                    rows="1"
                                    placeholder="Message ChatGPT..."
                                    class="w-full bg-transparent border-0 resize-none py-4 px-3 text-[#ECECF1] placeholder-[#8E8EA0] focus:outline-none focus:ring-0"
                                    @input="autoGrow"
                                    ref="textarea"
                                ></textarea>
                            </div>

                            <!-- Action Buttons -->
                            <div class="flex items-center gap-2 pr-2">
                                <!-- Attach Button -->
                                <button class="p-2 text-[#8E8EA0] hover:text-[#ECECF1] transition-colors relative">
                                    <input 
                                        type="file" 
                                        @change="handleFileUpload" 
                                        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        accept="image/*"
                                        multiple
                                    />
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M4 5a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V7a2 2 0 00-2-2h-1.586a1 1 0 01-.707-.293l-1.121-1.121A2 2 0 0011.172 3H8.828a2 2 0 00-1.414.586L6.293 4.707A1 1 0 015.586 5H4zm6 9a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
                                    </svg>
                                </button>

                                <!-- Send Button -->
                                <button 
                                    @click="sendMessage"
                                    :disabled="!canSend"
                                    class="p-2 text-[#8E8EA0] hover:text-[#ECECF1] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import * as Tesseract from 'tesseract.js';
import { OcrService } from './services/OcrService';

interface AttachedFile {
    file: File;
    url: string;
}

interface Message {
    text: string;
    images?: string[];
    isUser: boolean;
    timestamp: Date;
    isCopied?: boolean;
}

// Reactive state
const userInput = ref('');
const attachedFiles = ref<AttachedFile[]>([]);
const messages = ref<Message[]>([]);
const isProcessing = ref(false);
const textarea = ref<HTMLTextAreaElement | null>(null);

// Computed properties
const canSend = computed(() => {
    return userInput.value.trim().length > 0 || attachedFiles.value.length > 0;
});

// Methods
const autoGrow = () => {
    if (textarea.value) {
        textarea.value.style.height = 'auto';
        textarea.value.style.height = textarea.value.scrollHeight + 'px';
    }
};

const handleFileUpload = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files) {
        Array.from(target.files).forEach(file => {
            const url = URL.createObjectURL(file);
            attachedFiles.value.push({ file, url });
        });
    }
    // Reset input value to allow selecting the same file again
    target.value = '';
};

const removeFile = (index: number) => {
    URL.revokeObjectURL(attachedFiles.value[index].url);
    attachedFiles.value.splice(index, 1);
};

const processImages = async () => {
    const processedImages: string[] = [];
    for (const file of attachedFiles.value) {
        try {
            const result = await OcrService.processWithTesseract(
                file.url,
                'eng',
                {},
                () => {},
                true
            );
            if (result.text) {
                processedImages.push(result.text);
            }
        } catch (error) {
            console.error('Failed to process image:', error);
        }
    }
    return processedImages;
};

const sendMessage = async () => {
    if (!canSend.value || isProcessing.value) return;

    isProcessing.value = true;
    try {
        // Add user message
        const userMessage: Message = {
            text: userInput.value,
            images: attachedFiles.value.map(f => f.url),
            isUser: true,
            timestamp: new Date()
        };
        messages.value.push(userMessage);

        // Process images if any
        const processedTexts = await processImages();
        
        // TODO: Send to Claude API
        const prompt = [
            userInput.value,
            ...processedTexts
        ].join('\n\n');

        // Simulate Claude response for now
        setTimeout(() => {
            messages.value.push({
                text: `Received your message with ${attachedFiles.value.length} images. Here's what I found in the images:\n\n${processedTexts.join('\n\n')}`,
                isUser: false,
                timestamp: new Date()
            });
            isProcessing.value = false;
        }, 1000);

        // Clear input and files
        userInput.value = '';
        attachedFiles.value.forEach(file => URL.revokeObjectURL(file.url));
        attachedFiles.value = [];

        if (textarea.value) {
            textarea.value.style.height = 'auto';
        }
    } catch (error) {
        console.error('Failed to send message:', error);
        isProcessing.value = false;
    }
};

// Handle paste events
const handlePaste = (event: ClipboardEvent) => {
    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const file = items[i].getAsFile();
            if (file) {
                const url = URL.createObjectURL(file);
                attachedFiles.value.push({ file, url });
            }
        }
    }
};

onMounted(() => {
    document.addEventListener('paste', handlePaste);
    return () => {
        document.removeEventListener('paste', handlePaste);
    };
});

// Add today's chats
const todayChats = ref([
    { title: "Get Tag Release Name" },
    { title: "Using Tag Names in CI" }
]);

const copyMessage = async (text: string) => {
    try {
        await navigator.clipboard.writeText(text);
        // Find the message and set its isCopied state
        const message = messages.value.find(m => m.text === text);
        if (message) {
            message.isCopied = true;
            setTimeout(() => {
                message.isCopied = false;
            }, 2000);
        }
    } catch (err) {
        console.error('Failed to copy text:', err);
    }
};

const editMessage = (index: number) => {
    const message = messages.value[index];
    if (!message.isUser) {
        userInput.value = message.text;
        if (textarea.value) {
            textarea.value.focus();
            autoGrow();
        }
    }
};

const regenerateResponse = (index: number) => {
    // Remove all messages after this index
    messages.value = messages.value.slice(0, index);
    // Trigger a new response
    sendMessage();
};

const splitTextWithHighlights = (text: string) => {
    // This is a placeholder implementation - you should implement your own logic
    // to determine which parts should be highlighted
    const parts = text.split(/(\basdfasdfasdfasfasfa\b|\basdfasdfa\b|\basfasdfasfda\b)/g);
    return parts.map(part => ({
        text: part,
        highlight: /^(asdfasdfasdfasfasfa|asdfasdfa|asfasdfasfda)$/.test(part)
    }));
};
</script>

<style>
:root {
    --primary-color: #10A37F;
    --primary-light: #1A7F64;
    --primary-dark: #0D5D4A;
    --text-light: #ECECF1;
    --text-muted: #8E8EA0;
    --bg-dark: #343541;
    --bg-darker: #444654;
    --border-color: #565869;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-light);
    line-height: 1.6;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}

/* Textarea styles */
textarea {
    min-height: 24px;
    max-height: 200px;
    font-size: 16px;
    line-height: 1.5;
}

/* Message styles */
.message {
    padding: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.message:last-child {
    border-bottom: none;
}

/* Avatar styles */
.avatar {
    width: 30px;
    height: 30px;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 500;
    flex-shrink: 0;
}

/* Button styles */
button {
    transition: all 0.2s ease;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Image preview styles */
.image-preview {
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid var(--border-color);
}

.image-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* Responsive adjustments */
@media (max-width: 640px) {
    .message-content {
        padding: 0.75rem;
    }
    
    .avatar {
        width: 24px;
        height: 24px;
        font-size: 12px;
    }
}

/* Hide scrollbar for Chrome, Safari and Opera */
.overflow-y-auto {
    scrollbar-width: thin;
    scrollbar-color: var(--border-color) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
    width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 20px;
}

/* Prevent text selection on buttons */
button {
    user-select: none;
}

/* Improve textarea appearance */
textarea {
    min-height: 24px;
    max-height: 200px;
}

/* Mobile adjustments */
@media (max-width: 768px) {
    .w-64 {
        display: none;
    }
}

/* Add these new styles */
.group:hover .group-hover\:opacity-100 {
    opacity: 1;
}

.group-hover\:opacity-100 {
    transition: opacity 0.2s ease;
}

/* Custom scrollbar for message content */
.custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: var(--border-color) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
    width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: var(--border-color);
    border-radius: 10px;
}

/* Message text highlighting */
.border-b-2.border-red-500 {
    border-style: solid;
    border-color: rgb(239, 68, 68);
}
</style>
