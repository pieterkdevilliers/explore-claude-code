/**
 * Fix for @nuxtjs/tailwindcss 6.x + Tailwind CSS 3 on Node 18.
 *
 * The module generates a .mjs config file and passes it as a string path
 * to the tailwindcss PostCSS plugin. Tailwind 3 tries to load it via jiti,
 * but @nuxt/kit (imported transitively inside the config) uses `import.meta`
 * at the top level, which jiti/sucrase cannot transform → SyntaxError.
 *
 * Fix: after all modules are done, dynamically import() the .mjs file (which
 * works fine for ESM) and replace the string path with the inline config
 * object. Tailwind 3 accepts an object directly and skips jiti loading.
 */
import { defineNuxtModule } from '@nuxt/kit'

export default defineNuxtModule({
  meta: { name: 'tailwind-postcss-fix' },
  setup(_, nuxt) {
    nuxt.hook('build:before', async () => {
      const plugins = (nuxt.options.postcss as Record<string, unknown>)
        ?.plugins as Record<string, unknown> | undefined
      if (!plugins) return
      const twPlugin = plugins.tailwindcss
      if (typeof twPlugin !== 'string' || !twPlugin.endsWith('.mjs')) return

      try {
        // ESM dynamic import works fine for .mjs files
        const mod = await import(twPlugin)
        plugins.tailwindcss = mod.default ?? mod
      } catch (e) {
        console.warn('[tailwind-postcss-fix] Could not inline Tailwind config:', e)
      }
    })
  },
})
