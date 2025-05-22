<template>
  <button
    :disabled="isLoading"
    @click="playTTS"
    class="tts-btn"
    :style="{ background: isLoading ? gruvbox.bg1 : gruvbox.bg0, color: gruvbox.fg1 }"
    aria-label="Play audio"
  >
    <span v-if="isLoading">🔄</span>
    <span v-else>🔊 Listen</span>
  </button>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';

// Gruvbox theme colors (customize as needed)
const gruvbox = {
  bg0: '#282828',
  bg1: '#3c3836',
  fg1: '#ebdbb2',
};

const props = defineProps<{ text: string }>();
const isLoading = ref(false);
let audio: HTMLAudioElement | null = null;

async function playTTS() {
  if (!props.text || isLoading.value) return;
  isLoading.value = true;
  try {
    const response = await fetch('/api/tts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: props.text })
    });
    if (!response.ok) throw new Error('TTS request failed');
    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    audio = new Audio(audioUrl);
    audio.onended = () => { isLoading.value = false; };
    audio.onerror = () => { isLoading.value = false; };
    audio.play();
  } catch (e) {
    isLoading.value = false;
    // Optionally show error to user
  }
}

onUnmounted(() => {
  if (audio) {
    audio.pause();
    audio = null;
  }
});
</script>

<style scoped>
.tts-btn {
  border: none;
  border-radius: 4px;
  padding: 0.3em 0.8em;
  font-size: 1em;
  cursor: pointer;
  margin-left: 0.5em;
  transition: background 0.2s;
}
.tts-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
