<template>
    <div class="min-h-screen bg-gray-50 py-8">
        <div class="container mx-auto px-4 max-w-4xl">
            <h1 class="text-3xl font-bold text-center text-indigo-900 mb-6">Image to Text Converter</h1>

            <div class="bg-white rounded-lg shadow-lg overflow-hidden">
                <!-- Input Section -->
                <div class="p-6 border-b border-gray-200">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-semibold text-gray-800">Input</h2>
                        <div class="flex items-center gap-2">
                            <select v-model="selectedEngine"
                                class="bg-white border border-gray-300 text-gray-700 py-2 px-3 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                                :disabled="!isEasyOcrAvailable && selectedEngine === 'easyocr'">
                                <option value="tesseract">Tesseract.js</option>
                                <option value="easyocr" :disabled="!isEasyOcrAvailable">
                                    {{ isEasyOcrAvailable ? 'EasyOCR' : 'EasyOCR (Offline)' }}
                                </option>
                            </select>
                            <div v-if="!isEasyOcrAvailable && !checkingServer" class="inline-flex">
                                <button @click="checkServerStatus"
                                    class="text-red-500 hover:text-red-700 transition-colors" title="Retry connecting">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                        stroke-linejoin="round" class="feather feather-refresh-cw">
                                        <polyline points="23 4 23 10 17 10"></polyline>
                                        <polyline points="1 20 1 14 7 14"></polyline>
                                        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15">
                                        </path>
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Paste/Upload Area -->
                    <div class="space-y-4">
                        <div @paste="handlePaste" tabindex="0" ref="pasteArea" @focus="isPasteFocused = true"
                            @blur="isPasteFocused = false" @click="focusPasteArea"
                            class="border-2 border-dashed rounded-lg h-48 flex justify-center items-center cursor-pointer transition-all"
                            :class="{ 'border-indigo-400 ring-2 ring-indigo-200': isPasteFocused, 'border-gray-300': !isPasteFocused }">
                            <div class="text-center text-gray-500">
                                <div class="text-3xl mb-2">📋</div>
                                <p>Paste screenshot (Ctrl+V) or drag & drop images here</p>
                            </div>
                        </div>

                        <!-- Image Grid -->
                        <div v-if="images.length > 0" class="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
                            <div v-for="(image, index) in images" :key="index" 
                                class="relative group border rounded-lg overflow-hidden">
                                <img :src="image.url" alt="Uploaded image" class="w-full h-32 object-cover" />
                                <div class="absolute top-2 right-2 flex gap-2">
                                    <button @click="removeImage(index)"
                                        class="bg-red-500 text-white p-1 rounded-full hover:bg-red-600 transition-colors">
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                                        </svg>
                                    </button>
                                </div>
                                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1">
                                    Image {{ index + 1 }}
                                </div>
                            </div>
                        </div>

                        <div class="flex justify-between items-center">
                            <label
                                class="relative inline-flex items-center justify-center px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg font-medium cursor-pointer hover:bg-indigo-100 transition-colors">
                                <span>Upload Images</span>
                                <input type="file" accept="image/*" @change="handleImageUpload" ref="fileInput"
                                    class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" multiple />
                            </label>

                            <button @click="showOptions = !showOptions"
                                class="flex items-center gap-1 text-gray-600 hover:text-indigo-700 transition-colors"
                                :class="{ 'text-indigo-700': showOptions }">
                                Options
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="transform transition-transform"
                                    :class="{ 'rotate-180': showOptions }">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Collapsible Options Panel -->
                    <div class="overflow-hidden transition-all duration-300 ease-in-out"
                        :class="{ 'max-h-0 opacity-0': !showOptions, 'max-h-96 opacity-100 mt-6': showOptions }">
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Language</label>
                                <select v-model="selectedLanguage"
                                    class="w-full border border-gray-300 rounded-md py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                                    <option value="eng">English</option>
                                    <option value="spa">Spanish</option>
                                    <option value="fra">French</option>
                                    <option value="deu">German</option>
                                    <option value="chi_sim">Chinese</option>
                                    <option value="jpn">Japanese</option>
                                    <option value="kor">Korean</option>
                                    <option value="rus">Russian</option>
                                </select>
                            </div>

                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Recognition Quality</label>
                                <select v-model="recognitionQuality"
                                    class="w-full border border-gray-300 rounded-md py-2 px-3 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                                    <option value="fast">Fast</option>
                                    <option value="standard">Standard</option>
                                    <option value="best">Best</option>
                                </select>
                            </div>

                            <div class="space-y-2">
                                <label class="block text-sm font-medium text-gray-700">Preserve Layout</label>
                                <div class="flex items-center">
                                    <button @click="preserveLayout = !preserveLayout"
                                        class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                                        :class="preserveLayout ? 'bg-indigo-600' : 'bg-gray-200'">
                                        <span class="sr-only">Toggle layout preservation</span>
                                        <span
                                            class="pointer-events-none relative inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
                                            :class="preserveLayout ? 'translate-x-5' : 'translate-x-0'"></span>
                                    </button>
                                    <span class="ml-3 text-sm text-gray-500">{{ preserveLayout ? 'On' : 'Off' }}</span>
                                </div>
                            </div>
                        </div>

                        <div v-if="images.length > 0" class="border-t border-gray-200 pt-4 space-y-2">
                            <p class="text-sm font-medium text-gray-700">Image Processing</p>
                            <div class="flex flex-wrap gap-2">
                                <button @click="applyPreprocessing('grayscale')"
                                    class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition-colors">Grayscale</button>
                                <button @click="applyPreprocessing('contrast')"
                                    class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition-colors">Contrast</button>
                                <button @click="applyPreprocessing('sharpen')"
                                    class="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 text-gray-800 rounded transition-colors">Sharpen</button>
                                <button @click="resetImage"
                                    class="px-3 py-1 text-sm bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors">Reset</button>
                            </div>
                        </div>
                    </div>

                    <button @click="processAllImages" :disabled="images.length === 0 || isProcessing"
                        class="w-full mt-6 py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-md shadow-sm transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed">
                        <div v-if="isProcessing" class="flex justify-center items-center">
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
                                fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                            Processing {{ currentImageIndex + 1 }} of {{ images.length }}...
                        </div>
                        <span v-else>Convert {{ images.length }} {{ images.length === 1 ? 'Image' : 'Images' }} to Text</span>
                    </button>
                </div>

                <!-- Results Section -->
                <div v-if="results.length > 0" class="p-6 bg-gray-50">
                    <div class="flex justify-between items-center mb-4">
                        <h2 class="text-xl font-semibold text-gray-800">Results</h2>
                        <button @click="copyAllResults"
                            class="inline-flex items-center px-4 py-2 rounded-md transition-colors"
                            :class="isCopied ? 'bg-green-100 text-green-800' : 'bg-gray-100 hover:bg-gray-200 text-gray-800'">
                            <svg v-if="isCopied" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M5 13l4 4L19 7" />
                            </svg>
                            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none"
                                viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                            </svg>
                            {{ isCopied ? 'Copied All!' : 'Copy All Results' }}
                        </button>
                    </div>

                    <div v-for="(result, index) in results" :key="index" class="mb-6 last:mb-0">
                        <div class="flex justify-between items-center mb-2">
                            <h3 class="font-medium text-gray-700">Image {{ index + 1 }}</h3>
                            <div v-if="result.confidence > 0" class="px-3 py-1 rounded-full text-xs font-medium" :class="{
                                'bg-green-100 text-green-800': result.confidence >= 0.8,
                                'bg-yellow-100 text-yellow-800': result.confidence >= 0.5 && result.confidence < 0.8,
                                'bg-red-100 text-red-800': result.confidence < 0.5
                            }">
                                {{ Math.round(result.confidence * 100) }}% confidence
                            </div>
                        </div>
                        <div class="bg-white border border-gray-300 rounded-lg">
                            <pre class="p-4 text-sm font-mono text-gray-800 whitespace-pre-wrap break-words max-h-60 overflow-y-auto">{{ result.text }}</pre>
                        </div>
                    </div>

                    <div v-if="errorMessage" class="mt-4 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
                        <div class="flex">
                            <div class="flex-shrink-0">
                                <svg class="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"
                                    fill="currentColor">
                                    <path fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                        clip-rule="evenodd" />
                                </svg>
                            </div>
                            <div class="ml-3">
                                <p class="text-sm text-red-700">{{ errorMessage }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import * as Tesseract from 'tesseract.js';
import { OcrService, type OcrProgress } from '../services/OcrService';
import 'tailwindcss/tailwind.css';

interface ImageItem {
    file: File;
    url: string;
}

interface ResultItem {
    text: string;
    confidence: number;
}

const images = ref<ImageItem[]>([]);
const results = ref<ResultItem[]>([]);
const isProcessing = ref<boolean>(false);
const errorMessage = ref<string>('');
const progress = ref<number>(0);
const processingStatus = ref<string>('Processing image, please wait...');
const fileInput = ref<HTMLInputElement | null>(null);
const pasteArea = ref<HTMLDivElement | null>(null);
const isPasteFocused = ref<boolean>(false);
const isCopied = ref<boolean>(false);
const selectedLanguage = ref<string>('eng');
const recognitionQuality = ref<string>('standard');
const selectedEngine = ref<string>('tesseract');
const isEasyOcrAvailable = ref<boolean>(false);
const checkingServer = ref<boolean>(true);
const preserveLayout = ref<boolean>(true);
const currentImageIndex = ref<number>(0);
const showOptions = ref<boolean>(false);

// Check if EasyOCR server is available
const checkServerStatus = async () => {
    checkingServer.value = true;
    isEasyOcrAvailable.value = await OcrService.isServerAvailable();
    checkingServer.value = false;

    if (!isEasyOcrAvailable.value && selectedEngine.value === 'easyocr') {
        selectedEngine.value = 'tesseract';
    }
};

const handlePaste = (event: ClipboardEvent) => {
    if (event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement) {
        return;
    }

    event.preventDefault();
    const items = event.clipboardData?.items;

    if (!items) return;

    for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
            const blob = items[i].getAsFile();
            if (blob) {
                const url = URL.createObjectURL(blob);
                images.value.push({ file: blob, url });
                break;
            }
        }
    }
};

