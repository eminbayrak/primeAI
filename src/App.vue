<template>
    <div class="app-wrapper min-h-screen bg-[#323437]">
        <!-- Main Content -->
        <main class="py-8">
            <router-view />
        </main>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import * as Tesseract from 'tesseract.js';
import { OcrService, OcrProgress } from './services/OcrService';

export default defineComponent({
    name: 'App',
    setup() {
        const imageUrl = ref<string | null>(null);
        const originalImageUrl = ref<string | null>(null);
        const recognizedText = ref<string>('');
        const isProcessing = ref<boolean>(false);
        const errorMessage = ref<string>('');
        const progress = ref<number>(0);
        const confidence = ref<number>(0);
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
        const imageFile = ref<File | null>(null);
        const originalImageFile = ref<File | null>(null);
        const preserveLayout = ref<boolean>(true);

        // Check if EasyOCR server is available
        const checkServerStatus = async () => {
            checkingServer.value = true;
            isEasyOcrAvailable.value = await OcrService.isServerAvailable();
            checkingServer.value = false;

            // If server went offline, switch to Tesseract
            if (!isEasyOcrAvailable.value && selectedEngine.value === 'easyocr') {
                selectedEngine.value = 'tesseract';
            }
        };

        const triggerFileInput = () => {
            if (fileInput.value) {
                fileInput.value.click();
            }
        };

        const focusPasteArea = () => {
            if (pasteArea.value) {
                pasteArea.value.focus();
            }
        };

        const handlePaste = (event: ClipboardEvent) => {
            // Skip if we're pasting into an input element
            if (
                event.target instanceof HTMLInputElement ||
                event.target instanceof HTMLTextAreaElement
            ) {
                return;
            }

            event.preventDefault();
            const items = event.clipboardData?.items;

            if (!items) return;

            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const blob = items[i].getAsFile();
                    if (blob) {
                        imageFile.value = blob;
                        originalImageFile.value = blob;
                        imageUrl.value = URL.createObjectURL(blob);
                        originalImageUrl.value = imageUrl.value;
                        recognizedText.value = '';
                        errorMessage.value = '';
                        break;
                    }
                }
            }
        };

        const handleImageUpload = (event: Event) => {
            const target = event.target as HTMLInputElement;
            if (target.files && target.files[0]) {
                const file = target.files[0];
                imageFile.value = file;
                originalImageFile.value = file;
                imageUrl.value = URL.createObjectURL(file);
                originalImageUrl.value = imageUrl.value;
                recognizedText.value = '';
                errorMessage.value = '';
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

        const processImage = async () => {
            if (!imageUrl.value || !imageFile.value) return;

            try {
                isProcessing.value = true;
                recognizedText.value = '';
                errorMessage.value = '';
                confidence.value = 0;
                progress.value = 0;

                let result;

                if (selectedEngine.value === 'easyocr' && isEasyOcrAvailable.value) {
                    // Process with EasyOCR server
                    result = await OcrService.processWithEasyOCR(
                        imageFile.value,
                        selectedLanguage.value,
                        recognitionQuality.value,
                        [],
                        handleOcrProgress,
                        preserveLayout.value // Pass the layout preservation preference
                    );
                } else {
                    // Process with Tesseract.js
                    const tesseractOptions = getRecognitionOptions();
                    result = await OcrService.processWithTesseract(
                        imageUrl.value,
                        selectedLanguage.value,
                        tesseractOptions,
                        handleOcrProgress,
                        preserveLayout.value // Pass the layout preservation preference
                    );
                }

                recognizedText.value = result.text;
                confidence.value = result.confidence;

                if (!recognizedText.value.trim()) {
                    errorMessage.value = 'No text detected in the image.';
                }
            } catch (error: any) {
                console.error('OCR error:', error);
                errorMessage.value = `Error: ${error.message || 'Failed to process image'}`;

                // If EasyOCR failed, recheck server and fall back to Tesseract
                if (selectedEngine.value === 'easyocr') {
                    await checkServerStatus();
                    if (!isEasyOcrAvailable.value) {
                        selectedEngine.value = 'tesseract';
                    }
                }
            } finally {
                isProcessing.value = false;
            }
        };

        const copyToClipboard = async () => {
            if (!recognizedText.value) return;

            try {
                await navigator.clipboard.writeText(recognizedText.value);
                isCopied.value = true;

                // Reset the "Copied!" state after 2 seconds
                setTimeout(() => {
                    isCopied.value = false;
                }, 2000);
            } catch (err) {
                console.error('Failed to copy text: ', err);
                errorMessage.value = 'Failed to copy text to clipboard';
            }
        };

        const applyPreprocessing = async (type: string) => {
            if (!originalImageUrl.value || !originalImageFile.value) return;

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
                            imageFile.value = new File([blob], 'processed-image.png', { type: 'image/png' });
                            if (imageUrl.value) {
                                URL.revokeObjectURL(imageUrl.value);
                            }
                            imageUrl.value = URL.createObjectURL(blob);
                        }
                    }, 'image/png');
                };

                img.src = originalImageUrl.value;
            } catch (error) {
                console.error('Image processing error:', error);
                errorMessage.value = 'Failed to process the image';
            }
        };

        const resetImage = () => {
            if (originalImageUrl.value && originalImageFile.value) {
                if (imageUrl.value) {
                    URL.revokeObjectURL(imageUrl.value);
                }
                imageUrl.value = originalImageUrl.value;
                imageFile.value = originalImageFile.value;
            }
        };

        // Allow pasting from anywhere in the app
        onMounted(() => {
            document.addEventListener('paste', handlePaste);

            if (pasteArea.value) {
                pasteArea.value.focus();
            }

            // Check if EasyOCR server is available
            checkServerStatus();

            return () => {
                document.removeEventListener('paste', handlePaste);
            };
        });

        // New reactive states for improved UI
        const showOptions = ref<boolean>(false);

        const getConfidenceClass = (confidence: number) => {
            if (confidence >= 0.8) return 'high';
            if (confidence >= 0.5) return 'medium';
            return 'low';
        };

        return {
            imageUrl,
            recognizedText,
            isProcessing,
            errorMessage,
            progress,
            confidence,
            processingStatus,
            fileInput,
            pasteArea,
            isPasteFocused,
            isCopied,
            selectedLanguage,
            recognitionQuality,
            selectedEngine,
            isEasyOcrAvailable,
            checkingServer,
            handleImageUpload,
            processImage,
            triggerFileInput,
            handlePaste,
            focusPasteArea,
            copyToClipboard,
            applyPreprocessing,
            resetImage,
            checkServerStatus,
            showOptions,
            getConfidenceClass,
            preserveLayout,
        };
    },
});
</script>

