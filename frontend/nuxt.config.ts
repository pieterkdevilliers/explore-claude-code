// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Keep pages/components/etc at the frontend/ root (override compat v4 default of app/)
  srcDir: '.',

  modules: ['./modules/tailwind-postcss-fix', '@nuxt/ui', '@pinia/nuxt'],

  runtimeConfig: {
    // Server-side only — override with NUXT_API_BASE (used for SSR calls inside Docker)
    apiBase: '',
    public: {
      // Client-side (browser) — override with NUXT_PUBLIC_API_BASE
      apiBase: 'http://localhost:8000',
    },
  },

  typescript: {
    strict: true,
  },

  devtools: { enabled: true },
})
