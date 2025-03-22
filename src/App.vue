<template>
    <div class="h-screen flex">
        <!-- Sidebar -->
        <div class="w-64 bg-[#202123] flex flex-col">
            <!-- New Chat Button -->
            <button @click="createNewChat"
                class="m-3 flex py-3 px-3 items-center gap-3 rounded-md hover:bg-[#2A2B32] transition-colors duration-200 text-white cursor-pointer text-sm mb-2 border border-[#4E4F60]/20">
                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                New chat
            </button>

            <!-- Chat History -->
            <div class="flex-1 overflow-y-auto">
                <div class="flex flex-col gap-2 text-gray-100 text-sm">
                    <div v-for="group in chatGroups" :key="group.label" class="flex flex-col gap-1">
                        <h3 class="text-xs text-gray-500 font-medium px-3 pt-3">{{ group.label }}</h3>
                        <div v-for="chat in group.chats" :key="chat.id"
                            class="relative group"
                        >
                            <div @click="switchToChat(chat)"
                                class="py-3 px-3 hover:bg-[#2A2B32] cursor-pointer rounded-md mx-2 text-[#ECECF1] flex items-center gap-2"
                                :class="{ 'bg-[#2A2B32]': currentChat?.id === chat.id }">
                                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                                </svg>
                                {{ chat.title }}
                                
                                <!-- Context Menu Trigger -->
                                <button @click.stop="openContextMenu(chat)" 
                                    class="ml-auto opacity-0 group-hover:opacity-100 hover:text-white p-1 rounded">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                        <circle cx="12" cy="12" r="1"></circle>
                                        <circle cx="12" cy="5" r="1"></circle>
                                        <circle cx="12" cy="19" r="1"></circle>
                                    </svg>
                                </button>
                            </div>

                            <!-- Context Menu -->
                            <div v-if="activeContextMenu === chat.id"
                                class="absolute right-2 top-10 z-10 bg-[#202123] rounded-md shadow-lg border border-gray-700 py-2 min-w-[140px]">
                                <button @click.stop="shareChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-[#ECECF1] hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                        <polyline points="16 6 12 2 8 6"></polyline>
                                        <line x1="12" y1="2" x2="12" y2="15"></line>
                                    </svg>
                                    Share
                                </button>
                                <button @click.stop="startRenameChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-[#ECECF1] hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M12 20h9"></path>
                                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                                    </svg>
                                    Rename
                                </button>
                                <button @click.stop="archiveChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-[#ECECF1] hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                        <line x1="16" y1="2" x2="16" y2="6"></line>
                                        <line x1="8" y1="2" x2="8" y2="6"></line>
                                        <line x1="3" y1="10" x2="21" y2="10"></line>
                                    </svg>
                                    Archive
                                </button>
                                <button @click.stop="deleteChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-red-500 hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg">
                                        <polyline points="3 6 5 6 21 6"></polyline>
                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                    </svg>
                                    Delete
                                </button>
                            </div>
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
                    <span class="text-[#ECECF1]">{{ currentChat?.title || 'New Chat' }}</span>
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
                    <div v-if="!currentChat || currentChat.messages.length === 0" class="h-full flex flex-col items-center justify-center">
                        <h1 class="text-4xl font-semibold text-center text-[#ECECF1] mb-6">What can I help with?</h1>
                    </div>
                    <div v-else v-for="(message, index) in currentChat.messages" :key="index" 
                        :class="{ 'bg-[#343541]': message.isUser, 'bg-[#444654]': !message.isUser }">
                        <div class="max-w-3xl mx-auto px-4 py-6">
                            <div class="flex" :class="{ 'justify-end': message.isUser, 'justify-start': !message.isUser }">
                                <!-- Message Content Container -->
                                <div class="flex gap-4 max-w-[90%]" :class="{ 'flex-row-reverse': message.isUser }">
                                    <!-- Avatar -->
                                    <div class="w-8 h-8 rounded-sm flex items-center justify-center text-sm shrink-0"
                                        :class="{ 'bg-[#5436DA]': message.isUser, 'bg-[#10A37F]': !message.isUser }">
                                        {{ message.isUser ? 'U' : 'C' }}
                                    </div>

                                    <!-- Message Content -->
                                    <div class="flex-1 min-h-[20px]" :class="{ 'flex justify-end': message.isUser }">
                                        <div class="group relative text-[#D1D5DB]"
                                            :class="{ 
                                                'bg-[#19C37D] text-white rounded-2xl px-4 py-3': message.isUser,
                                                'text-[#ECECF1]': !message.isUser 
                                            }">
                                            <!-- Message Text -->
                                            <div class="max-h-[450px] overflow-y-auto pr-2 custom-scrollbar">
                                                <p class="whitespace-pre-wrap text-[16px] leading-6">
                                                    {{ message.text }}
                                                </p>
                                            </div>
                                            
                                            <!-- Edit Button (Top Right) - Only for agent messages -->
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

                                            <!-- Bottom Action Buttons - Only for agent messages -->
                                            <div v-if="!message.isUser" class="flex items-center gap-2 mt-4 text-gray-400">
                                                <button @click="copyMessage(message.text)"
                                                    class="flex items-center gap-2 rounded-md hover:bg-gray-700/50 hover:text-white px-3 py-1 text-xs"
                                                    :class="{ 'text-green-500': message.isCopied }">
                                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
                                                    Copy
                                                </button>
                                                <button @click="regenerateResponse(index)"
                                                    class="flex items-center gap-2 rounded-md hover:bg-gray-700/50 hover:text-white px-3 py-1 text-xs">
                                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4">
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

    <!-- Rename Dialog -->
    <div v-if="isRenaming" 
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-[#202123] rounded-lg shadow-xl w-full max-w-md p-6" @click.stop>
            <h3 class="text-lg font-medium text-[#ECECF1] mb-4">Rename chat</h3>
            <input 
                v-model="newChatTitle"
                type="text"
                class="w-full bg-[#40414F] border border-[#4E4F60]/20 rounded-md px-4 py-2 text-[#ECECF1] focus:outline-none focus:ring-2 focus:ring-[#10A37F]"
                placeholder="Enter new title"
                @keyup.enter="confirmRename"
            />
            <div class="flex justify-end gap-3 mt-6">
                <button 
                    @click="isRenaming = false"
                    class="px-4 py-2 text-[#ECECF1] hover:bg-[#2A2B32] rounded-md">
                    Cancel
                </button>
                <button 
                    @click="confirmRename"
                    class="px-4 py-2 bg-[#10A37F] text-white rounded-md hover:bg-[#1A7F64]">
                    Save
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
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

interface Chat {
    id: string;
    title: string;
    messages: Message[];
    createdAt: Date;
    lastUpdated: Date;
}

interface ChatGroup {
    label: string;
    chats: Chat[];
}

// Reactive state
const userInput = ref('');
const attachedFiles = ref<AttachedFile[]>([]);
const messages = ref<Message[]>([]);
const isProcessing = ref(false);
const textarea = ref<HTMLTextAreaElement | null>(null);
const currentChat = ref<Chat | null>(null);
const chats = ref<Chat[]>([]);
const chatGroups = computed(() => {
    const groups: { [key: string]: Chat[] } = {
        'Today': [],
        'Yesterday': [],
        'Previous 7 Days': [],
        'Previous 30 Days': []
    };

    const now = new Date();
    const yesterday = new Date(now.getTime() - 86400000);
    const last7Days = new Date(now.getTime() - 7 * 86400000);
    const last30Days = new Date(now.getTime() - 30 * 86400000);

    chats.value.forEach(chat => {
        const chatDate = new Date(chat.createdAt);
        if (chatDate.toDateString() === now.toDateString()) {
            groups['Today'].push(chat);
        } else if (chatDate.toDateString() === yesterday.toDateString()) {
            groups['Yesterday'].push(chat);
        } else if (chatDate.getTime() > last7Days.getTime()) {
            groups['Previous 7 Days'].push(chat);
        } else if (chatDate.getTime() > last30Days.getTime()) {
            groups['Previous 30 Days'].push(chat);
        }
    });

    return Object.entries(groups)
        .filter(([_, chats]) => chats.length > 0)
        .map(([label, chats]) => ({
            label,
            chats: chats.sort((a, b) => b.lastUpdated.getTime() - a.lastUpdated.getTime())
        }));
});

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

const createNewChat = () => {
    const newChat: Chat = {
        id: crypto.randomUUID(),
        title: 'New Chat',
        messages: [],
        createdAt: new Date(),
        lastUpdated: new Date()
    };
    chats.value.unshift(newChat);
    currentChat.value = newChat;
    userInput.value = '';
    attachedFiles.value = [];
};

const switchToChat = (chat: Chat) => {
    currentChat.value = chat;
    userInput.value = '';
    attachedFiles.value = [];
};

const sendMessage = async () => {
    if (!canSend.value || isProcessing.value) return;

    isProcessing.value = true;

    try {
        // Create a new chat if none exists
        if (!currentChat.value) {
            const newChat: Chat = {
                id: crypto.randomUUID(),
                title: userInput.value.slice(0, 30) + (userInput.value.length > 30 ? '...' : ''),
                messages: [],
                createdAt: new Date(),
                lastUpdated: new Date()
            };
            chats.value.unshift(newChat);
            currentChat.value = newChat;
        }

        const chat = currentChat.value;

        // Create user message
        const userMessage: Message = {
            text: userInput.value,
            images: attachedFiles.value.map(f => f.url),
            isUser: true,
            timestamp: new Date()
        };

        // Add user message to chat
        chat.messages.push(userMessage);

        // Update chat title if this is the first message
        if (chat.messages.length === 1) {
            chat.title = userInput.value.slice(0, 30) + (userInput.value.length > 30 ? '...' : '');
        }

        // Process images if any
        const processedTexts = await processImages();
        
        // TODO: Send to Claude API
        const prompt = [
            userInput.value,
            ...processedTexts
        ].join('\n\n');

        // Add assistant response
        chat.messages.push({
            text: `Received your message with ${attachedFiles.value.length} images. Here's what I found in the images:\n\n${processedTexts.join('\n\n')}`,
            isUser: false,
            timestamp: new Date()
        });

        // Update chat's last updated time
        chat.lastUpdated = new Date();

        // Clear input and files
        userInput.value = '';
        attachedFiles.value.forEach(file => URL.revokeObjectURL(file.url));
        attachedFiles.value = [];

        if (textarea.value) {
            textarea.value.style.height = 'auto';
        }
    } catch (error) {
        console.error('Failed to send message:', error);
    } finally {
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
    
    // Load chats from localStorage if available
    const savedChats = localStorage.getItem('chats');
    if (savedChats) {
        const parsedChats = JSON.parse(savedChats);
        chats.value = parsedChats.map((chat: any) => ({
            ...chat,
            createdAt: new Date(chat.createdAt),
            lastUpdated: new Date(chat.lastUpdated),
            messages: chat.messages.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
            }))
        }));
    }

    return () => {
        document.removeEventListener('paste', handlePaste);
    };
});

