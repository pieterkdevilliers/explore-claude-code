<template>
  <div class="space-y-4">
    <h2 class="text-2xl font-bold text-gray-800 dark:text-white">Accounts</h2>

    <UCard :ui="{ body: { padding: 'p-0' } }">
      <div v-if="pending" class="p-6 space-y-3">
        <USkeleton v-for="i in 6" :key="i" class="h-10 w-full" />
      </div>

      <UTable
        v-else
        :rows="accountsData?.accounts ?? []"
        :columns="columns"
      >
        <template #account_organisation-data="{ row }">
          <NuxtLink
            :to="`/accounts/${row.account_unique_id}`"
            class="font-medium text-primary-600 hover:underline"
          >
            {{ row.account_organisation }}
          </NuxtLink>
        </template>
      </UTable>
    </UCard>
  </div>
</template>

<script setup lang="ts">
interface AccountRead {
  id: number
  account_organisation: string
  account_unique_id: string
  relevance_score: number | null
  k_value: number | null
  temperature: number | null
}

const { data: accountsData, pending } =
  useApi<{ accounts: AccountRead[]; total: number }>('/accounts/')

const columns = [
  { key: 'account_organisation', label: 'Organisation' },
  { key: 'account_unique_id', label: 'Unique ID' },
  { key: 'relevance_score', label: 'Relevance Score' },
  { key: 'k_value', label: 'K Value' },
  { key: 'temperature', label: 'Temperature' },
]
</script>
