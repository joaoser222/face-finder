/**
 * router/index.ts
 *
 * Automatic routes for `./src/pages/*.vue`
 */

// Composables
import { createRouter, createWebHistory } from 'vue-router/auto'

const routes = [
  {
    path: '/login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/',
    component: () => import('@/pages/Layout.vue'),
    redirect: '/collections',
    children: [
      {
        path: 'collections',
        component: () => import('@/pages/collections/Index.vue'),
      },
      {
        path: 'collections/:id',
        props: true,
        component: () => import('@/pages/collections/Item.vue'),
      },
      {
        path: 'searches',
        component: () => import('@/pages/Search.vue'),
      },
      {
        path: 'settings',
        component: () => import('@/pages/Setting.vue'),
      },
      {
        path: 'collections/:id',
        component: () => import('@/pages/Collection.vue'),
      },
    ],
  },
] 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.('Failed to fetch dynamically imported module')) {
    if (!localStorage.getItem('vuetify:dynamic-reload')) {
      console.log('Reloading page to fix dynamic import error')
      localStorage.setItem('vuetify:dynamic-reload', 'true')
      location.assign(to.fullPath)
    } else {
      console.error('Dynamic import error, reloading page did not fix it', err)
    }
  } else {
    console.error(err)
  }
})

router.isReady().then(() => {
  localStorage.removeItem('vuetify:dynamic-reload')
})

export default router
