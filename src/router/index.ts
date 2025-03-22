import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router';
import OcrApp from '@/views/OcrApp.vue';
import ChatApp from '@/views/ChatApp.vue';

const routes: Array<RouteRecordRaw> = [
    {
        path: '/',
        name: 'OCR',
        component: OcrApp
    },
    {
        path: '/chat',
        name: 'Chat',
        component: ChatApp
    }
];

const router = createRouter({
    history: createWebHistory('/'),  // Use root path instead of process.env.BASE_URL
    routes
});

export default router;
