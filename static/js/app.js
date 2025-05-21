// CV RAG System with Vue.js
const { createApp, ref, computed, onMounted, watch } = Vue;

createApp({
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
}).mount('#app');
