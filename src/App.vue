<template>
    <div class="h-screen flex">
        <!-- Sidebar -->
        <div class="fixed md:relative bg-[#202123] flex flex-col transition-all duration-200 h-full z-50" 
            :class="{ 
                'w-64': !isSidebarCollapsed || isMobileMenuOpen,
                'w-0 overflow-hidden': isSidebarCollapsed && !isMobileMenuOpen,
                '-translate-x-full md:translate-x-0': !isMobileMenuOpen && isSidebarCollapsed,
                'translate-x-0': isMobileMenuOpen || !isSidebarCollapsed
            }">
            <!-- Sidebar Header -->
            <div class="flex items-center justify-between p-3 border-b border-[#2c2e31]">
                <!-- New Chat Button -->
                <button @click="createNewChat"
                    class="flex-1 flex items-center gap-3 text-[#ECECF1] hover:bg-[#2A2B32] transition-colors rounded-md py-3 px-3">
                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    <span>New chat</span>
                </button>

                <!-- Search Button -->
                <button @click="toggleSearch"
                    class="p-2 text-[#ECECF1] hover:bg-[#2A2B32] rounded-md ml-2">
                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                </button>

                <!-- Close Sidebar Button -->
                <button @click="closeSidebar"
                    class="p-2 text-[#ECECF1] hover:bg-[#2A2B32] rounded-md ml-2">
                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            <!-- Search Input (shown when search is active) -->
            <div v-if="isSearchActive" class="p-3 border-b border-[#2c2e31]">
                <div class="relative flex items-center">
                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4 absolute left-3 text-[#646669]">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input type="text" 
                        v-model="searchQuery" 
                        placeholder="Search chats..."
                        class="w-full bg-[#2A2B32] text-[#ECECF1] placeholder-[#646669] rounded-lg pl-10 pr-3 py-2 focus:outline-none"
                        @blur="handleSearchBlur"
                    />
                </div>
            </div>

            <!-- Chat History -->
            <div class="flex-1 overflow-y-auto">
                <div class="flex flex-col gap-2 text-gray-100 text-sm">
                    <div v-for="group in filteredChatGroups" :key="group.label" class="flex flex-col gap-1">
                        <h3 v-if="!isSidebarCollapsed" class="text-xs text-[#646669] font-medium px-3 pt-3">{{ group.label }}</h3>
                        <div v-for="chat in group.chats" :key="chat.id"
                            class="relative group"
                        >
                            <div @click="switchToChat(chat)"
                                class="py-3 px-3 hover:bg-[#2c2e31] cursor-pointer rounded-md mx-2 text-[#d1d0c5] flex items-center gap-2"
                                :class="{ 'bg-[#2c2e31]': currentChat?.id === chat.id }">
                                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                                </svg>
                                <span v-if="!isSidebarCollapsed" class="flex-1 truncate">{{ chat.title }}</span>
                                <!-- Context Menu Button -->
                                <button v-if="!isSidebarCollapsed" 
                                    @click.stop="openContextMenu(chat)"
                                    class="p-1 text-[#646669] hover:text-[#e2b714] transition-colors opacity-0 group-hover:opacity-100">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                                    </svg>
                                </button>
                            </div>

                            <!-- Context Menu -->
                            <div v-if="activeContextMenu === chat.id && !isSidebarCollapsed"
                                class="absolute right-2 top-10 z-10 bg-[#202123] rounded-md shadow-lg border border-[#2c2e31] py-2 min-w-[140px]">
                                <button @click.stop="shareChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-[#ECECF1] hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                                        <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                        <polyline points="16 6 12 2 8 6"></polyline>
                                        <line x1="12" y1="2" x2="12" y2="15"></line>
                                    </svg>
                                    Share
                                </button>
                                <button @click.stop="startRenameChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-[#ECECF1] hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                                        <path d="M12 20h9"></path>
                                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                                    </svg>
                                    Rename
                                </button>
                                <button @click.stop="archiveChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-[#ECECF1] hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
                                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                                        <line x1="16" y1="2" x2="16" y2="6"></line>
                                        <line x1="8" y1="2" x2="8" y2="6"></line>
                                        <line x1="3" y1="10" x2="21" y2="10"></line>
                                    </svg>
                                    Archive
                                </button>
                                <button @click.stop="deleteChat(chat)" 
                                    class="w-full px-4 py-2 text-left text-red-500 hover:bg-[#2A2B32] flex items-center gap-3">
                                    <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-4 w-4">
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

        <!-- Mobile Menu Overlay -->
        <div v-if="isMobileMenuOpen" 
            class="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            @click="isMobileMenuOpen = false">
        </div>

        <!-- Main Content -->
        <div class="flex-1 flex flex-col bg-[#343541] overflow-hidden w-full">
            <!-- Top Navigation -->
            <div class="h-12 border-b border-[#4E4F60]/20 flex items-center justify-between px-4 bg-[#343541]">
                <!-- Left Side -->
                <div class="flex items-center gap-2">
                    <!-- Menu Button (shown when sidebar is collapsed on desktop) -->
                    <button @click="isSidebarCollapsed = false"
                        v-if="isSidebarCollapsed && !isMobileMenuOpen"
                        class="hidden md:block p-2 text-[#646669] hover:text-[#e2b714] transition-colors rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16m-7 6h7" />
                        </svg>
                    </button>
                    <!-- Mobile Menu Button (only shown on mobile when sidebar is closed) -->
                    <button @click="isMobileMenuOpen = !isMobileMenuOpen"
                        class="md:hidden p-2 hover:bg-[#2A2B32] rounded-md"
                        v-if="!isMobileMenuOpen">
                        <svg stroke="currentColor" fill="none" stroke-width="1.5" viewBox="0 0 24 24" 
                            class="h-6 w-6 text-[#ECECF1]">
                            <line x1="3" y1="12" x2="21" y2="12"></line>
                            <line x1="3" y1="6" x2="21" y2="6"></line>
                            <line x1="3" y1="18" x2="21" y2="18"></line>
                        </svg>
                    </button>
                    <span class="text-[#ECECF1] truncate">{{ currentChat?.title || 'New Chat' }}</span>
                </div>

                <!-- Right Side -->
                <div class="flex items-center gap-2">
                    <!-- Search Button -->
                    <button class="p-2 text-[#ECECF1] hover:bg-[#2A2B32] rounded-md">
                        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-5 w-5">
                            <circle cx="11" cy="11" r="8"></circle>
                            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        </svg>
                    </button>
                    <!-- Edit Button -->
                    <button class="p-2 text-[#ECECF1] hover:bg-[#2A2B32] rounded-md">
                        <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-5 w-5">
                            <path d="M12 20h9"></path>
                            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
                        </svg>
                    </button>
                </div>
            </div>

            <!-- Chat Container -->
            <div class="flex-1 overflow-hidden flex flex-col">
                <!-- Chat Messages -->
                <div class="flex-1 overflow-y-auto">
                    <div v-if="!currentChat || currentChat.messages.length === 0" 
                        class="h-full flex flex-col items-center justify-center p-4">
                        <h1 class="text-2xl md:text-4xl font-semibold text-center text-[#ECECF1] mb-6">
                            What can I help with?
                        </h1>
                    </div>
                    <div v-else v-for="(message, index) in currentChat.messages" :key="index" 
                        class="py-4 px-2 md:px-4">
                        <div class="flex" :class="{ 'justify-end': message.isUser, 'justify-start': !message.isUser }">
                            <!-- Message Content Container -->
                            <div class="flex gap-2 md:gap-4 max-w-[95%] md:max-w-[90%]" 
                                :class="{ 'flex-row-reverse': message.isUser }">
                                <!-- Avatar -->
                                <div class="w-8 h-8 rounded-sm flex items-center justify-center text-sm shrink-0"
                                    :class="{ 'bg-[#e2b714] text-[#323437]': message.isUser, 'bg-[#646669] text-[#d1d0c5]': !message.isUser }">
                                    {{ message.isUser ? 'U' : 'C' }}
                                </div>

                                <!-- Message Content -->
                                <div class="flex-1 min-h-[20px]" :class="{ 'flex justify-end': message.isUser }">
                                    <div class="group relative"
                                        :class="{ 
                                            'bg-[#2c2e31] text-[#d1d0c5] rounded-lg px-4 py-3': message.isUser,
                                            'text-[#d1d0c5]': !message.isUser 
                                        }">
                                        <!-- Message Text -->
                                        <div class="max-h-[450px] overflow-y-auto pr-2 custom-scrollbar">
                                            <p class="whitespace-pre-wrap text-[16px] leading-6">
                                                {{ message.text }}
                                            </p>
                                        </div>
                                        
                                        <!-- Action Buttons - Only for agent messages -->
                                        <div v-if="!message.isUser" class="flex items-center gap-2 mt-4 text-[#646669]">
                                            <button @click="copyMessage(message.text)"
                                                class="flex items-center gap-2 rounded-md hover:bg-[#e2b714] hover:text-[#323437] px-3 py-1 text-xs transition-colors"
                                                :class="{ 'text-[#e2b714]': message.isCopied }">
                                                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>
                                                Copy
                                            </button>
                                            <button @click="regenerateResponse(index)"
                                                class="flex items-center gap-2 rounded-md hover:bg-[#e2b714] hover:text-[#323437] px-3 py-1 text-xs transition-colors">
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

                <!-- Input Area -->
                <div>
                    <div class="max-w-3xl mx-auto p-2 md:p-4">
                        <!-- Attached Files Preview -->
                        <div v-if="attachedFiles.length > 0" class="mb-3">
                            <div class="grid grid-cols-3 gap-2 max-w-xs">
                                <div v-for="(file, index) in attachedFiles" :key="index" 
                                    class="relative group aspect-square bg-[#444654] rounded-md overflow-hidden">
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
                        <form class="w-full">
                            <div class="relative z-[1] flex h-full max-w-full flex-1 flex-col">
                                <div class="group relative z-[1] flex w-full items-center">
                                    <div class="w-full">
                                        <div class="flex w-full cursor-text flex-col overflow-clip rounded-3xl bg-[#303030] shadow-[0_2px_12px_0px_rgba(0,0,0,0.04),_0_9px_9px_0px_rgba(0,0,0,0.01),_0_2px_5px_0px_rgba(0,0,0,0.06)]">
                                            <div class="px-3 py-1">
                                                <div class="flex flex-col justify-start">
                                                    <div class="flex min-h-[44px] items-start pl-1">
                                                        <div class="min-w-0 max-w-full flex-1">
                                                            <textarea 
                                                                v-model="userInput"
                                                                rows="1"
                                                                placeholder="Ask anything"
                                                                class="block h-10 w-full resize-none border-0 bg-transparent px-0 py-2 text-[#d1d0c5] placeholder-[#646669] focus:outline-none focus:ring-0 text-sm md:text-base"
                                                                @input="autoGrow"
                                                                ref="textarea"
                                                            ></textarea>
                                                        </div>
                                                    </div>
                                                </div>
                                                
                                                <div class="mb-2 mt-1 flex items-center justify-between">
                                                    <!-- Left side buttons -->
                                                    <div class="flex gap-x-1.5">
                                                        <!-- Add button with file input -->
                                                        <div class="relative">
                                                            <button @click="triggerFileInput" type="button" class="flex h-9 w-9 items-center justify-center rounded-full border border-[#4E4F60]/20 text-[#646669] hover:bg-[#404040] transition-colors">
                                                                <svg stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" class="h-[18px] w-[18px]">
                                                                    <line x1="12" y1="5" x2="12" y2="19"></line>
                                                                    <line x1="5" y1="12" x2="19" y2="12"></line>
                                                                </svg>
                                                            </button>
                                                            <input 
                                                                type="file" 
                                                                ref="fileInput"
                                                                @change="handleFileUpload" 
                                                                class="hidden"
                                                                accept="image/*"
                                                                multiple
                                                            />
                                                        </div>

                                                        <!-- Globe button -->
                                                        <button class="flex h-9 w-9 items-center justify-center rounded-full border border-[#4E4F60]/20 text-[#646669] hover:bg-[#404040] transition-colors">
                                                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-[18px] w-[18px]">
                                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12ZM11.9851 4.00291C11.9933 4.00046 11.9982 4.00006 11.9996 4C12.001 4.00006 12.0067 4.00046 12.0149 4.00291C12.0256 4.00615 12.047 4.01416 12.079 4.03356C12.2092 4.11248 12.4258 4.32444 12.675 4.77696C12.9161 5.21453 13.1479 5.8046 13.3486 6.53263C13.6852 7.75315 13.9156 9.29169 13.981 11H10.019C10.0844 9.29169 10.3148 7.75315 10.6514 6.53263C10.8521 5.8046 11.0839 5.21453 11.325 4.77696C11.5742 4.32444 11.7908 4.11248 11.921 4.03356C11.953 4.01416 11.9744 4.00615 11.9851 4.00291Z" fill="currentColor"/>
                                                            </svg>
                                                        </button>

                                                        <!-- Reason button -->
                                                        <button class="flex h-9 items-center justify-center rounded-full border border-[#4E4F60]/20 text-[#646669] hover:bg-[#404040] transition-colors px-3">
                                                            <svg fill="none" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="h-[18px] w-[18px]">
                                                                <path d="m12 3c-3.585 0-6.5 2.9225-6.5 6.5385 0 2.2826 1.162 4.2913 2.9248 5.4615h7.1504c1.7628-1.1702 2.9248-3.1789 2.9248-5.4615 0-3.6159-2.915-6.5385-6.5-6.5385z" fill="currentColor"/>
                                                            </svg>
                                                            <span class="ml-1">Reason</span>
                                                        </button>
                                                    </div>

                                                    <!-- Right side button -->
                                                    <div class="flex gap-x-1.5">
                                                        <button 
                                                            @click="sendMessage" 
                                                            :disabled="!canSend"
                                                            class="flex h-9 w-9 items-center justify-center rounded-full bg-black text-white hover:opacity-70 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                                                        >
                                                            <svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-[18px] w-[18px]">
                                                                <path fill-rule="evenodd" clip-rule="evenodd" d="M15.1918 8.90615C15.6381 8.45983 16.3618 8.45983 16.8081 8.90615L21.9509 14.049C22.3972 14.4953 22.3972 15.2189 21.9509 15.6652C21.5046 16.1116 20.781 16.1116 20.3347 15.6652L17.1428 12.4734V22.2857C17.1428 22.9169 16.6311 23.4286 15.9999 23.4286C15.3688 23.4286 14.8571 22.9169 14.8571 22.2857V12.4734L11.6652 15.6652C11.2189 16.1116 10.4953 16.1116 10.049 15.6652C9.60265 15.2189 9.60265 14.4953 10.049 14.049L15.1918 8.90615Z" fill="currentColor"/>
                                                            </svg>
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </form>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue';
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

