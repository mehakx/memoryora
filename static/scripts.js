// Voice-only ORA Wellness Agent with Behavioral Learning
// Enhanced for pure voice-to-voice conversation

let isListening = false;
let recognition = null;
let currentAudio = null;
let startTime = Date.now();
let timerInterval;

// Timer functionality
function updateTimer() {
    const elapsed = Date.now() - startTime;
    const minutes = Math.floor(elapsed / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        timerElement.textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

function startTimer() {
    startTime = Date.now();
    timerInterval = setInterval(updateTimer, 1000);
}

// Initialize speech recognition
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            console.log('🎤 Speech recognition started');
            isListening = true;
            updateMicrophoneButton(true);
            updateStatus('👂 Listening...');
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            console.log('🗣️ User said:', transcript);
            
            updateStatus('🤔 ORA is thinking...');
            sendToOraAPI(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('❌ Speech recognition error:', event.error);
            updateStatus('❌ Could not hear you clearly. Try again.');
            resetMicrophone();
        };
        
        recognition.onend = function() {
            console.log('🎤 Speech recognition ended');
            isListening = false;
            updateMicrophoneButton(false);
        };
        
        console.log('✅ Speech recognition initialized');
    } else {
        console.error('❌ Speech recognition not supported');
        updateStatus('❌ Voice not supported in this browser');
    }
}

// Send user input to ORA API (Make.com webhook)
function sendToOraAPI(userInput) {
    console.log('📤 Sending to ORA API:', userInput);
    
    // REPLACE THIS WITH YOUR ACTUAL MAKE.COM WEBHOOK URL
    const webhookURL = 'https://hook.eu2.make.com/YOUR_WEBHOOK_URL_HERE';
    
    const payload = {
        message: userInput,
        timestamp: new Date().toISOString(),
        user_id: 'user_' + Date.now() // Simple user ID for now
    };
    
    fetch(webhookURL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => {
        console.log('📥 Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📥 Response received:', data);
        handleOraResponse(data);
    })
    .catch(error => {
        console.error('❌ Error calling ORA API:', error);
        updateStatus('❌ Connection error. Please try again.');
        resetMicrophone();
    });
}

