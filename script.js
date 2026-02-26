document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('widget-toggle-btn');
    const closeBtn = document.getElementById('widget-close-btn');
    const widgetContainer = document.getElementById('university-widget-container');
    const sendBtn = document.getElementById('widget-send-btn');
    const widgetInput = document.getElementById('widget-input');
    const widgetBody = document.querySelector('.widget-body');

    let isWidgetOpen = false;

    // Toggle widget visibility
    const toggleWidget = () => {
        isWidgetOpen = !isWidgetOpen;
        if (isWidgetOpen) {
            widgetContainer.classList.remove('widget-hidden');
            widgetContainer.classList.add('widget-visible');
            // Remove pulse animation when opened
            toggleBtn.classList.remove('pulse-anim');
            // Auto focus input
            setTimeout(() => widgetInput.focus(), 300);
        } else {
            widgetContainer.classList.remove('widget-visible');
            widgetContainer.classList.add('widget-hidden');
        }
    };

    toggleBtn.addEventListener('click', toggleWidget);
    closeBtn.addEventListener('click', toggleWidget);

    // Handle sending message
    const sendMessage = () => {
        const text = widgetInput.value.trim();
        if (!text) return;

        // Add user message
        const userMsg = document.createElement('div');
        userMsg.classList.add('message', 'user-message');
        userMsg.textContent = text;
        widgetBody.appendChild(userMsg);

        // Clear input and scroll to bottom
        widgetInput.value = '';
        widgetBody.scrollTop = widgetBody.scrollHeight;

        // Simulate thinking and system response
        setTimeout(() => {
            const sysMsg = document.createElement('div');
            sysMsg.classList.add('message', 'system-message');
            sysMsg.textContent = "I'm a demo assistant. I've received your query about: " + text;
            widgetBody.appendChild(sysMsg);
            widgetBody.scrollTop = widgetBody.scrollHeight;
        }, 800);
    };

    sendBtn.addEventListener('click', sendMessage);

    // Send on Enter key
    widgetInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
