document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const form = document.getElementById('generate-form');
    const promptInput = document.getElementById('prompt');
    const styleSelect = document.getElementById('style-select');
    const negativePromptInput = document.getElementById('negative-prompt');
    const ratioBtns = document.querySelectorAll('.ratio-btn');
    const guidanceScale = document.getElementById('guidance-scale');
    const guidanceVal = document.getElementById('guidance-val');
    const magicDiceBtn = document.getElementById('magic-dice-btn');
    
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const btnIcon = generateBtn.querySelector('i');
    const loaderSpinner = generateBtn.querySelector('.loader-spinner');
    
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const imageDisplay = document.getElementById('image-display');
    const generatedImage = document.getElementById('generated-image');
    const downloadLink = document.getElementById('download-link');
    
    const historyTrack = document.getElementById('history-track');
    const clearHistoryBtn = document.getElementById('clear-history');
    const toastContainer = document.getElementById('toast-container');

    // State
    let currentAspectRatio = '1:1';
    const MAX_HISTORY = 10;

    // Magic Prompts
    const magicPrompts = [
        "A hyper-realistic majestic dragon perched on a glowing crystal peak, cinematic lighting, 8k, extremely detailed",
        "A cyberpunk street market in the rain at night, neon signs reflecting in puddles, bustling crowds, futuristic",
        "A serene ancient temple hidden deep in a bioluminescent forest, misty atmosphere, magical glowing plants",
        "An astronaut floating in space looking at a shattered Earth, dramatic lighting, high contrast, sci-fi masterpiece",
        "A cozy cabin interior with a roaring fireplace during a blizzard, warm orange glow, extremely cozy, detailed textures"
    ];

    // Initialization
    loadHistory();

    // Event Listeners
    guidanceScale.addEventListener('input', (e) => {
        guidanceVal.textContent = e.target.value;
    });

    ratioBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            ratioBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAspectRatio = btn.dataset.ratio;
        });
    });

    magicDiceBtn.addEventListener('click', () => {
        const randomPrompt = magicPrompts[Math.floor(Math.random() * magicPrompts.length)];
        promptInput.value = randomPrompt;
        promptInput.focus();
        showToast('Magic prompt applied!', 'success');
    });

    clearHistoryBtn.addEventListener('click', () => {
        localStorage.removeItem('imaginai_history');
        renderHistory([]);
        showToast('History cleared.', 'success');
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const prompt = promptInput.value.trim();
        if (!prompt) return;

        const payload = {
            prompt: prompt,
            style: styleSelect.value,
            aspect_ratio: currentAspectRatio,
            negative_prompt: negativePromptInput.value.trim(),
            guidance_scale: parseFloat(guidanceScale.value)
        };

        setLoadingState(true);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                displayImage(data.image_data, prompt);
                saveToHistory(data.image_data, prompt);
                showToast('Image generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to generate image');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast(error.message, 'error');
            showResult('empty'); // Reset canvas if error
        } finally {
            setLoadingState(false);
        }
    });

    // Functions
    function displayImage(base64Data, prompt) {
        generatedImage.src = base64Data;
        downloadLink.href = base64Data;
        const safePrompt = prompt.slice(0, 20).replace(/[^a-z0-9]/gi, '_').toLowerCase();
        downloadLink.download = `imaginAI_${safePrompt}.png`;
        showResult('image');
    }

    function setLoadingState(isLoading) {
        if (isLoading) {
            generateBtn.disabled = true;
            btnText.textContent = 'Generating...';
            btnIcon.style.display = 'none';
            loaderSpinner.style.display = 'block';
            showResult('loading');
        } else {
            generateBtn.disabled = false;
            btnText.textContent = 'Generate';
            btnIcon.style.display = 'inline-block';
            loaderSpinner.style.display = 'none';
        }
    }

    function showResult(state) {
        emptyState.style.display = 'none';
        loadingState.style.display = 'none';
        imageDisplay.style.display = 'none';

        if (state === 'empty') emptyState.style.display = 'block';
        else if (state === 'loading') loadingState.style.display = 'block';
        else if (state === 'image') imageDisplay.style.display = 'flex';
    }

    // History Functions
    function saveToHistory(imageData, prompt) {
        let history = getHistory();
        history.unshift({ image: imageData, prompt: prompt, id: Date.now() });
        if (history.length > MAX_HISTORY) history.pop();
        localStorage.setItem('imaginai_history', JSON.stringify(history));
        renderHistory(history);
    }

    function getHistory() {
        const h = localStorage.getItem('imaginai_history');
        return h ? JSON.parse(h) : [];
    }

    function loadHistory() {
        renderHistory(getHistory());
    }

    function renderHistory(history) {
        historyTrack.innerHTML = '';
        if (history.length === 0) {
            historyTrack.innerHTML = '<p class="no-history-text">No recent images.</p>';
            return;
        }

        history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.title = item.prompt;
            div.innerHTML = `<img src="${item.image}" alt="History item">`;
            div.addEventListener('click', () => {
                displayImage(item.image, item.prompt);
                promptInput.value = item.prompt;
            });
            historyTrack.appendChild(div);
        });
    }

    // Toast Notifications
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        toast.innerHTML = `<i class="fas ${icon}"></i> <span>${message}</span>`;
        
        toastContainer.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
