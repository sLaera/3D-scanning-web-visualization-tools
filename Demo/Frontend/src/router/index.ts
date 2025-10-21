import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layout/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '/',
          name: 'home',
          component: () => import('@/views/HomeView.vue')
        },
        {
          path: '/demo-multiple-instances',
          name: 'demo-load-gltf',
          component: () => import('@/views/UnityMultipleInstancesView.vue')
        },
      ]
    }
  ]
})

export default router
