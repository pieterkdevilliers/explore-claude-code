<template>
  <UCard>
    <template #header>
      <p class="text-sm font-semibold text-gray-700 dark:text-gray-200">
        Message Sentiment Breakdown — Last 30 Days
      </p>
    </template>

    <div class="flex items-center justify-center" style="height: 260px;">
      <USkeleton v-if="pending" class="h-full w-full rounded-xl" />
      <p
        v-else-if="!sentiments || sentiments.length === 0"
        class="text-sm text-gray-400"
      >
        No sentiment data available.
      </p>
      <ClientOnly v-else>
        <Doughnut :data="chartData" :options="chartOptions" style="max-height: 240px;" />
      </ClientOnly>
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

interface SentimentCount {
  sentiment: string | null
  count: number
}

const SENTIMENT_COLORS: Record<string, string> = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral: '#94a3b8',
  mixed: '#f59e0b',
}

const props = defineProps<{
  sentiments?: SentimentCount[]
  pending?: boolean
}>()

const chartData = computed(() => ({
  labels: (props.sentiments ?? []).map(s => s.sentiment ?? 'Unclassified'),
  datasets: [
    {
      data: (props.sentiments ?? []).map(s => s.count),
      backgroundColor: (props.sentiments ?? []).map(
        s => SENTIMENT_COLORS[s.sentiment ?? ''] ?? '#cbd5e1',
      ),
      borderWidth: 1,
      borderColor: '#fff',
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' as const },
  },
}
</script>
