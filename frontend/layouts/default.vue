<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
    <AppSidebar class="w-64 shrink-0" />

    <div class="flex flex-col flex-1 overflow-hidden">
      <!-- Top bar -->
      <header
        class="h-14 shrink-0 border-b border-gray-200 dark:border-gray-700
               bg-white dark:bg-gray-800 flex items-center px-6 gap-4"
      >
        <span class="text-sm font-semibold text-gray-700 dark:text-gray-200">
          Management Overview
        </span>
        <div class="ml-auto flex items-center gap-3">
          <span class="text-xs text-gray-500 dark:text-gray-400">
            {{ authStore.user?.email }}
          </span>
          <UButton size="xs" color="gray" variant="ghost" @click="authStore.logout()">
            Logout
          </UButton>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
</script>
