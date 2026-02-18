<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
    <UCard class="w-full max-w-sm">
      <template #header>
        <h1 class="text-xl font-bold text-center text-gray-800 dark:text-white">
          Management Login
        </h1>
      </template>

      <div class="space-y-4">
        <UFormGroup label="Email">
          <UInput
            v-model="form.email"
            type="email"
            placeholder="admin@example.com"
            :disabled="loading"
          />
        </UFormGroup>

        <UFormGroup label="Password">
          <UInput
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            :disabled="loading"
            @keyup.enter="onSubmit"
          />
        </UFormGroup>

        <UAlert
          v-if="errorMsg"
          color="red"
          variant="subtle"
          :description="errorMsg"
        />

        <UButton block :loading="loading" @click="onSubmit">
          Sign In
        </UButton>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const authStore = useAuthStore()

// Redirect already-authenticated users
if (authStore.isAuthenticated) {
  await navigateTo('/dashboard')
}

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const errorMsg = ref<string | null>(null)

async function onSubmit() {
  if (!form.email || !form.password) {
    errorMsg.value = 'Please enter your email and password.'
    return
  }
  loading.value = true
  errorMsg.value = null
  try {
    await authStore.login(form.email, form.password)
    await navigateTo('/dashboard')
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    errorMsg.value = err?.data?.detail ?? 'Login failed. Check your credentials.'
  }
  finally {
    loading.value = false
  }
}
</script>
