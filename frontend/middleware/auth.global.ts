export default defineNuxtRouteMiddleware((to) => {
  if (to.path === '/login') return

  const authStore = useAuthStore()
  // useCookie is SSR-safe; js-cookie only works on the client
  const tokenCookie = useCookie('auth_token')
  const hasToken = authStore.token ?? tokenCookie.value

  if (!hasToken) {
    return navigateTo('/login')
  }
})