// Add these to the script setup section
const isSidebarCollapsed = ref(false);
const isSearchActive = ref(false);
const searchQuery = ref('');

const toggleSearch = () => {
    isSearchActive.value = !isSearchActive.value;
    if (isSearchActive.value) {
        // Focus the search input when shown
        nextTick(() => {
            const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
            if (searchInput) searchInput.focus();
        });
    } else {
        searchQuery.value = '';
    }
};

// Add a computed property for filtered chat groups
const filteredChatGroups = computed(() => {
    if (!searchQuery.value) return chatGroups.value;
    
    return chatGroups.value.map(group => ({
        label: group.label,
        chats: group.chats.filter(chat => 
            chat.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            chat.messages.some(msg => msg.text.toLowerCase().includes(searchQuery.value.toLowerCase()))
        )
    })).filter(group => group.chats.length > 0);
});

// Add to script section
const isMobileMenuOpen = ref(false);

// Add this method in the script section after toggleSearch
const handleSearchBlur = () => {
    if (!searchQuery.value) {
        isSearchActive.value = false;
    }
};

// Add this method in the script section after handleSearchBlur
const closeSidebar = () => {
    if (window.innerWidth < 768) { // Mobile
        isMobileMenuOpen.value = false;
    } else { // Desktop
        isSidebarCollapsed.value = true;
    }
};

