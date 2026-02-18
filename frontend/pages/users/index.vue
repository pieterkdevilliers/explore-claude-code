<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white">Users</h2>
      <UButton icon="i-heroicons-plus" @click="openCreate">
        Add User
      </UButton>
    </div>

    <UCard :ui="{ body: { padding: 'p-0' } }">
      <UTable :rows="data ?? []" :columns="columns">
        <template #is_active-data="{ row }">
          <UBadge :color="row.is_active ? 'green' : 'red'" variant="subtle">
            {{ row.is_active ? 'Active' : 'Inactive' }}
          </UBadge>
        </template>

        <template #is_superuser-data="{ row }">
          <UBadge v-if="row.is_superuser" color="purple" variant="subtle">Superuser</UBadge>
          <span v-else class="text-gray-400 text-xs">—</span>
        </template>

        <template #actions-data="{ row }">
          <div class="flex gap-1">
            <UButton
              size="xs"
              color="gray"
              variant="ghost"
              icon="i-heroicons-pencil-square"
              @click="openEdit(row)"
            />
            <UButton
              size="xs"
              color="red"
              variant="ghost"
              icon="i-heroicons-trash"
              @click="confirmDelete(row)"
            />
          </div>
        </template>
      </UTable>
    </UCard>

    <!-- Create/Edit modal -->
    <UsersUserModal v-model:open="modalOpen" :user="editingUser" @saved="refresh()" />

    <!-- Delete confirmation -->
    <UModal v-model="deleteModalOpen">
      <UCard>
        <template #header>
          <p class="font-semibold">Delete User</p>
        </template>
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Are you sure you want to delete
          <strong>{{ deletingUser?.email }}</strong>?
          This action cannot be undone.
        </p>
        <template #footer>
          <div class="flex justify-end gap-2">
            <UButton color="gray" variant="ghost" @click="deleteModalOpen = false">
              Cancel
            </UButton>
            <UButton color="red" :loading="deleting" @click="executeDelete">
              Delete
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { UserRead } from '~/stores/auth'

definePageMeta({ middleware: ['superuser'] })

const { data, refresh } = useApi<UserRead[]>('/users/')

const columns = [
  { key: 'email', label: 'Email' },
  { key: 'full_name', label: 'Full Name' },
  { key: 'is_active', label: 'Status' },
  { key: 'is_superuser', label: 'Role' },
  { key: 'actions', label: '' },
]

// Create / Edit
const modalOpen = ref(false)
const editingUser = ref<UserRead | null>(null)

function openCreate() {
  editingUser.value = null
  modalOpen.value = true
}
function openEdit(user: UserRead) {
  editingUser.value = user
  modalOpen.value = true
}

// Delete
const deleteModalOpen = ref(false)
const deletingUser = ref<UserRead | null>(null)
const deleting = ref(false)

function confirmDelete(user: UserRead) {
  deletingUser.value = user
  deleteModalOpen.value = true
}

async function executeDelete() {
  if (!deletingUser.value) return
  deleting.value = true
  try {
    await apiFetch(`/users/${deletingUser.value.id}`, { method: 'DELETE' })
    deleteModalOpen.value = false
    await refresh()
  }
  finally {
    deleting.value = false
  }
}
</script>