<style>
:root {
    --primary-color: #4361ee;
    --primary-light: #4895ef;
    --primary-dark: #3a0ca3;
    --success: #4cc9f0;
    --warning: #f72585;
    --text-dark: #2b2d42;
    --text-light: #8d99ae;
    --bg-light: #f8f9fa;
    --bg-card: #ffffff;
    --border-radius: 8px;
    --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    --transition: all 0.3s ease;
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #323437;
    color: #646669;
    line-height: 1.6;
}

/* App container */
.app-container {
    max-width: 800px;
    width: 90%;
    margin: 0 auto;
    padding: 20px 0;
}

/* Heading styles */
h1 {
    text-align: center;
    color: #e2b714;
    margin-bottom: 20px;
    font-weight: 600;
    font-size: 28px;
}

h2 {
    font-weight: 500;
    font-size: 18px;
    margin: 0;
    color: #e2b714;
}

/* Card styles */
.card {
    background-color: #2c2e31;
    border-radius: var(--border-radius);
    overflow: hidden;
    box-shadow: var(--shadow);
    border: 1px solid #3c3e42;
}

/* Section styles */
.section {
    padding: 20px;
}

.section + .section {
    border-top: 1px solid #3c3e42;
}

/* Button styles */
.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: var(--transition);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background-color: #3c3e42;
    color: #e2b714;
}

.btn:hover {
    background-color: #4c4e52;
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn.primary {
    background-color: #e2b714;
    color: #323437;
}

.btn.primary:hover:not(:disabled) {
    background-color: #f8d03b;
}

/* Form elements */
select {
    width: 100%;
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #3c3e42;
    background-color: #2c2e31;
    color: #e2b714;
    font-size: 14px;
}

/* Text result styles */
.text-result-wrapper {
    position: relative;
    border: 1px solid #3c3e42;
    border-radius: var(--border-radius);
    background-color: #323437;
}

.text-result {
    padding: 16px;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 300px;
    overflow-y: auto;
    margin: 0;
    font-family: 'Consolas', monospace;
    font-size: 14px;
    color: #e2b714;
}

/* Error message styles */
.error-message {
    display: flex;
    align-items: center;
    background-color: rgba(226, 183, 20, 0.1);
    color: #e2b714;
    padding: 12px;
    border-radius: var(--border-radius);
    margin-top: 16px;
}

/* Router link active state */
.router-link-active {
    color: #e2b714;
}

/* Section header */
.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

/* Engine selector */
.engine-selector {
    display: flex;
    align-items: center;
}

/* Server badge */
.server-badge {
    margin-left: 8px;
    font-size: 12px;
    display: flex;
}

.server-badge.offline .retry-btn {
    background: none;
    border: none;
    color: #e2b714;
    cursor: pointer;
    font-size: 16px;
}

/* Paste container */
.paste-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
}

