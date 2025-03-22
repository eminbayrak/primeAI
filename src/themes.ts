import { ref } from 'vue';

export interface Theme {
    name: string;
    colors: {
        bgPrimary: string;
        bgSecondary: string;
        bgTertiary: string;
        bgInput: string;
        bgHover: string;
        bgSidebar: string;
        bgContextMenu: string;

        textPrimary: string;
        textSecondary: string;
        textTertiary: string;
        textInverted: string;

        borderPrimary: string;
        borderSecondary: string;

        accent: string;
        accentHover: string;
        accentText: string;

        success: string;
        error: string;
        warning: string;
    };
}

export const darkTheme: Theme = {
    name: 'dark',
    colors: {
        bgPrimary: '#000000',
        bgSecondary: '#0A0A0A',
        bgTertiary: '#111111',
        bgInput: '#0A0A0A',
        bgHover: '#1A1A1A',
        bgSidebar: '#000000',
        bgContextMenu: '#0A0A0A',

        textPrimary: '#FFFFFF',
        textSecondary: '#CCCCCC',
        textTertiary: '#666666',
        textInverted: '#000000',

        borderPrimary: '#1A1A1A',
        borderSecondary: '#111111',

        accent: '#FFFFFF',
        accentHover: '#CCCCCC',
        accentText: '#000000',

        success: '#00FF00',
        error: '#FF0000',
        warning: '#FFFF00'
    }
}; 