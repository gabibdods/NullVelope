<template>
  <div class="container">
    <h1>Temporary Email</h1>
    <p>Click "Generate" to create a disposable inbox, then send emails to that address to test.</p>

    <div class="toolbar">
      <button @click="genAddress" :disabled="busy">Generate</button>
      <strong v-if="address">{{ address }}</strong>
      <button v-if="address" @click="refresh" :disabled="busy">Refresh</button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <hr />

    <div class="split">
      <section>
        <h3>Inbox</h3>
        <div v-if="!messages.length && address" class="muted">
          No messages yet! Send a mail to <code>{{ address }}</code> and refresh.
        </div>
        <ul class="list">
          <li
              v-for="m in messages"
              :key="m.id"
              class="item"
              @click="openMessage(m.id)"
          >
            <div class="subj"><strong>{{ m.subject || '(no subject)' }}</strong></div>
            <div class="meta">
              <small>from {{ m.from_ }} — {{ new Date(m.received_at).toLocaleString() }}</small>
            </div>
          </li>
        </ul>
      </section>

      <section>
        <h3>Message</h3>
        <div v-if="selectedMessage">
          <p class="subj"><strong>{{ selectedMessage.subject || '(no subject)' }}</strong></p>
          <p>From: {{ selectedMessage.from_ }}</p>
          <p>To: {{ selectedMessage.to.join(', ') }}</p>
          <p>Received: {{ new Date(selectedMessage.received_at).toLocaleString() }}</p>

          <details open v-if="selectedMessage.text">
            <summary>Text</summary>
            <pre class="pre">{{ selectedMessage.text }}</pre>
          </details>

          <details v-if="selectedMessage.html">
            <summary>HTML</summary>
            <div v-html="selectedMessage.html" class="htmlbox"></div>
          </details>

          <div v-if="selectedMessage.attachments?.length">
            <h4>Attachments</h4>
            <ul>
              <li
                  v-for="a in selectedMessage.attachments"
                  :key="(a.filename || 'file') + ':' + a.size"
              >
                {{ a.filename || '(unnamed)' }} — {{ a.size }} bytes — {{ a.content_type || 'application/octet-stream' }}
                <template v-if="a.content_b64">
                  —
                  <a
                      :href="'data:' + (a.content_type || 'application/octet-stream') + ';base64,' + a.content_b64"
                      :download="a.filename || 'attachment'"
                  >Download</a>
                </template>
                <template v-else>
                  — (too large to store inline)
                </template>
              </li>
            </ul>
          </div>
        </div>
        <div v-else class="muted">Select a message.</div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, type Ref } from 'vue'
  import axios from 'axios'

  const API_BASE = '/api'

  interface NewAddressResponse {
    local_part: string
    address: string
    expires_in_seconds: number
  }
  interface MessagePreview {
    id: string
    subject: string
    from_: string
    received_at: string
    has_attachments: boolean
  }
  interface Attachment {
    filename?: string
    content_type?: string
    size: number
    content_b64?: string
  }
  interface MessageDetail {
    id: string
    subject: string
    from_: string
    to: string[]
    received_at: string
    text: string
    html: string
    attachments: Attachment[]
  }
  function errMsg(e: unknown): string {
    if (axios.isAxiosError(e)) return e.message || 'Request failed'
    if (e instanceof Error) return e.message
    try { return String(e) } catch { return 'Unknown error' }
  }
  const localPart: Ref<string> = ref('')
  const address: Ref<string> = ref('')
  const messages: Ref<MessagePreview[]> = ref([])
  const selectedMessage: Ref<MessageDetail | null> = ref(null)
  const busy: Ref<boolean> = ref(false)
  const error: Ref<string> = ref('')

  const genAddress = async (): Promise<void> => {
    try {
      busy.value = true
      error.value = ''
      const { data } = await axios.post<NewAddressResponse>(`${API_BASE}/addresses`)
      localPart.value = data.local_part
      address.value = data.address
      messages.value = []
      selectedMessage.value = null
    } catch (e) {
      error.value = errMsg(e) || 'Failed to generate address'
    } finally {
      busy.value = false
    }
  }
  const refresh = async (): Promise<void> => {
    if (!localPart.value) return
    try {
      busy.value = true
      error.value = ''
      const { data } = await axios.get<MessagePreview[]>(
          `${API_BASE}/addresses/${encodeURIComponent(localPart.value)}/messages`
      )
      messages.value = data
    } catch (e) {
      error.value = errMsg(e) || 'Failed to load messages'
    } finally {
      busy.value = false
    }
  }
  const openMessage = async (id: string): Promise<void> => {
    try {
      busy.value = true
      error.value = ''
      const { data } = await axios.get<MessageDetail>(`${API_BASE}/messages/${encodeURIComponent(id)}`)
      selectedMessage.value = data
    } catch (e) {
      error.value = errMsg(e) || 'Failed to open message'
    } finally {
      busy.value = false
    }
  }
</script>

<style scoped>
  .container {
    max-width: 960px;
    margin: 2rem auto;
    font-family: system-ui,
    sans-serif;
  }
  .toolbar {
    display: flex;
    gap: .5rem;
    align-items: center;
    margin-bottom: 1rem;
  }
  .split {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1rem;
  }
  .list {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .item {
    cursor: pointer;
    padding: .5rem;
    border-radius: .5rem;
  }
  .item:hover { background: #f3f3f3; }
  .muted { color: #666; }
  .error { color: #c00; }
  .subj { margin: .25rem 0; }
  .pre {
    white-space: pre-wrap;
    border: 1px solid #ddd;
    padding: .5rem;
    border-radius: .5rem;
  }
  .htmlbox {
    border: 1px solid #ddd;
    padding: .5rem;
    border-radius: .5rem;
  }
</style>
