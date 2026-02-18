<template>
  <UCard>
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ label }}</p>
        <div class="mt-1">
          <USkeleton v-if="loading" class="h-9 w-24" />
          <p v-else class="text-3xl font-bold text-gray-900 dark:text-white">
            {{ count != null ? count.toLocaleString() : '—' }}
          </p>
        </div>
        <p class="text-xs text-gray-400 mt-1">Last {{ periodDays }} days</p>
      </div>
      <UIcon :name="icon" class="text-3xl text-primary-400 opacity-60 mt-0.5" />
    </div>
  </UCard>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  count?: number | null
  periodDays: number
  icon: string
  loading?: boolean
}>()
</script>
