export default defineNuxtRouteMiddleware(async () => {
  const authStore = useAuthStore()

  // Ensure user is loaded (e.g. after hard refresh)
  if (!authStore.user && authStore.token) {
    await authStore.fetchUser()
  }

  if (!authStore.isSuperuser) {
    return navigateTo('/dashboard')
  }
})
