/**
 * Advanced text post-processing service to improve OCR results
 */
export class TextProcessor {
    /**
     * Apply multiple post-processing techniques to OCR text
     */
    static improveText(text: string, preserveLayout: boolean = true): string {
        let result = text;

        // Apply adaptable text improvements
        result = this.fixCommonErrors(result);
        result = this.normalizeSpacing(result, preserveLayout);
        result = this.fixLineBreaks(result, preserveLayout);
        result = this.fixCommonSymbols(result);

        return result;
    }

    /**
     * Fix spacing issues in OCR text while preserving layout
     */
    static normalizeSpacing(text: string, preserveLayout: boolean = true): string {
        if (preserveLayout) {
            // When preserving layout, only fix the most obvious issues

            // Replace multiple spaces (more than 2) with double spaces
            let result = text.replace(/[ ]{3,}/g, '  ');

            // Fix missing space after punctuation marks at word boundaries
            result = result.replace(/([.!?,;:])([A-Z])/g, '$1 $2');

            return result;
        }

        // Standard spacing normalization for non-layout-preserving mode
        let result = text.replace(/\s+/g, ' ');
        result = result.replace(/([.!?,;:])([a-zA-Z])/g, '$1 $2');
        result = result.replace(/\s+([(\[{])/g, ' $1');
        result = result.replace(/([)\]}])\s*/g, '$1 ');

        return result;
    }

    /**
     * Fix common OCR errors
     */
    static fixCommonErrors(text: string): string {
        const commonErrors: { [key: string]: string; } = {
            '0': 'O',
            'l': 'I',
            '1': 'I',
            '5': 'S',
            'rn': 'm',
            'cl': 'd',
            'vv': 'w',
            '\u201C': '"', // Fix smart quotes
            '\u201D': '"',
        };

        // We only replace these errors when they appear as standalone characters
        // to avoid changing actual numbers or valid combinations
        let result = text;

        // Replace common OCR errors with their corrections
        Object.keys(commonErrors).forEach(error => {
            // Use regex to identify standalone characters
            const regex = new RegExp(`\\b${error}\\b`, 'g');
            result = result.replace(regex, commonErrors[error]);
        });

        return result;
    }

    /**
     * Fix line break issues while preserving original layout
     */
    static fixLineBreaks(text: string, preserveLayout: boolean = true): string {
        if (preserveLayout) {
            // When preserving layout, leave most line breaks intact

            // Only normalize multiple consecutive blank lines (>2)
            let result = text.replace(/\n{3,}/g, '\n\n');

            // Don't touch other line breaks
            return result;
        }

        // Standard line break handling
        let result = text.replace(/([^.!?;:])\n([a-zA-Z])/g, '$1 $2');
        result = result.replace(/([.!?])\s*\n/g, '$1\n\n');

        return result;
    }

    /**
     * Fix common symbol recognition errors
     */
    static fixCommonSymbols(text: string): string {
        // Fix common symbol errors
        const symbolFixes: { [key: string]: string; } = {
            '—': '-',
            '–': '-',
            '…': '...',
            '\'': "'",
            '’': "'",
            '′': "'",
            '″': '"',
        };

        let result = text;

        // Replace symbol errors
        Object.keys(symbolFixes).forEach(symbol => {
            result = result.replace(new RegExp(symbol, 'g'), symbolFixes[symbol]);
        });

        return result;
    }
}
