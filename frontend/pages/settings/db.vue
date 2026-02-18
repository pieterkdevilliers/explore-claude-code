<template>
  <div class="space-y-6 max-w-xl">
    <h2 class="text-2xl font-bold text-gray-800 dark:text-white">Database Connection</h2>

    <!-- Current status -->
    <UCard>
      <template #header>
        <p class="text-sm font-semibold text-gray-700 dark:text-gray-200">Current Status</p>
      </template>

      <div v-if="statusPending" class="space-y-2">
        <USkeleton class="h-6 w-32" />
        <USkeleton class="h-4 w-64" />
      </div>
      <div v-else class="space-y-2">
        <div class="flex items-center gap-2 flex-wrap">
          <UBadge :color="statusData?.reachable ? 'green' : 'red'">
            {{ statusData?.reachable ? 'Connected' : 'Disconnected' }}
          </UBadge>
          <UBadge v-if="statusData?.configured" color="gray" variant="subtle">
            URL configured
          </UBadge>
        </div>
        <p class="text-sm text-gray-500">{{ statusData?.message }}</p>
      </div>
    </UCard>

    <!-- Configure URL -->
    <UCard>
      <template #header>
        <p class="text-sm font-semibold text-gray-700 dark:text-gray-200">
          Configure Connection URL
        </p>
      </template>

      <div class="space-y-4">
        <UFormGroup
          label="PostgreSQL URL"
          help="Format: postgres://user:pass@host:5432/dbname"
        >
          <UInput
            v-model="url"
            placeholder="postgres://..."
            :disabled="testing || saving"
          />
        </UFormGroup>

        <UAlert
          v-if="testResult"
          :color="testResult.success ? 'green' : 'red'"
          :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
          :description="testResult.message"
        />

        <p v-if="testResult?.server_version" class="text-xs text-gray-400 font-mono">
          {{ testResult.server_version }}
        </p>

        <div class="flex gap-3">
          <UButton
            color="gray"
            :loading="testing"
            :disabled="!url || saving"
            @click="testConnection"
          >
            Test Connection
          </UButton>
          <UButton
            :loading="saving"
            :disabled="!testResult?.success || testing"
            @click="saveConnection"
          >
            Save &amp; Activate
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: ['superuser'] })

interface DbTestResult { success: boolean; message: string; server_version: string | null }
interface DbStatus { configured: boolean; reachable: boolean; message: string }

const { data: statusData, pending: statusPending, refresh: refreshStatus } =
  useApi<DbStatus>('/db-connection/status')

const url = ref('')
const testResult = ref<DbTestResult | null>(null)
const testing = ref(false)
const saving = ref(false)

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    testResult.value = await apiFetch<DbTestResult>('/db-connection/test', {
      method: 'POST',
      body: { url: url.value },
    })
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    testResult.value = {
      success: false,
      message: err?.data?.detail ?? 'Connection test failed.',
      server_version: null,
    }
  }
  finally {
    testing.value = false
  }
}

async function saveConnection() {
  saving.value = true
  try {
    await apiFetch('/db-connection/save', {
      method: 'POST',
      body: { url: url.value },
    })
    await refreshStatus()
  }
  finally {
    saving.value = false
  }
}
</script>