// Handle ORA's response
function handleOraResponse(responseData) {
    console.log("📥 Raw response received:", responseData);
    console.log("📊 Response type:", typeof responseData);
    console.log("🔍 Response keys:", Object.keys(responseData || {}));
    
    // Enhanced audio URL detection
    let audioUrl = "";
    
    // Try different possible paths for the audio URL
    if (responseData) {
        audioUrl = responseData.audio_url || 
                  responseData.audioUrl || 
                  responseData.Audio_File || 
                  responseData.audio_file ||
                  responseData.audioFile ||
                  (responseData.data && responseData.data.audio_url) ||
                  "";
    }
    
    console.log('🎵 Searching for audio URL...');
    console.log('🎵 Found audio URL:', audioUrl);
    
    // AUTO-PLAY THE AUDIO (Voice-only response)
    if (audioUrl) {
        console.log("🔊 Playing audio:", audioUrl);
        
        // Update status to show ORA is speaking
        updateStatus('🔊 ORA is speaking...');
        showSpeakingIndicator();
        
        // Stop any currently playing audio
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
        }
        
        currentAudio = new Audio(audioUrl);
        
        // Enhanced autoplay with better error handling
        const playAudio = () => {
            return currentAudio.play().then(() => {
                console.log("✅ Audio playing successfully");
                return true;
            }).catch(error => {
                console.error("❌ Audio autoplay blocked:", error);
                return false;
            });
        };
        
        // Try to play immediately
        playAudio().then(success => {
            if (!success) {
                // Autoplay failed, create a more prominent play button
                updateStatus('🔊 Tap anywhere to hear ORA');
                
                // Make the entire interface clickable to play audio
                const playOverlay = document.createElement('div');
                playOverlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                    cursor: pointer;
                `;
                
                const playButton = document.createElement('div');
                playButton.innerHTML = `
                    <div style="
                        background: #ef4444;
                        color: white;
                        padding: 2rem 3rem;
                        border-radius: 20px;
                        font-size: 1.5rem;
                        text-align: center;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                        animation: pulse 2s infinite;
                    ">
                        🔊 Tap to hear ORA's response
                    </div>
                `;
                
                playOverlay.appendChild(playButton);
                document.body.appendChild(playOverlay);
                
                // Click anywhere to play
                playOverlay.onclick = () => {
                    currentAudio.play().then(() => {
                        document.body.removeChild(playOverlay);
                        updateStatus('🔊 ORA is speaking...');
                        showSpeakingIndicator();
                    }).catch(e => {
                        console.error("Failed to play audio:", e);
                        updateStatus('❌ Could not play audio');
                        document.body.removeChild(playOverlay);
                        hideSpeakingIndicator();
                        resetMicrophone();
                    });
                };
            }
        });
        
        // When audio ends, reset to ready state
        currentAudio.addEventListener('ended', () => {
            console.log("🔊 Audio playback completed");
            updateStatus('✨ Ready to listen again');
            hideSpeakingIndicator();
            resetMicrophone();
        });
        
        // Handle audio errors
        currentAudio.addEventListener('error', (e) => {
            console.error("❌ Audio playback error:", e);
            updateStatus('❌ Could not play response');
            hideSpeakingIndicator();
            resetMicrophone();
        });
        
    } else {
        // If no audio URL, show error and log the full response
        console.log("❌ No audio URL found in response");
        console.log("📋 Full response structure:", JSON.stringify(responseData, null, 2));
        updateStatus('❌ No voice response received');
        resetMicrophone();
    }
}

// UI Helper Functions
function updateStatus(text) {
    const statusElement = document.getElementById('statusText');
    if (statusElement) {
        statusElement.textContent = text;
    }
    console.log('📱 Status updated:', text);
}

function updateMicrophoneButton(listening) {
    const micButton = document.getElementById('micButton');
    if (micButton) {
        if (listening) {
            micButton.classList.add('listening');
        } else {
            micButton.classList.remove('listening');
        }
    }
}

function showSpeakingIndicator() {
    const indicator = document.getElementById('speakingIndicator');
    if (indicator) {
        indicator.classList.add('active');
    }
}

function hideSpeakingIndicator() {
    const indicator = document.getElementById('speakingIndicator');
    if (indicator) {
        indicator.classList.remove('active');
    }
}

function resetMicrophone() {
    isListening = false;
    updateMicrophoneButton(false);
    if (recognition) {
        recognition.abort();
    }
}

// Start listening function
function startListening() {
    if (!recognition) {
        console.error('❌ Speech recognition not initialized');
        updateStatus('❌ Voice recognition not available');
        return;
    }
    
    if (isListening) {
        console.log('🛑 Stopping listening');
        recognition.stop();
        resetMicrophone();
        updateStatus('✨ Ready to listen');
        return;
    }
    
    console.log('🎤 Starting to listen');
    recognition.start();
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ORA Voice Interface Loading...');
    
    // Start the timer
    startTimer();
    
    // Initialize speech recognition
    initializeSpeechRecognition();
    
    // Set up button event listeners
    const micButton = document.getElementById('micButton');
    if (micButton) {
        micButton.addEventListener('click', startListening);
    }
    
    const mainButton = document.getElementById('mainButton');
    if (mainButton) {
        mainButton.addEventListener('click', startListening);
    }
    
    // Set initial status
    updateStatus('✨ Ready to listen');
    
    console.log('✅ ORA Voice Interface Ready!');
});

// Export functions for external use
window.oraVoice = {
    startListening,
    updateStatus,
    showSpeakingIndicator,
    hideSpeakingIndicator
};







