<template>
  <UModal v-model="open">
    <UCard>
      <template #header>
        <p class="font-semibold">{{ isEditing ? 'Edit User' : 'Create User' }}</p>
      </template>

      <div class="space-y-4">
        <UFormGroup label="Email" name="email">
          <UInput v-model="form.email" type="email" placeholder="user@example.com" />
        </UFormGroup>

        <UFormGroup label="Full Name" name="full_name">
          <UInput v-model="form.full_name" placeholder="Jane Doe" />
        </UFormGroup>

        <UFormGroup
          label="Password"
          name="password"
          :help="isEditing ? 'Leave blank to keep current password' : ''"
        >
          <UInput v-model="form.password" type="password" />
        </UFormGroup>

        <UFormGroup v-if="!isEditing" label="Superuser" name="is_superuser">
          <UToggle v-model="form.is_superuser" />
        </UFormGroup>

        <UAlert
          v-if="errorMsg"
          color="red"
          variant="subtle"
          :description="errorMsg"
        />
      </div>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton color="gray" variant="ghost" @click="open = false">Cancel</UButton>
          <UButton :loading="saving" @click="onSubmit">
            {{ isEditing ? 'Save Changes' : 'Create User' }}
          </UButton>
        </div>
      </template>
    </UCard>
  </UModal>
</template>

<script setup lang="ts">
import type { UserRead } from '~/stores/auth'

const props = defineProps<{ user: UserRead | null }>()
const open = defineModel<boolean>('open', { default: false })
const emit = defineEmits<{ saved: [] }>()

const isEditing = computed(() => !!props.user)
const saving = ref(false)
const errorMsg = ref<string | null>(null)

const form = reactive({
  email: '',
  full_name: '',
  password: '',
  is_superuser: false,
})

watch(
  () => props.user,
  (u) => {
    if (u) {
      form.email = u.email
      form.full_name = u.full_name ?? ''
      form.password = ''
      form.is_superuser = u.is_superuser
    }
    else {
      Object.assign(form, { email: '', full_name: '', password: '', is_superuser: false })
    }
    errorMsg.value = null
  },
  { immediate: true },
)

async function onSubmit() {
  saving.value = true
  errorMsg.value = null
  try {
    if (isEditing.value && props.user) {
      const body: Record<string, unknown> = { email: form.email, full_name: form.full_name || null }
      if (form.password) body.password = form.password
      await apiFetch(`/users/${props.user.id}`, { method: 'PATCH', body })
    }
    else {
      await apiFetch('/users/', {
        method: 'POST',
        body: {
          email: form.email,
          password: form.password,
          full_name: form.full_name || null,
          is_superuser: form.is_superuser,
        },
      })
    }
    open.value = false
    emit('saved')
  }
  catch (e: unknown) {
    const err = e as { data?: { detail?: string } }
    errorMsg.value = err?.data?.detail ?? 'An error occurred.'
  }
  finally {
    saving.value = false
  }
}
</script>