// Add this method in the script section after handleFileUpload
const triggerFileInput = () => {
    if (fileInput.value) {
        fileInput.value.click();
    }
};

// Add this with other refs at the top of the script
const fileInput = ref<HTMLInputElement | null>(null);
</script>

<style>
@font-face {
    font-family: 'MonoLisa';
    src: url('@/assets/fonts/e11418ac562b8ac1-s.p.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}

@font-face {
    font-family: 'MonoLisa';
    src: url('@/assets/fonts/66f30814ff6d7cdf.p.woff2') format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    font-family: 'MonoLisa', monospace;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    font-feature-settings: "liga" 0;
    letter-spacing: -0.02em;
}

body {
    font-family: 'MonoLisa', monospace;
    background-color: var(--bgPrimary);
    color: var(--textPrimary);
    line-height: 1.6;
    font-size: 16px;
}

/* Heading styles */
h1, h2, h3, h4, h5, h6 {
    font-family: 'MonoLisa', monospace;
    font-weight: 700;
    letter-spacing: -0.03em;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 4px;
    height: 4px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

::-webkit-scrollbar-thumb {
    background: var(--borderPrimary);
    border-radius: 2px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--textTertiary);
}

/* Input and textarea styles */
input, textarea {
    font-family: 'MonoLisa', monospace;
    font-size: 16px;
    line-height: 1.5;
    background-color: var(--bgInput);
    color: var(--textPrimary);
    border: 1px solid var(--borderSecondary);
    border-radius: 4px;
    padding: 12px 16px;
    letter-spacing: -0.02em;
}

input::placeholder, textarea::placeholder {
    color: var(--textTertiary);
}

/* Button styles */
button {
    font-family: 'MonoLisa', monospace;
    font-size: 16px;
    transition: all 0.2s ease;
    letter-spacing: -0.02em;
}

button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Message styles */
.message {
    font-size: 16px;
    line-height: 1.6;
    letter-spacing: -0.02em;
}

/* Code block styles */
pre, code {
    font-family: 'MonoLisa', monospace;
    font-size: 15px;
    line-height: 1.45;
    background-color: var(--bgTertiary);
    border-radius: 4px;
    padding: 0.2em 0.4em;
    letter-spacing: -0.02em;
}

pre code {
    padding: 0;
    background-color: transparent;
}

/* Link styles */
a {
    color: var(--accent);
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: var(--accentHover);
}

/* Mobile styles */
@media (max-width: 768px) {
    body {
        font-size: 15px;
    }

    input, textarea, button {
        font-size: 15px;
    }
}

/* Add these utility classes */
.bg-primary { background-color: var(--bgPrimary); }
.bg-secondary { background-color: var(--bgSecondary); }
.bg-tertiary { background-color: var(--bgTertiary); }
.bg-input { background-color: var(--bgInput); }
.bg-hover { background-color: var(--bgHover); }
.bg-sidebar { background-color: var(--bgSidebar); }
.bg-context-menu { background-color: var(--bgContextMenu); }

.border-primary { border-color: var(--borderPrimary); }
.border-secondary { border-color: var(--borderSecondary); }

.text-primary { color: var(--textPrimary); }
.text-secondary { color: var(--textSecondary); }
.text-tertiary { color: var(--textTertiary); }

.text-accent { color: var(--accent); }
.bg-accent { background-color: var(--accent); }
.hover-bg-accent:hover { background-color: var(--accentHover); }

/* Minutes to launch style */
.minutes-to-launch {
    font-family: 'MonoLisa', monospace;
    font-size: 14px;
    color: var(--textTertiary);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* Quickstart heading style */
.quickstart-heading {
    font-family: 'MonoLisa', monospace;
    font-size: 64px;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--textPrimary);
}

/* Description text style */
.description-text {
    font-family: 'MonoLisa', monospace;
    font-size: 20px;
    line-height: 1.5;
    color: var(--textSecondary);
    letter-spacing: -0.02em;
}
</style>
