<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink
        to="/accounts"
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
      >
        <UIcon name="i-heroicons-arrow-left" class="text-xl" />
      </NuxtLink>
      <div>
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white">Account</h2>
        <p class="text-sm text-gray-500 font-mono">{{ id }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <StatCard
        label="Sessions"
        :count="sessionsData?.count"
        :period-days="30"
        icon="i-heroicons-chat-bubble-left-right"
        :loading="sessionsPending"
      />
      <StatCard
        label="Messages"
        :count="messagesData?.count"
        :period-days="30"
        icon="i-heroicons-chat-bubble-oval-left"
        :loading="messagesPending"
      />
    </div>

    <SentimentChart
      :sentiments="sentimentData?.sentiments"
      :pending="sentimentPending"
    />
  </div>
</template>

<script setup lang="ts">
interface CountResponse { count: number; period_days: number }
interface SentimentResponse {
  sentiments: { sentiment: string | null; count: number }[]
  period_days: number
}

const route = useRoute()
const id = route.params.id as string

const { data: sessionsData, pending: sessionsPending } =
  useApi<CountResponse>(`/accounts/${id}/sessions/count`)

const { data: messagesData, pending: messagesPending } =
  useApi<CountResponse>(`/accounts/${id}/messages/count`)

const { data: sentimentData, pending: sentimentPending } =
  useApi<SentimentResponse>(`/accounts/${id}/messages/by-sentiment`)
</script>
