import { defineStore } from 'pinia'
import Cookies from 'js-cookie'

export interface UserRead {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
  updated_at: string
}

const COOKIE_KEY = 'auth_token'
const COOKIE_OPTIONS: Cookies.CookieAttributes = {
  expires: 1,
  sameSite: 'Lax',
  secure: false, // set to true in production (HTTPS)
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(
    import.meta.client ? (Cookies.get(COOKIE_KEY) ?? null) : null,
  )
  const user = ref<UserRead | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.is_superuser === true)

  async function login(email: string, password: string) {
    const config = useRuntimeConfig()
    const response = await $fetch<{ access_token: string; token_type: string }>(
      `${config.public.apiBase}/auth/login`,
      { method: 'POST', body: { email, password } },
    )
    token.value = response.access_token
    Cookies.set(COOKIE_KEY, response.access_token, COOKIE_OPTIONS)
    await fetchUser()
  }

  async function fetchUser() {
    if (!token.value) return
    const config = useRuntimeConfig()
    try {
      const data = await $fetch<UserRead>(`${config.public.apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      user.value = data
    }
    catch {
      logout()
    }
  }

  function logout() {
    const config = useRuntimeConfig()
    // Best-effort server logout (stateless JWT — failure is tolerable)
    if (token.value) {
      $fetch(`${config.public.apiBase}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}` },
      }).catch(() => {})
    }
    token.value = null
    user.value = null
    Cookies.remove(COOKIE_KEY)
    navigateTo('/login')
  }

  return { token, user, isAuthenticated, isSuperuser, login, logout, fetchUser }
})