// Add watch to save chats to localStorage
watch(chats, (newChats) => {
    localStorage.setItem('chats', JSON.stringify(newChats));
}, { deep: true });

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

// Add these to the script setup section after the existing interfaces
const activeContextMenu = ref<string | null>(null);
const isRenaming = ref(false);
const newChatTitle = ref('');

// Add these methods after the existing methods
const openContextMenu = (chat: Chat) => {
    activeContextMenu.value = activeContextMenu.value === chat.id ? null : chat.id;
};

const shareChat = (chat: Chat) => {
    // Implement share functionality
    console.log('Share chat:', chat.title);
    activeContextMenu.value = null;
};

const startRenameChat = (chat: Chat) => {
    newChatTitle.value = chat.title;
    isRenaming.value = true;
    activeContextMenu.value = null;
};

const archiveChat = (chat: Chat) => {
    // Implement archive functionality
    console.log('Archive chat:', chat.title);
    activeContextMenu.value = null;
};

const deleteChat = (chat: Chat) => {
    const index = chats.value.findIndex(c => c.id === chat.id);
    if (index !== -1) {
        chats.value.splice(index, 1);
        if (currentChat.value?.id === chat.id) {
            currentChat.value = chats.value[0] || null;
        }
    }
    activeContextMenu.value = null;
};

