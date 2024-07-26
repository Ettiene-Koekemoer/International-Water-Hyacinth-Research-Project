import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PredictionView from "@/views/PredictionView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/PredictionView',
            name: 'predictionView',
            component: PredictionView,
            props: (route) => ({
                latitude: route.params.latitude,
                longitude: route.params.longitude,
                X1: route.params.X1,
                Y1: route.params.Y1,
                X2: route.params.X2,
                Y2: route.params.Y2
            }),

        }
    ]
})

export default router
