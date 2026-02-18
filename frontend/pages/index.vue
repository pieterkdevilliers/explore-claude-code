<script setup lang="ts">
// auth.global.ts will redirect unauthenticated visitors to /login.
// Authenticated visitors landing on / are sent to the dashboard.
await navigateTo('/dashboard', { replace: true })
</script>
