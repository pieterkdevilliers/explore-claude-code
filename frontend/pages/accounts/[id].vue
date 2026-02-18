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

    <!-- Chat analytics -->
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

    <!-- Stripe / Billing section -->
    <div>
      <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-200 mb-3 flex items-center gap-2">
        <UIcon name="i-heroicons-credit-card" />
        Billing
      </h3>

      <div v-if="stripePending" class="space-y-3">
        <USkeleton class="h-32 w-full rounded-xl" />
        <USkeleton class="h-20 w-full rounded-xl" />
      </div>

      <p v-else-if="!stripeData?.subscription" class="text-sm text-gray-400 italic">
        No Stripe subscription found for this account.
      </p>

      <div v-else class="space-y-4">
        <!-- Subscription card -->
        <UCard>
          <div class="flex items-start justify-between flex-wrap gap-4">
            <div class="space-y-3">
              <div class="flex items-center gap-2">
                <p class="font-semibold text-gray-800 dark:text-white text-base">
                  {{ stripeData.subscription.related_product_title ?? 'Subscription' }}
                </p>
                <UBadge :color="statusColor(stripeData.subscription.status)" variant="subtle" size="xs">
                  {{ stripeData.subscription.status ?? 'unknown' }}
                </UBadge>
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-1 text-sm text-gray-600 dark:text-gray-300">
                <div v-if="stripeData.subscription.type">
                  <span class="text-gray-400">Type</span>
                  <span class="ml-2 font-medium capitalize">{{ stripeData.subscription.type }}</span>
                </div>
                <div v-if="stripeData.subscription.subscription_start">
                  <span class="text-gray-400">Started</span>
                  <span class="ml-2 font-medium">{{ fmtDate(stripeData.subscription.subscription_start) }}</span>
                </div>
                <div v-if="stripeData.subscription.current_period_end">
                  <span class="text-gray-400">Renews</span>
                  <span class="ml-2 font-medium">{{ fmtDate(stripeData.subscription.current_period_end) }}</span>
                </div>
                <div v-if="stripeData.subscription.trial_start">
                  <span class="text-gray-400">Trial start</span>
                  <span class="ml-2 font-medium">{{ fmtDate(stripeData.subscription.trial_start) }}</span>
                </div>
                <div v-if="stripeData.subscription.trial_end">
                  <span class="text-gray-400">Trial end</span>
                  <span class="ml-2 font-medium">{{ fmtDate(stripeData.subscription.trial_end) }}</span>
                </div>
                <div v-if="stripeData.customer?.email">
                  <span class="text-gray-400">Customer email</span>
                  <span class="ml-2 font-medium">{{ stripeData.customer.email }}</span>
                </div>
                <div v-if="stripeData.customer?.name">
                  <span class="text-gray-400">Customer name</span>
                  <span class="ml-2 font-medium">{{ stripeData.customer.name }}</span>
                </div>
              </div>
            </div>

            <a
              v-if="stripeData.subscription.stripe_account_url"
              :href="stripeData.subscription.stripe_account_url"
              target="_blank"
              rel="noopener noreferrer"
              class="flex items-center gap-1 text-sm text-primary-600 hover:underline shrink-0"
            >
              View in Stripe
              <UIcon name="i-heroicons-arrow-top-right-on-square" class="text-xs" />
            </a>
          </div>
        </UCard>

        <!-- Payment method -->
        <UCard v-if="stripeData.payment_methods?.length">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-3">Payment Method</p>
          <div
            v-for="pm in stripeData.payment_methods"
            :key="pm.last4"
            class="flex items-center gap-3"
          >
            <UIcon name="i-heroicons-credit-card" class="text-2xl text-gray-400" />
            <span class="text-sm text-gray-700 dark:text-gray-200">
              <span class="font-medium capitalize">{{ pm.brand }}</span>
              <span class="ml-2 text-gray-500">•••• {{ pm.last4 }}</span>
              <span class="ml-3 text-gray-400">Exp {{ String(pm.exp_month).padStart(2, '0') }}/{{ pm.exp_year }}</span>
            </span>
          </div>
        </UCard>

        <!-- Invoices -->
        <UCard v-if="stripeData.invoices?.length" :ui="{ body: { padding: 'p-0' } }">
          <template #header>
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-400">Recent Invoices</p>
          </template>
          <UTable :rows="stripeData.invoices" :columns="invoiceColumns">
            <template #created-data="{ row }">
              {{ fmtDate(row.created) }}
            </template>
            <template #amount_paid-data="{ row }">
              {{ fmtAmount(row.amount_paid, row.currency) }}
            </template>
            <template #status-data="{ row }">
              <UBadge :color="invoiceStatusColor(row.status)" variant="subtle" size="xs">
                {{ row.status ?? '—' }}
              </UBadge>
            </template>
            <template #invoice_pdf-data="{ row }">
              <a
                v-if="row.invoice_pdf"
                :href="row.invoice_pdf"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary-500 hover:text-primary-700"
                title="Download PDF"
              >
                <UIcon name="i-heroicons-arrow-down-tray" />
              </a>
              <span v-else class="text-gray-300">—</span>
            </template>
          </UTable>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CountResponse { count: number; period_days: number }
interface SentimentResponse {
  sentiments: { sentiment: string | null; count: number }[]
  period_days: number
}
interface StripeSubscription {
  stripe_subscription_id: string
  stripe_customer_id: string
  status: string | null
  current_period_end: string | null
  type: string | null
  trial_start: string | null
  trial_end: string | null
  subscription_start: string | null
  stripe_account_url: string | null
  related_product_title: string | null
}
interface StripeCustomer {
  id: string
  email: string | null
  name: string | null
}
interface StripePaymentMethod {
  brand: string
  last4: string
  exp_month: number
  exp_year: number
}
interface StripeInvoice {
  id: string
  number: string | null
  amount_paid: number
  currency: string
  status: string | null
  created: string
  invoice_pdf: string | null
}
interface AccountStripeResponse {
  subscription: StripeSubscription | null
  customer: StripeCustomer | null
  payment_methods: StripePaymentMethod[]
  invoices: StripeInvoice[]
}

const route = useRoute()
const id = route.params.id as string

const { data: sessionsData, pending: sessionsPending } =
  useApi<CountResponse>(`/accounts/${id}/sessions/count`)

const { data: messagesData, pending: messagesPending } =
  useApi<CountResponse>(`/accounts/${id}/messages/count`)

const { data: sentimentData, pending: sentimentPending } =
  useApi<SentimentResponse>(`/accounts/${id}/messages/by-sentiment`)

const { data: stripeData, pending: stripePending } =
  useApi<AccountStripeResponse>(`/accounts/${id}/stripe`)

// --- Display helpers ---

function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

function fmtAmount(cents: number, currency: string): string {
  return new Intl.NumberFormat(undefined, {
    style: 'currency',
    currency: currency.toUpperCase(),
  }).format(cents / 100)
}

function statusColor(status: string | null | undefined) {
  if (status === 'active') return 'green'
  if (status === 'trialing') return 'blue'
  if (status === 'past_due' || status === 'unpaid') return 'red'
  return 'gray'
}

function invoiceStatusColor(status: string | null | undefined) {
  if (status === 'paid') return 'green'
  if (status === 'open') return 'yellow'
  if (status === 'void' || status === 'uncollectible') return 'red'
  return 'gray'
}

const invoiceColumns = [
  { key: 'created', label: 'Date' },
  { key: 'number', label: 'Invoice #' },
  { key: 'amount_paid', label: 'Amount' },
  { key: 'status', label: 'Status' },
  { key: 'invoice_pdf', label: 'PDF' },
]
</script>
