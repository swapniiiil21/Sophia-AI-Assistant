$(document).ready(function() {
    // References to new DOM elements for face recognition
    const loadingOverlay = $('#loading-overlay');
    const sophiaActivationStatus = $('#sophia-activation-status');
    const sophiaStatusMessage = $('#sophia-status-message'); // Corrected ID usage for consistency
    const videoContainer = $('#video-container');
    const webcamFeed = $('#webcam-feed')[0]; // Get the native DOM element
    const faceDetectionCanvas = $('#face-detection-canvas')[0];
    const canvasContext = faceDetectionCanvas.getContext('2d');

    let faceDetected = false;
    let stream; // To hold the media stream

    // --- User Name Configuration ---
    // This is set to "Sir" as per your preference.
    let userName = "Sir"; 

    // --- Face Recognition Setup ---
    // IMPORTANT: Ensure your face-api.js models are in this directory: assets/models/
    const MODELS_URL = 'assets/models'; 

    async function loadFaceApiModels() {
        sophiaActivationStatus.text("Loading Face Recognition Models...");
        sophiaStatusMessage.text(""); // Clear any previous status message
        try {
            // Load the tiny face detector model
            await faceapi.nets.tinyFaceDetector.load(MODELS_URL);
            sophiaActivationStatus.text("Models Loaded. Starting Webcam...");
            startWebcam();
        } catch (error) {
            sophiaActivationStatus.text("Error Loading Models.");
            sophiaStatusMessage.text("Please ensure models are in assets/models and refresh.");
            console.error("Error loading face-api models:", error);
            // Fallback: If models fail to load, proceed to activate Sophia after a delay
            console.warn("Face recognition models failed to load. Falling back to timed activation.");
            setTimeout(activateSophiaUI, 5000); // Activate after 5 seconds if face detection fails
        }
    }

    async function startWebcam() {
        try {
            // Request access to the user's webcam
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            webcamFeed.srcObject = stream;
            videoContainer.css('display', 'block'); // Show video container
            sophiaStatusMessage.text("Looking for your face...");

            // Once video stream is loaded and playing, start face detection
            webcamFeed.addEventListener('play', () => {
                // Set canvas dimensions to match video feed
                faceDetectionCanvas.width = webcamFeed.videoWidth;
                faceDetectionCanvas.height = webcamFeed.videoHeight;
                detectFaces();
            });
        } catch (err) {
            sophiaActivationStatus.text("Webcam Access Denied.");
            sophiaStatusMessage.text("Sophia cannot activate without webcam access. Please allow permissions and refresh. Falling back to timed activation.");
            console.error("Error accessing webcam:", err);
            // Fallback: If webcam access is denied, proceed to activate Sophia after a delay
            setTimeout(activateSophiaUI, 5000); // Activate after 5 seconds if webcam is denied
        }
    }

    async function detectFaces() {
        const displaySize = { width: webcamFeed.videoWidth, height: webcamFeed.videoHeight };
        faceapi.matchDimensions(faceDetectionCanvas, displaySize);

        setInterval(async () => {
            if (!webcamFeed.paused && !webcamFeed.ended) {
                const detections = await faceapi.detectAllFaces(webcamFeed, new faceapi.TinyFaceDetectorOptions());

                const resizedDetections = faceapi.resizeResults(detections, displaySize);
                canvasContext.clearRect(0, 0, faceDetectionCanvas.width, faceDetectionCanvas.height);

                if (resizedDetections.length > 0) {
                    // Draw a custom glowing blue circle around the detected face
                    resizedDetections.forEach(detection => {
                        const box = detection.box;
                        const centerX = box.x + box.width / 2;
                        const centerY = box.y + box.height / 2;
                        const radius = Math.max(box.width, box.height) / 1.8; // Adjust radius based on face size

                        canvasContext.beginPath();
                        canvasContext.arc(centerX, centerY, radius, 0, 2 * Math.PI);
                        canvasContext.strokeStyle = '#00eaff'; // Electric blue color
                        canvasContext.lineWidth = 3;
                        canvasContext.shadowColor = '#00eaff';
                        canvasContext.shadowBlur = 15; // Glowing effect
                        canvasContext.stroke();
                        canvasContext.shadowBlur = 0; // Reset shadow for other drawings
                    });

                    if (!faceDetected) {
                        faceDetected = true;
                        sophiaActivationStatus.text("Face Recognized! SOPHIA ACTIVATED.");
                        sophiaStatusMessage.text("Welcome back!");
                        setTimeout(activateSophiaUI, 1500); // Fade out overlay after a short delay
                    }
                } else if (!faceDetected) {
                    // No face detected yet or face lost
                    sophiaActivationStatus.text("Looking for your face...");
                    sophiaStatusMessage.text("Please position yourself in front of the camera.");
                } else if (faceDetected && resizedDetections.length === 0) {
                    // If face was detected, but now it's gone
                    faceDetected = false;
                    sophiaActivationStatus.text("Face Lost. Looking for your face...");
                    sophiaStatusMessage.text("Please position yourself in front of the camera.");
                }
            }
        }, 100); // Run detection every 100ms
    }

    // Function to fade out the loading overlay and activate the main UI
    function activateSophiaUI() {
        // Stop webcam stream to release camera resources
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
        loadingOverlay.css('opacity', '0'); // Start fading out the overlay
        setTimeout(function() {
            loadingOverlay.remove(); // Remove overlay from DOM after transition completes
        }, 1500); // Matches CSS transition duration

        // After Sophia UI is active, make her speak the greeting
        const greetingMessage = `${getGreeting()}, How can I help you?`;
        if (typeof eel !== 'undefined') {
            eel.speakSophiaGreeting(greetingMessage)(); // Call new eel function to speak
        } else {
            console.warn("eel is not defined. Sophia cannot speak the greeting.");
        }
    }

    // Initial call to start the face recognition process
    loadFaceApiModels();

    // --- Helper function to get time-based greeting for IST ---
    function getGreeting() {
        const now = new Date();
        // Convert to IST (UTC+5:30)
        const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
        const istOffset = 5.5 * 3600000; // 5 hours 30 minutes in milliseconds
        const istTime = new Date(utc + istOffset);
        const hour = istTime.getHours();

        let timeOfDay;
        if (hour >= 5 && hour < 12) {
            timeOfDay = "Good Morning";
        } else if (hour >= 12 && hour < 17) {
            timeOfDay = "Good Afternoon";
        } else {
            timeOfDay = "Good Evening";
        }

        // Use the userName variable for personalization (which is set to "Sir")
        return `${timeOfDay} ${userName}`;
    }

    // --- Global Variable for Chat History ---
    // Initialize chat history with a system instruction and Sophia's dynamic greeting.
    // The actual speaking of this greeting is now handled in activateSophiaUI.
    let chatHistory = [
        { role: "user", parts: [{ text: "You are Sophia, an advanced AI assistant powered by the Gemini model. Your goal is to be highly informative, creative, and capable of generating detailed and coherent responses across a wide range of topics. Engage in natural conversation, provide insightful explanations, and assist the user thoroughly." }] },
        { role: "model", parts: [{ text: `${getGreeting()}, How can I help you?` }] } // Sophia's initial greeting dynamically generated and added to chat history
    ];


    // --- Three.js Background Setup (Remains unchanged from previous correct version) ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById('three-bg'),
        alpha: true // Allow transparency for CSS background to show through if desired
    });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio); // For sharper rendering on high-DPI screens

    // Add a subtle ambient light
    const ambientLight = new THREE.AmbientLight(0x00aaff, 0.1); // Soft blue ambient light
    scene.add(ambientLight);

    // Add a point light for highlights and glow
    const pointLight = new THREE.PointLight(0x00eaff, 1, 100); // Electric blue point light
    pointLight.position.set(0, 0, 10);
    scene.add(pointLight);

    // Create a glowing particle system (example: many small spheres)
    const particleGeometry = new THREE.BufferGeometry();
    const particlesCount = 2000; // Number of particles

    const posArray = new Float32Array(particlesCount * 3); // x, y, z for each particle

    for (let i = 0; i < particlesCount * 3; i++) {
        // Random positions within a cube
        posArray[i] = (Math.random() - 0.5) * 200; // -100 to 100
    }

    particleGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    const particleMaterial = new THREE.PointsMaterial({
        size: 0.5, // Size of each particle
        color: 0x00ccff, // Blue color
        blending: THREE.AdditiveBlending, // For glow effect
        transparent: true,
        opacity: 0.8
    });

    const particles = new THREE.Points(particleGeometry, particleMaterial);
    scene.add(particles);

    camera.position.z = 50; // Move camera back to see particles

    // Animation loop for Three.js
    function animateThreeJs() {
        requestAnimationFrame(animateThreeJs);

        // Rotate particles slowly
        particles.rotation.x += 0.0005;
        particles.rotation.y += 0.0008;

        renderer.render(scene, camera);
    }

    animateThreeJs(); // Start the 3D animation

    // Handle window resize for Three.js
    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });

    // --- End Three.js Background Setup ---

    // --- Textillate for main tagline ---
    $('.tagline').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp", // More subtle robotic entry
        },
        out: {
            effect: "fadeOutDown", // Subtle robotic exit
            delay: 5 // Delay before fading out
        },
    });

    // --- SiriWave Initialization ---
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: Math.min(window.innerWidth * 0.9, 800), // Responsive width
        height: 200,
        style: "ios9", // Keep the iOS9 style for a clean look
        amplitude: 1.2, // Slightly more pronounced wave
        speed: 0.25, // A bit slower, more controlled
        autostart: true,
        pixelDepth: 0.02, // Adds some depth
        lerpSpeed: 0.1 // Smooth transitions
    });

    // Update SiriWave width on window resize
    $(window).resize(function() {
        siriWave.setWidth(Math.min(window.innerWidth * 0.9, 800));
    });

    // --- Textillate for SiriWave message ---
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },
    });

    // --- Chatbox Functionality ---
    const chatboxInput = $('#chatbox');
    const chatBtn = $('#ChatBtn');
    const chatHistoryDisplay = $('#chat-history-display'); // Reference to the chat history div

    // Function to add or update a message in the chat history display
    window.addMessageToChatHistory = function(message, sender, messageId = null) {
        let messageDiv;
        if (messageId && $(`#${messageId}`).length) {
            messageDiv = $(`#${messageId}`);
            messageDiv.text(message)
                     .removeClass('sophia-thinking-message')
                     .addClass('sophia-message');
            messageDiv.find('.typing-dots').remove();
        } else {
            messageDiv = $('<div>').addClass('chat-message');
            if (sender === 'user') {
                messageDiv.addClass('user-message').text(message);
            } else if (sender === 'sophia') {
                messageDiv.addClass('sophia-message').text(message);
            } else if (sender === 'sophia-thinking') {
                messageDiv.addClass('sophia-thinking-message').text(message).attr('id', messageId);
                messageDiv.append($('<span>').addClass('typing-dots'));
            }
            chatHistoryDisplay.append(messageDiv);
        }
        chatHistoryDisplay.scrollTop(chatHistoryDisplay[0].scrollHeight);
    };

    // Function to send message and interact with Gemini API
    async function sendMessage() {
        const message = chatboxInput.val().trim();

        if (message) {
            console.log("Sending message:", message);
            addMessageToChatHistory(message, 'user');

            const thinkingMessageId = 'sophia-thinking-' + Date.now();
            addMessageToChatHistory('SOPHIA is thinking', 'sophia-thinking', thinkingMessageId);

            chatboxInput.val('');

            // Add user message to the ongoing chat history
            chatHistory.push({ role: "user", parts: [{ text: message }] });

            try {
                const payload = { contents: chatHistory };
                const apiKey = ""; // Canvas will automatically provide the API key
                const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;

                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const result = await response.json();

                if (result.candidates && result.candidates.length > 0 &&
                    result.candidates[0].content && result.candidates[0].content.parts &&
                    result.candidates[0].content.parts.length > 0) {
                    const sophiaResponse = result.candidates[0].content.parts[0].text;
                    addMessageToChatHistory(sophiaResponse, 'sophia', thinkingMessageId);
                    // Add Sophia's response to the ongoing chat history for context in next turns
                    chatHistory.push({ role: "model", parts: [{ text: sophiaResponse }] });
                } else {
                    addMessageToChatHistory("I apologize, I couldn't generate a response from the AI at this moment. Gemini returned an unexpected structure.", 'sophia', thinkingMessageId);
                    console.error("Gemini API returned an unexpected structure or no content:", result);
                    chatHistory.pop(); // Remove user message if API fails
                }
            } catch (error) {
                addMessageToChatHistory("I'm having trouble connecting to the AI right now. Please try again later. (Network Error)", 'sophia', thinkingMessageId);
                console.error("Error calling Gemini API:", error);
                chatHistory.pop(); // Remove user message if API fails
            }

            // Call eel function to send message to Python backend (if still needed)
            if (typeof eel !== 'undefined') {
                eel.sendUserMessage(message, thinkingMessageId)();
            } else {
                console.warn("eel is not defined. Python backend integration might be affected.");
            }
        }
    }

    // Event listener for Chat button click
    chatBtn.on('click', function() {
        sendMessage();
        var offcanvas = new bootstrap.Offcanvas(document.getElementById('offcanvasScrolling'));
        offcanvas.show();
    });

    // Event listener for Enter key press in chatbox
    chatboxInput.on('keypress', function(e) {
        if (e.which === 13) {
            sendMessage();
        }
    });

    // --- Existing Mic Button Click Handler ---
    $("#MicBtn").click(function() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        if (typeof eel !== 'undefined') {
            eel.playClickSound();
            eel.allCommands()();
        } else {
            console.warn("eel is not defined. Mic command not sent.");
        }
    });

    // Additional event listeners for input interaction (focus/blur glow)
    chatboxInput.on("focus", function() {
        $(this).closest("#textInput").addClass("input-focused");
    }).on("blur", function() {
        $(this).closest("#textInput").removeClass("input-focused");
    });

    // Example for Settings Button
    $('#SettingsBtn').on('click', function() {
        console.log("Settings button clicked!");
    });
});
