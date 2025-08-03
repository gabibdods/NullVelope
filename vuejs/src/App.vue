<template>
    <div>
        <h1 class="text-xl font-bold text-center mb-8">Inbox</h1>
        <ul>
            <li v-for="email in emails" :key="email._id" class="mt-2 border p-2">
                <p><strong>From:</strong> {{ email.from }}</p>
                <p><strong>Subject:</strong> {{ email.subject }}</p>
                <p><strong>Body:</strong> {{ email.txt }}</p>
            </li>
        </ul>
    </div>
</template>

<script setup lang="ts">
    import { ref, onMounted } from 'vue'
    import axios from 'axios'

    const emails = ref([])
    onMounted(async () => {
        const res = await axios.get('http://localhost:8000/inbox/{inboxId}')
        emails.value = res.data
    })
</script>

<style scoped>

</style>