// CV RAG System with Vue.js
const { createApp, ref, computed, onMounted, watch } = Vue;

const app = createApp({
    setup() {
        // Core data
        const messages = ref([]);
        const userInput = ref('');
        const messageContainer = ref(null);
        const inputField = ref(null);
        const isLoading = ref(false);
        const errorMessage = ref('');
        const showScrollIndicator = ref(false);

        // Watch for new messages and scroll to bottom
        watch(messages, () => {
            scrollToBottom();
        }, { deep: true });

        // Watch scroll position to determine if we should show scroll indicator
        const checkScrollPosition = () => {
            if (!messageContainer.value) return;
            
            const { scrollTop, scrollHeight, clientHeight } = messageContainer.value;
            const scrollBottom = scrollHeight - scrollTop - clientHeight;
            
            // Show scroll indicator if we're more than 100px from bottom
            showScrollIndicator.value = scrollBottom > 100;
        };

        // Format the message timestamp
        const formatTime = (timestamp) => {
            const date = new Date(timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        };

        // Markdown rendering for assistant messages
        const renderMarkdown = (mdText) => {
            if (window.marked && window.DOMPurify) {
                return DOMPurify.sanitize(marked.parse(mdText));
            }
            return mdText;
        };

        onMounted(() => {
            // Add a welcome message when the app loads
            messages.value.push({
                id: Date.now(),
                role: 'assistant',
                content: 'Hello! I\'m Olaf\'s AI assistant. I can help you learn about Olaf\'s skills, experience, and qualifications. What would you like to know?',
                timestamp: new Date()
            });
            
            // Add focus to the input field
            if (inputField.value) {
                inputField.value.focus();
            }

            // Add scroll event listener
            if (messageContainer.value) {
                messageContainer.value.addEventListener('scroll', checkScrollPosition);
            }
        });

        const scrollToBottom = () => {
            setTimeout(() => {
                if (messageContainer.value) {
                    messageContainer.value.scrollTop = messageContainer.value.scrollHeight;
                    checkScrollPosition();
                }
            }, 100);
        };

        const sendMessage = async () => {
            // Validate input
            const trimmedInput = userInput.value.trim();
            if (!trimmedInput || isLoading.value) return;

            // Clear any previous error
            errorMessage.value = '';

            // Add user message to chat
            const userMessage = {
                id: Date.now(),
                role: 'user',
                content: trimmedInput,
                timestamp: new Date()
            };
            messages.value.push(userMessage);
            userInput.value = '';
            isLoading.value = true;

            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: userMessage.content })
                });
                const data = await response.json();
                isLoading.value = false;
                if (data.status === 'error' && data.message && data.message.toLowerCase().includes('reindexing')) {
                    messages.value.push({
                        id: Date.now() + 1,
                        role: 'assistant',
                        content: '⏳ The system is currently reindexing the knowledge base. Please try again in a few moments.',
                        timestamp: new Date()
                    });
                    return;
                }
                if (data.status === 'success' && data.data && data.data.answer) {
                    messages.value.push({
                        id: Date.now() + 2,
                        role: 'assistant',
                        content: data.data.answer,
                        timestamp: new Date()
                    });
                } else {
                    messages.value.push({
                        id: Date.now() + 3,
                        role: 'assistant',
                        content: data.message || 'Sorry, something went wrong.',
                        timestamp: new Date()
                    });
                }
            } catch (error) {
                isLoading.value = false;
                messages.value.push({
                    id: Date.now() + 4,
                    role: 'assistant',
                    content: '⚠️ The system is temporarily unavailable. This may be due to reindexing the knowledge base. Please try again in a few moments.',
                    timestamp: new Date()
                });
            }
        };

        return {
            messages,
            userInput,
            sendMessage,
            messageContainer,
            inputField,
            isLoading,
            errorMessage,
            showScrollIndicator,
            scrollToBottom,
            formatTime,
            renderMarkdown // expose to template
        };
    }
});

// Function to play TTS
function playTTS(text) {
    if (!text) return;
    const btn = event?.target;
    if (btn) btn.disabled = true;
    fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    })
        .then(response => {
            if (!response.ok) throw new Error('TTS request failed');
            return response.blob();
        })
        .then(audioBlob => {
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            audio.onended = () => { if (btn) btn.disabled = false; };
            audio.onerror = () => { if (btn) btn.disabled = false; };
            audio.play();
        })
        .catch(() => { if (btn) btn.disabled = false; });
}

// Global Vue component for TTS button
app.component('tts-button', {
    props: ['text'],
    template: `<button class="tts-btn" @click="play" :disabled="loading"><span v-if="loading">🔄</span><span v-else>🔊 Listen</span></button>`,
    data() { return { loading: false }; },
    methods: {
        play() {
            if (!this.text || this.loading) return;
            this.loading = true;
            console.log('[TTS] Sending request to /api/tts:', this.text);
            fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: this.text })
            })
                .then(response => {
                    if (!response.ok) {
                        console.error('[TTS] Response not OK:', response.status, response.statusText);
                        throw new Error('TTS request failed: ' + response.status);
                    }
                    return response.blob();
                })
                .then(audioBlob => {
                    console.log('[TTS] Received audio blob:', audioBlob);
                    const audioUrl = URL.createObjectURL(audioBlob);
                    const audio = new Audio(audioUrl);
                    audio.onended = () => { this.loading = false; };
                    audio.onerror = (e) => {
                        this.loading = false;
                        alert('Audio playback failed.');
                        console.error('[TTS] Audio playback error:', e);
                    };
                    audio.play().catch(e => {
                        this.loading = false;
                        alert('Audio playback failed.');
                        console.error('[TTS] Audio play() error:', e);
                    });
                })
                .catch((err) => {
                    this.loading = false;
                    alert('TTS request failed: ' + err.message);
                    console.error('[TTS] Fetch error:', err);
                });
        }
    }
});

// Patch message rendering to include the TTS button for each assistant message
const origRender = app.config.globalProperties.renderMarkdown;
app.config.globalProperties.renderMarkdown = function(text, message) {
    let html = origRender ? origRender.call(this, text) : text;
    if (message && message.role === 'assistant') {
        html += `<tts-button :text="${JSON.stringify(message.content)}"></tts-button>`;
    }
    return html;
};

app.mount('#app');
