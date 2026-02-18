// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Keep pages/components/etc at the frontend/ root (override compat v4 default of app/)
  srcDir: '.',

  modules: ['./modules/tailwind-postcss-fix', '@nuxt/ui', '@pinia/nuxt'],

  runtimeConfig: {
    public: {
      // Override with NUXT_PUBLIC_API_BASE env var
      apiBase: 'http://localhost:8000',
    },
  },

  typescript: {
    strict: true,
  },

  devtools: { enabled: true },
})