// Add click outside handler to close context menu
onMounted(() => {
    // ... existing onMounted code ...
    
    document.addEventListener('click', (event) => {
        if (activeContextMenu.value !== null) {
            activeContextMenu.value = null;
        }
        if (isRenaming.value && !(event.target as HTMLElement).closest('.rename-dialog')) {
            isRenaming.value = false;
        }
    });
});

// Add this to the script section after the existing methods
const confirmRename = () => {
    const chat = currentChat.value;
    if (chat && newChatTitle.value.trim()) {
        chat.title = newChatTitle.value.trim();
        isRenaming.value = false;
        newChatTitle.value = '';
    }
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
    border-bottom: 1px solid rgba(32,33,35,0.5);
}

.bg-\[\#343541\] {
    background-color: rgb(52,53,65);
    border-bottom: 1px solid rgba(32,33,35,.5);
}

.bg-\[\#444654\] {
    background-color: rgb(68,70,84);
    border-bottom: 1px solid rgba(32,33,35,.5);
}

/* Improve text colors */
.text-\[\#D1D5DB\] {
    color: rgb(209,213,219);
}

/* Add hover effects for action buttons */
.hover\:bg-gray-700\/50:hover {
    background-color: rgba(55,65,81,0.5);
}

/* Improve scrollbar styling */
.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
    height: 5px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(217,217,227,.8);
    border-radius: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
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
