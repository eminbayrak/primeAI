import axios from 'axios';
import * as Tesseract from 'tesseract.js';
import { TextProcessor } from './TextProcessor';

export interface OcrResult {
    text: string;
    confidence: number;
    engine?: string;
    words?: number;
}

export interface OcrProgress {
    progress: number;
    status: string;
}

export interface ServerInfo {
    supported_languages: Record<string, string>;
    preprocessing_options: string[];
    quality_options: string[];
    version: string;
}

export class OcrService {
    private static readonly SERVER_URL = 'http://localhost:5000';
    private static serverInfo: ServerInfo | null = null;

    /**
     * Process image with local Tesseract.js
     */
    static async processWithTesseract(
        imageUrl: string,
        language: string,
        options: any = {},
        progressCallback: (progress: OcrProgress) => void,
        preserveLayout: boolean = true
    ): Promise<OcrResult> {
        // Use optimal PSM mode based on layout preservation preference
        if (preserveLayout) {
            // For layout preservation, we prefer these modes:
            // PSM.SPARSE_TEXT (11): Sparse text. Find as much text as possible in no particular order.
            // PSM.SPARSE_TEXT_OSD (12): Sparse text with OSD (orientation and script detection)
            options.tessedit_pageseg_mode = Tesseract.PSM.SPARSE_TEXT;
        } else {
            // For continuous text without layout concerns:
            // PSM.SINGLE_BLOCK (6): Assume a single uniform block of text.
            options.tessedit_pageseg_mode = Tesseract.PSM.SINGLE_BLOCK;
        }

        // Additional options for better OCR
        const tessOptions = {
            ...options,
            preserve_interword_spaces: preserveLayout ? '1' : '0',  // Preserve spaces between words
            textord_tablefind_recognize_tables: preserveLayout ? '1' : '0',  // Better table recognition
            textord_preserve_line_breaks: preserveLayout ? '1' : '0',  // Preserve line breaks
            textord_tabfind_vertical_text: preserveLayout ? '1' : '0',  // Better vertical text detection
        };

        const result = await Tesseract.recognize(imageUrl, language, {
            logger: m => {
                if (m.status === 'recognizing text') {
                    progressCallback({ progress: m.progress, status: 'recognizing' });
                } else {
                    progressCallback({ progress: m.progress || 0, status: m.status });
                }
            },
            ...tessOptions
        });

        // Apply minimal post-processing when layout preservation is enabled
        const processedText = TextProcessor.improveText(result.data.text, preserveLayout);

        return {
            text: processedText,
            confidence: result.data.confidence || 0,
            engine: 'tesseract',
            words: processedText.split(/\s+/).length
        };
    }

    /**
     * Check if EasyOCR server is available
     */
    static async isServerAvailable(): Promise<boolean> {
        try {
            const response = await axios.get(`${this.SERVER_URL}/health`, { timeout: 2000 });
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    /**
     * Get server information (supported languages, options)
     */
    static async getServerInfo(): Promise<ServerInfo | null> {
        if (this.serverInfo) {
            return this.serverInfo;
        }

        try {
            const response = await axios.get(`${this.SERVER_URL}/info`, { timeout: 2000 });
            this.serverInfo = response.data;
            return this.serverInfo;
        } catch (error) {
            console.error('Failed to get server info:', error);
            return null;
        }
    }

    /**
     * Process image with EasyOCR server
     */
    static async processWithEasyOCR(
        imageFile: File,
        language: string,
        quality: string = 'standard',
        preprocessing: string[] = [],
        progressCallback: (progress: OcrProgress) => void,
        preserveLayout: boolean = true
    ): Promise<OcrResult> {
        // Start with indeterminate progress
        progressCallback({ progress: 0.1, status: 'uploading' });

        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('language', language);
        formData.append('quality', quality);
        formData.append('preserve_layout', preserveLayout.toString());

        // Add preprocessing steps if any
        preprocessing.forEach(step => {
            formData.append('preprocessing', step);
        });

        try {
            // Upload progress simulation (we can't track actual server processing)
            let fakeProgress = 0.1;
            const interval = setInterval(() => {
                fakeProgress += 0.05;
                if (fakeProgress < 0.9) {
                    progressCallback({ progress: fakeProgress, status: 'processing' });
                } else {
                    clearInterval(interval);
                }
            }, 300);

            const response = await axios.post(`${this.SERVER_URL}/ocr`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                },
                timeout: 60000 // 1 minute timeout for large/complex images
            });

            clearInterval(interval);
            progressCallback({ progress: 1, status: 'completed' });

            // Apply the same post-processing as we do with Tesseract
            const processedText = TextProcessor.improveText(response.data.text, preserveLayout);

            return {
                text: processedText,
                confidence: response.data.confidence || 0,
                engine: response.data.engine || 'easyocr',
                words: response.data.words || processedText.split(/\s+/).length
            };
        } catch (error) {
            console.error('EasyOCR server error:', error);
            throw new Error('Failed to process image with EasyOCR. Is the server running?');
        }
    }
}
