<template>
  <aside
    class="flex flex-col h-full border-r border-gray-200 dark:border-gray-700
           bg-white dark:bg-gray-800"
  >
    <!-- Logo -->
    <div
      class="h-14 shrink-0 flex items-center px-4 border-b
             border-gray-200 dark:border-gray-700"
    >
      <span class="font-bold text-primary-600 dark:text-primary-400 tracking-wide text-sm">
        Management
      </span>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto py-4 px-2">
      <UVerticalNavigation :links="navLinks" />
    </nav>

    <!-- User footer -->
    <div class="p-4 border-t border-gray-200 dark:border-gray-700">
      <p class="text-xs text-gray-500 truncate">
        {{ authStore.user?.full_name || authStore.user?.email }}
      </p>
      <UBadge v-if="authStore.isSuperuser" color="purple" variant="subtle" size="xs" class="mt-1">
        Superuser
      </UBadge>
    </div>
  </aside>
</template>

<script setup lang="ts">
const authStore = useAuthStore()

const navLinks = computed(() => {
  const links = [
    { label: 'Dashboard', icon: 'i-heroicons-chart-bar', to: '/dashboard' },
    { label: 'Accounts', icon: 'i-heroicons-building-office', to: '/accounts' },
  ]
  if (authStore.isSuperuser) {
    links.push(
      { label: 'Users', icon: 'i-heroicons-users', to: '/users' },
      { label: 'DB Connection', icon: 'i-heroicons-circle-stack', to: '/settings/db' },
    )
  }
  return links
})
</script>
