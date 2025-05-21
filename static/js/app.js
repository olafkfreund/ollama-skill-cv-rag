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
            
            // Clear input field
            userInput.value = '';
            
            // Set loading state
            isLoading.value = true;
            
            // Add a temporary loading message
            const loadingMessageId = Date.now() + 1;
            messages.value.push({
                id: loadingMessageId,
                role: 'assistant',
                content: 'Thinking...',
                isLoading: true,
                timestamp: new Date()
            });
            
            // Focus input for next message
            if (inputField.value) {
                inputField.value.focus();
            }

            try {
                // Make request to API
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ query: trimmedInput })
                });

                if (!response.ok) {
                    throw new Error(`Server responded with status: ${response.status}`);
                }

                const data = await response.json();
                
                // Remove loading message
                const index = messages.value.findIndex(m => m.id === loadingMessageId);
                if (index !== -1) {
                    messages.value.splice(index, 1);
                }
                
                // Add the response message
                messages.value.push({
                    id: Date.now() + 2,
                    role: 'assistant',
                    content: data.response || 'I\'m sorry, I couldn\'t process that query.',
                    timestamp: new Date()
                });
            } catch (error) {
                console.error('Error sending message:', error);
                
                // Remove loading message
                const index = messages.value.findIndex(m => m.id === loadingMessageId);
                if (index !== -1) {
                    messages.value.splice(index, 1);
                }
                
                // Add an error message
                errorMessage.value = `Error: ${error.message}`;
                messages.value.push({
                    id: Date.now() + 2,
                    role: 'assistant',
                    content: 'Sorry, there was an error processing your request. Please try again later.',
                    timestamp: new Date()
                });
            } finally {
                isLoading.value = false;
                
                // Focus back on input field
                setTimeout(() => {
                    if (inputField.value) {
                        inputField.value.focus();
                    }
                }, 100);
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