.paste-area {
    border: 2px dashed #3c3e42;
    border-radius: var(--border-radius);
    height: 140px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    transition: var(--transition);
    outline: none;
    background-color: #2c2e31;
    overflow: hidden;
}

.paste-focus {
    border-color: #e2b714;
}

.paste-instructions {
    text-align: center;
    color: #646669;
    max-width: 80%;
}

.paste-icon {
    font-size: 28px;
    margin-bottom: 8px;
}

.preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

/* Upload controls */
.upload-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
}

/* Process button */
.process-btn {
    width: 100%;
    margin-top: 16px;
    padding: 10px;
    font-weight: 500;
}

/* Options toggle */
.options-toggle {
    font-size: 14px;
    color: #646669;
    cursor: pointer;
    display: flex;
    align-items: center;
    margin-left: auto;
    transition: var(--transition);
}

.options-toggle:hover {
    color: #e2b714;
}

.options-toggle.active {
    color: #e2b714;
}

.toggle-icon {
    margin-left: 4px;
    font-size: 10px;
}

/* Options panel */
.options-panel {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out;
}

.options-panel.visible {
    max-height: 200px;
    margin-top: 16px;
    margin-bottom: 16px;
}

.options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}

.option-item label {
    display: block;
    font-size: 14px;
    margin-bottom: 4px;
    color: #646669;
}

/* Image processing */
.image-processing {
    margin-top: 12px;
    border-top: 1px solid #3c3e42;
    padding-top: 12px;
}

.processing-label {
    font-size: 14px;
    color: #646669;
    margin-bottom: 6px;
}

.processing-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.image-btn {
    font-size: 12px;
    padding: 4px 10px;
    background-color: #3c3e42;
    color: #e2b714;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: var(--transition);
}

.image-btn:hover {
    background-color: #4c4e52;
}

.image-btn.reset {
    color: #e2b714;
}

/* Result section */
.result-section {
    background-color: #2c2e31;
}

.confidence-badge {
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 12px;
    font-weight: 500;
}

.confidence-badge.high {
    background-color: rgba(226, 183, 20, 0.2);
    color: #e2b714;
}

.confidence-badge.medium {
    background-color: rgba(226, 183, 20, 0.2);
    color: #e2b714;
}

.confidence-badge.low {
    background-color: rgba(226, 183, 20, 0.2);
    color: #e2b714;
}

/* Processing status */
.processing-status {
    text-align: center;
    padding: 20px;
    color: #646669;
}

.progress-bar {
    height: 6px;
    background-color: #3c3e42;
    border-radius: 3px;
    margin: 12px auto;
    width: 80%;
    max-width: 300px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background-color: #e2b714;
    transition: width 0.4s ease;
}

/* Result content */
.result-content {
    display: flex;
    flex-direction: column;
}

.result-actions {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 8px;
}

.copy-btn.copied {
    background-color: #e2b714;
    color: #323437;
}

/* Error icon */
.error-icon {
    margin-right: 10px;
    font-size: 18px;
}

/* Loader */
.loader {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(226, 183, 20, 0.3);
    border-radius: 50%;
    border-top-color: #e2b714;
    animation: spin 1s linear infinite;
    display: inline-block;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

/* Toggle switch */
.toggle-switch {
    display: flex;
    align-items: center;
    margin-top: 4px;
}

.toggle-input {
    height: 0;
    width: 0;
    visibility: hidden;
    position: absolute;
}

.toggle-label {
    cursor: pointer;
    width: 40px;
    height: 20px;
    background: #3c3e42;
    display: block;
    border-radius: 20px;
    position: relative;
}

.toggle-label:after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 16px;
    height: 16px;
    background: #323437;
    border-radius: 16px;
    transition: 0.3s;
}

.toggle-input:checked + .toggle-label {
    background: #e2b714;
}

.toggle-input:checked + .toggle-label:after {
    left: calc(100% - 2px);
    transform: translateX(-100%);
}

.toggle-text {
    margin-left: 10px;
    font-size: 14px;
}

@media (max-width: 600px) {
    .app-container {
        width: 95%;
        padding: 10px 0;
    }

    .section {
        padding: 16px;
    }

    h1 {
        font-size: 24px;
    }

    .paste-area {
        height: 120px;
    }

    .options-grid {
        grid-template-columns: 1fr;
        gap: 12px;
    }
}
</style>
