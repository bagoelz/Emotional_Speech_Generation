/**
 * Emotional TTS Frontend JavaScript
 * Modern, interactive interface for speech synthesis
 */

class EmotionalTTSApp {
    constructor() {
        this.apiBase = '';
        this.currentAudio = null;
        this.isProcessing = false;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadSystemStatus();
        this.loadVoices();
        this.updateCharCounter();
        this.setupSliders();
        this.allVoices = []; // Store all voices for filtering
    }

    bindEvents() {
        // Main controls
        document.getElementById('synthesizeBtn').addEventListener('click', () => this.synthesizeSpeech());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearForm());
        
        // Input events
        document.getElementById('textInput').addEventListener('input', () => this.updateCharCounter());
        document.getElementById('intensitySlider').addEventListener('input', () => this.updateIntensityDisplay());
        document.getElementById('speedSlider').addEventListener('input', () => this.updateSpeedDisplay());
        document.getElementById('styleSelect').addEventListener('change', () => this.onStyleChange());
        document.getElementById('engineSelect').addEventListener('change', () => this.onEngineChange());
        document.getElementById('genderFilter').addEventListener('change', () => this.filterVoicesByGender());
        document.getElementById('voiceSelect').addEventListener('change', () => this.onVoiceChange());
        document.getElementById('previewVoiceBtn').addEventListener('click', () => this.previewVoice());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // Prevent form submission on Enter
        document.getElementById('textInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.synthesizeSpeech();
            }
        });
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            // Determine system status based on available engines
            const systemStatus = status.coqui_available || status.pyttsx3_available ? 'online' : 'offline';
            document.getElementById('systemStatus').textContent = systemStatus;
            document.getElementById('systemStatus').className = `status-value ${systemStatus}`;
            
            // Build engines list
            const engines = [];
            if (status.coqui_available) engines.push('Coqui TTS');
            if (status.pyttsx3_available) engines.push('pyttsx3');
            
            document.getElementById('availableEngines').textContent = engines.join(', ') || 'None';
            
            // Update engine select options based on availability
            this.updateEngineOptions([
                { name: 'coqui', available: status.coqui_available },
                { name: 'pyttsx3', available: status.pyttsx3_available }
            ]);
            
        } catch (error) {
            console.error('Failed to load system status:', error);
            document.getElementById('systemStatus').textContent = 'Error';
            document.getElementById('availableEngines').textContent = 'Unknown';
        }
    }

    async loadVoices() {
        try {
            const response = await fetch('/api/voices');
            const voices = await response.json();
            
            if (!voices.success) {
                console.error('Failed to load voices:', voices.error);
                return;
            }
            
            // Store all voices for filtering
            this.allVoices = [];
            
            // Process Coqui voices
            if (voices.coqui && voices.coqui.length > 0) {
                voices.coqui.forEach(voice => {
                    this.allVoices.push({
                        ...voice,
                        value: `coqui:${voice.id}`,
                        displayName: `${voice.name} (Coqui TTS)`,
                        group: 'Coqui TTS Voices'
                    });
                });
            }
            
            // Process pyttsx3 voices
            if (voices.pyttsx3 && voices.pyttsx3.length > 0) {
                voices.pyttsx3.forEach(voice => {
                    this.allVoices.push({
                        ...voice,
                        value: `pyttsx3:${voice.id}`,
                        displayName: voice.description || `${voice.name} (System)`,
                        group: 'System Voices'
                    });
                });
            }
            
            // Initial population of voice select
            this.filterVoicesByGender();
            
        } catch (error) {
            console.error('Failed to load voices:', error);
        }
    }

    filterVoicesByGender() {
        const genderFilter = document.getElementById('genderFilter').value;
        const voiceSelect = document.getElementById('voiceSelect');
        
        // Clear current options
        voiceSelect.innerHTML = '<option value="">Default Voice</option>';
        
        // Filter voices by gender
        const filteredVoices = this.allVoices.filter(voice => {
            if (genderFilter === 'all') return true;
            return voice.gender === genderFilter;
        });
        
        // Group voices by engine
        const groupedVoices = {};
        filteredVoices.forEach(voice => {
            if (!groupedVoices[voice.group]) {
                groupedVoices[voice.group] = [];
            }
            groupedVoices[voice.group].push(voice);
        });
        
        // Add grouped options to select
        Object.keys(groupedVoices).forEach(groupName => {
            const optgroup = document.createElement('optgroup');
            optgroup.label = groupName;
            
            groupedVoices[groupName].forEach(voice => {
                const option = document.createElement('option');
                option.value = voice.value;
                option.textContent = voice.displayName;
                option.dataset.gender = voice.gender;
                option.dataset.language = voice.language;
                option.dataset.description = voice.description;
                optgroup.appendChild(option);
            });
            
            voiceSelect.appendChild(optgroup);
        });
        
        // Update voice info if a voice is selected
        this.onVoiceChange();
    }

    onVoiceChange() {
        const voiceSelect = document.getElementById('voiceSelect');
        const voiceInfo = document.getElementById('voiceInfo');
        const voiceDetails = voiceInfo.querySelector('.voice-details');
        
        if (voiceSelect.value && voiceSelect.selectedOptions[0].dataset.description) {
            const selectedOption = voiceSelect.selectedOptions[0];
            const gender = selectedOption.dataset.gender;
            const language = selectedOption.dataset.language;
            const description = selectedOption.dataset.description;
            
            voiceDetails.innerHTML = `
                <i class="fas fa-info-circle"></i> 
                ${description}
                <br>
                <i class="fas fa-${gender === 'female' ? 'venus' : gender === 'male' ? 'mars' : 'genderless'}"></i> 
                ${gender.charAt(0).toUpperCase() + gender.slice(1)} • 
                <i class="fas fa-globe"></i> ${language}
            `;
            voiceInfo.style.display = 'block';
        } else {
            voiceInfo.style.display = 'none';
        }
    }

    updateEngineOptions(engines) {
        const engineSelect = document.getElementById('engineSelect');
        const currentValue = engineSelect.value;
        
        // Clear current options except auto
        engineSelect.innerHTML = '<option value="auto">Auto (Best Available)</option>';
        
        engines.forEach(engine => {
            if (engine.available) {
                const option = document.createElement('option');
                option.value = engine.name;
                option.textContent = `${engine.name} (${engine.available ? 'Available' : 'Unavailable'})`;
                engineSelect.appendChild(option);
            }
        });
        
        // Restore previous selection if still valid
        if (Array.from(engineSelect.options).some(opt => opt.value === currentValue)) {
            engineSelect.value = currentValue;
        }
    }

    updateCharCounter() {
        const textInput = document.getElementById('textInput');
        const charCount = document.getElementById('charCount');
        const length = textInput.value.length;
        
        charCount.textContent = length;
        charCount.style.color = length > 4500 ? '#ff6b6b' : length > 4000 ? '#ffe066' : '#7f8c8d';
    }

    updateIntensityDisplay() {
        const slider = document.getElementById('intensitySlider');
        const display = document.getElementById('intensityValue');
        display.textContent = slider.value;
        
        // Visual feedback
        const percentage = slider.value / 100;
        slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percentage * 100}%, #e1e8ed ${percentage * 100}%, #e1e8ed 100%)`;
    }

    updateSpeedDisplay() {
        const slider = document.getElementById('speedSlider');
        const display = document.getElementById('speedValue');
        display.textContent = parseFloat(slider.value).toFixed(1);
        
        // Visual feedback
        const percentage = (slider.value - 0.5) / 1.5; // Normalize 0.5-2.0 to 0-1
        slider.style.background = `linear-gradient(to right, #667eea 0%, #667eea ${percentage * 100}%, #e1e8ed ${percentage * 100}%, #e1e8ed 100%)`;
    }

    setupSliders() {
        this.updateIntensityDisplay();
        this.updateSpeedDisplay();
    }

    onStyleChange() {
        const style = document.getElementById('styleSelect').value;
        const intensitySlider = document.getElementById('intensitySlider');
        
        // Auto-adjust intensity based on style
        const styleIntensities = {
            'neutral': 30,
            'enthusiastic': 80,
            'somber': 40,
            'confident': 70,
            'authoritative': 85
        };
        
        if (styleIntensities[style]) {
            intensitySlider.value = styleIntensities[style];
            this.updateIntensityDisplay();
        }
        
        // Add visual feedback
        this.showToast(`Style changed to: ${style}`, 'info');
    }

    onEngineChange() {
        const engine = document.getElementById('engineSelect').value;
        this.loadVoices(); // Reload voices for selected engine
        this.showToast(`Engine preference: ${engine}`, 'info');
    }

    async previewVoice() {
        const voiceSelect = document.getElementById('voiceSelect');
        const engineSelect = document.getElementById('engineSelect');
        const previewBtn = document.getElementById('previewVoiceBtn');
        
        const selectedVoice = voiceSelect.value;
        const selectedEngine = engineSelect.value;
        
        if (!selectedVoice) {
            this.showToast('Please select a voice to preview', 'warning');
            return;
        }
        
        // Disable button and show loading state
        previewBtn.disabled = true;
        previewBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        try {
            const response = await fetch('/api/preview-voice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    voice_id: selectedVoice,
                    engine: selectedEngine
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Play the preview audio
                const audio = new Audio(result.audio_url);
                audio.play().catch(e => {
                    console.error('Error playing preview:', e);
                    this.showToast('Error playing voice preview', 'error');
                });
                
                this.showToast('Voice preview generated successfully', 'success');
            } else {
                this.showToast(`Preview failed: ${result.error}`, 'error');
            }
            
        } catch (error) {
            console.error('Preview error:', error);
            this.showToast('Failed to generate voice preview', 'error');
        } finally {
            // Re-enable button
            previewBtn.disabled = false;
            previewBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    }

    async synthesizeSpeech() {
        if (this.isProcessing) return;
        
        const textInput = document.getElementById('textInput');
        const text = textInput.value.trim();
        
        if (!text) {
            this.showError('Please enter some text to synthesize');
            textInput.focus();
            return;
        }
        
        if (text.length > 5000) {
            this.showError('Text is too long. Maximum 5000 characters allowed.');
            return;
        }
        
        this.isProcessing = true;
        this.showLoading('Generating speech...');
        
        try {
            const requestData = {
                text: text,
                style: document.getElementById('styleSelect').value,
                intensity: parseInt(document.getElementById('intensitySlider').value),
                engine: document.getElementById('engineSelect').value,
                voice: document.getElementById('voiceSelect').value || null,
                speed: parseFloat(document.getElementById('speedSlider').value)
            };
            
            const startTime = Date.now();
            
            const response = await fetch('/api/synthesize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.detail || 'Synthesis failed');
            }
            
            if (result.success) {
                this.displayResult(result);
                this.showToast('Speech generated successfully!', 'success');
            } else {
                throw new Error(result.message || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Synthesis error:', error);
            this.showError(`Failed to generate speech: ${error.message}`);
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }

    displayResult(result) {
        const resultsSection = document.getElementById('resultsSection');
        const audioPlayer = document.getElementById('audioPlayer');
        const downloadLink = document.getElementById('downloadLink');
        
        // Update audio player
        audioPlayer.src = result.audio_url;
        audioPlayer.load();
        
        // Update download link
        downloadLink.href = result.audio_url;
        downloadLink.download = `speech_${Date.now()}.wav`;
        
        // Update metadata
        if (result.metadata) {
            document.getElementById('processingTime').textContent = 
                `${result.processing_time?.toFixed(2) || 'N/A'}s`;
            document.getElementById('engineUsed').textContent = 
                result.engine_used || 'Unknown';
            document.getElementById('audioDuration').textContent = 
                result.metadata.audio_duration ? `${result.metadata.audio_duration.toFixed(2)}s` : 'N/A';
            document.getElementById('fileSize').textContent = 
                result.metadata.file_size ? this.formatFileSize(result.metadata.file_size) : 'N/A';
        }
        
        // Show results section with animation
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
        // Auto-play if user prefers
        setTimeout(() => {
            if (document.getElementById('autoPlayCheck')?.checked) {
                audioPlayer.play().catch(e => console.log('Auto-play prevented by browser'));
            }
        }, 500);
    }

    clearForm() {
        document.getElementById('textInput').value = '';
        document.getElementById('styleSelect').value = 'neutral';
        document.getElementById('intensitySlider').value = 50;
        document.getElementById('speedSlider').value = 1.0;
        document.getElementById('engineSelect').value = 'auto';
        document.getElementById('voiceSelect').value = '';
        
        this.updateCharCounter();
        this.updateIntensityDisplay();
        this.updateSpeedDisplay();
        
        // Hide results
        document.getElementById('resultsSection').style.display = 'none';
        
        // Stop current audio
        if (this.currentAudio) {
            this.currentAudio.pause();
            this.currentAudio = null;
        }
        
        this.showToast('Form cleared', 'info');
    }

    showLoading(message = 'Processing...', details = 'Please wait while we process your request') {
        const overlay = document.getElementById('loadingOverlay');
        const detailsElement = document.getElementById('loadingDetails');
        
        overlay.querySelector('.loading-content p').textContent = message;
        detailsElement.textContent = details;
        overlay.style.display = 'flex';
        
        // Disable form elements
        this.toggleFormElements(false);
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
        this.toggleFormElements(true);
    }

    toggleFormElements(enabled) {
        const elements = [
            'textInput', 'styleSelect', 'intensitySlider', 
            'speedSlider', 'engineSelect', 'voiceSelect', 
            'synthesizeBtn', 'clearBtn'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.disabled = !enabled;
            }
        });
    }

    showError(message) {
        const errorDiv = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        errorText.textContent = message;
        errorDiv.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => this.hideError(), 5000);
    }

    hideError() {
        document.getElementById('errorMessage').style.display = 'none';
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${this.getToastIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        // Style the toast
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: this.getToastColor(type),
            color: 'white',
            padding: '12px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            zIndex: '1001',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '14px',
            fontWeight: '500',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease'
        });
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    getToastIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    getToastColor(type) {
        const colors = {
            'success': '#4ecdc4',
            'error': '#ff6b6b',
            'warning': '#ffe066',
            'info': '#667eea'
        };
        return colors[type] || '#667eea';
    }

    handleKeyboard(e) {
        // Ctrl+Enter to synthesize
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            this.synthesizeSpeech();
        }
        
        // Escape to clear/stop
        if (e.key === 'Escape') {
            if (this.isProcessing) {
                // Could implement cancellation here
            } else {
                this.hideError();
            }
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Global functions for HTML event handlers
function hideError() {
    app.hideError();
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new EmotionalTTSApp();
    
    // Add some example texts for quick testing
    const examples = [
        "Hello! This is an example of emotional speech synthesis.",
        "Welcome to our advanced text-to-speech system with emotional control.",
        "The weather today is absolutely beautiful, perfect for a walk in the park!",
        "I'm sorry to inform you that the meeting has been postponed until next week.",
        "Congratulations on your outstanding achievement! You should be very proud."
    ];
    
    // Add example button (optional)
    const exampleBtn = document.createElement('button');
    exampleBtn.textContent = '💡 Try Example';
    exampleBtn.className = 'btn btn-secondary';
    exampleBtn.style.marginLeft = '10px';
    exampleBtn.onclick = () => {
        const randomExample = examples[Math.floor(Math.random() * examples.length)];
        document.getElementById('textInput').value = randomExample;
        app.updateCharCounter();
        app.showToast('Example text loaded!', 'info');
    };
    
    document.querySelector('.action-buttons').appendChild(exampleBtn);
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}