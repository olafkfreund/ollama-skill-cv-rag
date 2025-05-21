<template>
  <div class="chat-message">
    <span class="message-text">{{ message.text }}</span>
    <TTSPlayer :text="message.text" />
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import TTSPlayer from '@/components/TTSPlayer.vue';

const props = defineProps<{ message: { text: string } }>();
</script>

<style scoped>
.chat-message {
  display: flex;
  align-items: center;
  margin-bottom: 0.5em;
  background: #282828; /* Gruvbox bg0 */
  color: #ebdbb2;      /* Gruvbox fg1 */
  padding: 0.5em 1em;
  border-radius: 6px;
}
.message-text {
  flex: 1;
  word-break: break-word;
}
</style>
