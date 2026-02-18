<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white">Dashboard</h2>
      <p class="text-sm text-gray-500 mt-1">Global analytics — last 30 days</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <StatCard
        label="Total Sessions"
        :count="sessionsData?.count"
        :period-days="sessionsData?.period_days ?? 30"
        icon="i-heroicons-chat-bubble-left-right"
        :loading="sessionsPending"
      />
      <StatCard
        label="Total Messages"
        :count="messagesData?.count"
        :period-days="messagesData?.period_days ?? 30"
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

const { data: sessionsData, pending: sessionsPending } =
  useApi<CountResponse>('/analytics/sessions/count')

const { data: messagesData, pending: messagesPending } =
  useApi<CountResponse>('/analytics/messages/count')

const { data: sentimentData, pending: sentimentPending } =
  useApi<SentimentResponse>('/analytics/messages/by-sentiment')
</script>
