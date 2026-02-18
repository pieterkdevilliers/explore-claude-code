import type { UseFetchOptions } from 'nuxt/app'

/**
 * Reactive data loader (for use in <script setup>).
 * Wraps useFetch with: API base URL, Bearer token injection, 401 redirect.
 */
export function useApi<T>(path: string, options: UseFetchOptions<T> = {}) {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  return useFetch<T>(`${config.public.apiBase}${path}`, {
    ...options,
    headers: {
      ...(options.headers as Record<string, string> | undefined),
      ...(authStore.token ? { Authorization: `Bearer ${authStore.token}` } : {}),
    },
    async onResponseError({ response }) {
      if (response.status === 401) {
        authStore.token = null
        authStore.user = null
        await navigateTo('/login')
      }
    },
  })
}

/**
 * Imperative fetch (for use inside event handlers where useFetch cannot be called).
 */
export async function apiFetch<T>(
  path: string,
  opts: Parameters<typeof $fetch>[1] = {},
): Promise<T> {
  const config = useRuntimeConfig()
  const authStore = useAuthStore()

  return $fetch<T>(`${config.public.apiBase}${path}`, {
    ...opts,
    headers: {
      ...(opts.headers as Record<string, string> | undefined),
      ...(authStore.token ? { Authorization: `Bearer ${authStore.token}` } : {}),
    },
  })
}