const handleImageUpload = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target.files) {
        Array.from(target.files).forEach(file => {
            const url = URL.createObjectURL(file);
            images.value.push({ file, url });
        });
    }
};

const removeImage = (index: number) => {
    if (images.value[index]) {
        URL.revokeObjectURL(images.value[index].url);
        images.value.splice(index, 1);
    }
};

const getRecognitionOptions = () => {
    let options: any = {};
    switch (recognitionQuality.value) {
        case 'fast':
            options = { tessedit_pageseg_mode: Tesseract.PSM.SINGLE_BLOCK };
            break;
        case 'best':
            options = { tessedit_pageseg_mode: Tesseract.PSM.SPARSE_TEXT };
            break;
        default:
            options = { tessedit_pageseg_mode: Tesseract.PSM.AUTO };
            break;
    }
    return options;
};

const handleOcrProgress = (ocrProgress: OcrProgress) => {
    progress.value = ocrProgress.progress;
    switch (ocrProgress.status) {
        case 'recognizing':
            processingStatus.value = 'Recognizing text...';
            break;
        case 'uploading':
            processingStatus.value = 'Uploading image to server...';
            break;
        case 'processing':
            processingStatus.value = 'Processing on server...';
            break;
        case 'completed':
            processingStatus.value = 'Finishing up...';
            break;
        default:
            processingStatus.value = `Processing: ${ocrProgress.status}`;
    }
};

const processImage = async (image: ImageItem) => {
    try {
        progress.value = 0;
        let result;

        if (selectedEngine.value === 'easyocr' && isEasyOcrAvailable.value) {
            result = await OcrService.processWithEasyOCR(
                image.file,
                selectedLanguage.value,
                recognitionQuality.value,
                [],
                handleOcrProgress,
                preserveLayout.value
            );
        } else {
            const tesseractOptions = getRecognitionOptions();
            result = await OcrService.processWithTesseract(
                image.url,
                selectedLanguage.value,
                tesseractOptions,
                handleOcrProgress,
                preserveLayout.value
            );
        }

        return {
            text: result.text || 'No text detected',
            confidence: result.confidence / 100
        };
    } catch (error: any) {
        console.error('OCR error:', error);
        throw new Error(error.message || 'Failed to process image');
    }
};

const processAllImages = async () => {
    if (images.value.length === 0) return;

    isProcessing.value = true;
    errorMessage.value = '';
    results.value = [];
    currentImageIndex.value = 0;

    try {
        for (let i = 0; i < images.value.length; i++) {
            currentImageIndex.value = i;
            const result = await processImage(images.value[i]);
            results.value.push(result);
        }
    } catch (error: any) {
        errorMessage.value = error.message;
        if (selectedEngine.value === 'easyocr') {
            await checkServerStatus();
            if (!isEasyOcrAvailable.value) {
                selectedEngine.value = 'tesseract';
            }
        }
    } finally {
        isProcessing.value = false;
        currentImageIndex.value = 0;
    }
};

const copyAllResults = async () => {
    if (results.value.length === 0) return;

    try {
        const text = results.value.map((result, index) => 
            `Image ${index + 1}:\n${result.text}`
        ).join('\n\n');
        
        await navigator.clipboard.writeText(text);
        isCopied.value = true;

        setTimeout(() => {
            isCopied.value = false;
        }, 2000);
    } catch (err) {
        console.error('Failed to copy text: ', err);
        errorMessage.value = 'Failed to copy text to clipboard';
    }
};

const focusPasteArea = () => {
    if (pasteArea.value) {
        pasteArea.value.focus();
    }
};

const applyPreprocessing = async (type: string) => {
    if (images.value.length === 0) return;

    try {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');

            if (!ctx) {
                errorMessage.value = 'Failed to process image: canvas context not available';
                return;
            }

            canvas.width = img.width;
            canvas.height = img.height;

            // Draw original image
            ctx.drawImage(img, 0, 0);

            // Apply filter based on type
            switch (type) {
                case 'grayscale':
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;

                    for (let i = 0; i < data.length; i += 4) {
                        const avg = (data[i] + data[i + 1] + data[i + 2]) / 3;
                        data[i] = avg; // R
                        data[i + 1] = avg; // G
                        data[i + 2] = avg; // B
                    }

                    ctx.putImageData(imageData, 0, 0);
                    break;

                case 'contrast':
                    ctx.filter = 'contrast(180%)';
                    ctx.drawImage(img, 0, 0);
                    break;

                case 'sharpen':
                    // Apply a simple sharpening filter
                    ctx.filter = 'contrast(120%) brightness(120%)';
                    ctx.drawImage(img, 0, 0);
                    break;
            }

            // Convert to blob and update image URL
            canvas.toBlob((blob) => {
                if (blob) {
                    const updatedImage = {
                        file: new File([blob], 'processed-image.png', { type: 'image/png' }),
                        url: URL.createObjectURL(blob)
                    };
                    images.value[currentImageIndex.value] = updatedImage;
                    if (images.value[currentImageIndex.value].url) {
                        URL.revokeObjectURL(images.value[currentImageIndex.value].url);
                    }
                    images.value[currentImageIndex.value].url = URL.createObjectURL(blob);
                }
            }, 'image/png');
        };

        img.src = images.value[currentImageIndex.value].url;
    } catch (error) {
        console.error('Image processing error:', error);
        errorMessage.value = 'Failed to process the image';
    }
};

const resetImage = () => {
    if (images.value.length > 0) {
        images.value.forEach(image => {
            if (image.url) {
                URL.revokeObjectURL(image.url);
            }
        });
        images.value = [];
    }
};

onMounted(() => {
    if (pasteArea.value) {
        pasteArea.value.focus();
    }
    checkServerStatus();
    return () => {
        images.value.forEach(image => URL.revokeObjectURL(image.url));
    };
});
</script>