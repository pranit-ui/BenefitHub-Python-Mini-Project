document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotInput = document.getElementById('chatbotInput');
    const chatbotSend = document.getElementById('chatbotSend');
    const chatbotMessages = document.getElementById('chatbotMessages');

    // User context to track conversation state
    let userContext = {
        lastCategory: null,
        preferences: [],
        eligibilityInfo: {},
        lastQuery: null
    };

    // Quick reply suggestions
    const quickReplies = {
        'initial': ['Find schemes for me', 'Check my eligibility', 'How to apply', 'Required documents'],
        'schemes': ['Education & Scholarship', 'Healthcare & Wellness', 'Housing & Property', 'Agriculture & Farming', 'Employment & Skill'],
        'help': ['Track application', 'Contact helpdesk', 'FAQs'],
        'eligibility': ['Income below 3 lakh', 'Student', 'Senior citizen', 'Farmer', 'Woman entrepreneur'],
        'documents': ['Aadhaar Card', 'Income Certificate', 'Caste Certificate', 'Domicile Certificate', 'Bank Account']
    };

    // Add suggestions for autocomplete based on categories
    const suggestions = {
        general: [
            'Find schemes for me',
            'Check my eligibility',
            'How to apply for schemes',
            'Required documents',
            'Track my application',
            'FAQs about schemes'
        ],
        education: [
            'PM Vidya Scheme details',
            'Scholarship for SC/ST students',
            'Merit scholarship eligibility',
            'Education loan subsidy',
            'Free coaching schemes'
        ],
        healthcare: [
            'Ayushman Bharat registration',
            'PM Jan Arogya Yojana benefits',
            'Free health checkup schemes',
            'Healthcare for senior citizens',
            'Maternity benefit schemes'
        ],
        housing: [
            'PM Awas Yojana application',
            'Housing loan subsidy rate',
            'Rural housing scheme eligibility',
            'Home loan interest subsidy',
            'EWS housing scheme documents'
        ],
        agriculture: [
            'PM Kisan Samman Nidhi payment',
            'Crop insurance application',
            'Subsidies for organic farming',
            'Agricultural loan waiver',
            'Farm equipment subsidy'
        ],
        employment: [
            'PM Rozgar Yojana registration',
            'Skill development training',
            'Self-employment loan scheme',
            'Startup India benefits',
            'Women entrepreneur schemes'
        ]
    };

    // Create suggestions container
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'suggestions-container';
    chatbotInput.parentNode.insertBefore(suggestionsContainer, chatbotInput.nextSibling);
    suggestionsContainer.style.display = 'none';

    // Initialize chat with welcome message and quick replies
    function initializeChat() {
        if (chatbotMessages.children.length === 0) {
            addMessage("नमस्ते! Welcome to BenefitHub Assistant. How can I help you find government schemes today?", true);
            addQuickReplies('initial');
        }
    }

    // Function to get active suggestions based on context
    function getActiveSuggestions() {
        if (userContext.lastCategory && suggestions[userContext.lastCategory]) {
            return [...suggestions[userContext.lastCategory], ...suggestions.general];
        }
        return suggestions.general;
    }

    async function sendMessage(message = null) {
        const messageText = message || chatbotInput.value.trim();
        if (!messageText) return;

        try {
            // Show user message first
            addMessage(messageText, false);
            chatbotInput.value = '';
            
            // Update user context based on message
            updateUserContext(messageText);

            // Show typing indicator
            showTypingIndicator();

            // Get CSRF token if available
            let headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            };
            
            // Try to get CSRF token from meta tag if it exists
            const csrfToken = document.querySelector('meta[name="csrf-token"]');
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken.getAttribute('content');
            }

            const response = await fetch('/chatbot', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ 
                    message: messageText,
                    context: userContext,
                    timestamp: new Date().toISOString() 
                }),
                credentials: 'same-origin'  // Include cookies with request
            });

            // Remove typing indicator
            removeTypingIndicator();

            if (!response.ok) {
                const errorBody = await response.text();
                console.error(`HTTP error! status: ${response.status}`, errorBody);
                
                // Check if it's a CSRF error
                if (errorBody.includes('CSRF token') || response.status === 400) {
                    addMessage("I'm having trouble connecting to the server. Please refresh the page and try again.", true);
                } else {
                    throw new Error(`Server error: ${response.status}`);
                }
                return;
            }

            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                addMessage("I received an unexpected response. Please try again later.", true);
                return;
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // If we have scheme data, display it in a card format
            if (data.schemes && data.schemes.length > 0) {
                addSchemeCards(data.schemes);
            } else {
                addMessage(data.response, true);
            }

            // Update context if server provides it
            if (data.context) {
                userContext = {...userContext, ...data.context};
            }

            if (data.redirect_url) {
                addMessage(`I'll take you to the relevant page in a moment...`, true);
                setTimeout(() => {
                    window.location.href = data.redirect_url;
                }, 1500);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error. Please try again.', true);
        }
    }

    // Update user context based on message content
    function updateUserContext(message) {
        const lowerMessage = message.toLowerCase();
        userContext.lastQuery = lowerMessage;
        
        // Detect category interest
        const categories = ['education', 'healthcare', 'housing', 'agriculture', 'employment', 'family welfare'];
        for (const category of categories) {
            if (lowerMessage.includes(category)) {
                userContext.lastCategory = category;
                if (!userContext.preferences.includes(category)) {
                    userContext.preferences.push(category);
                }
                break;
            }
        }
        
        // Detect eligibility information
        if (lowerMessage.includes('income') || lowerMessage.includes('salary')) {
            const incomeMatch = lowerMessage.match(/(\d+)(\s*)(lakh|lac|k|thousand)/i);
            if (incomeMatch) {
                userContext.eligibilityInfo.income = incomeMatch[0];
            }
        }
        
        if (lowerMessage.includes('student') || lowerMessage.includes('study')) {
            userContext.eligibilityInfo.isStudent = true;
        }
        
        if (lowerMessage.includes('senior') || lowerMessage.includes('old') || lowerMessage.includes('elder')) {
            userContext.eligibilityInfo.isSenior = true;
        }
        
        if (lowerMessage.includes('farm') || lowerMessage.includes('agriculture') || lowerMessage.includes('crop')) {
            userContext.eligibilityInfo.isFarmer = true;
        }
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator';
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        typingDiv.id = 'typing-indicator';
        chatbotMessages.appendChild(typingDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function addSchemeCards(schemes) {
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'scheme-cards';
        
        schemes.forEach(scheme => {
            const card = document.createElement('div');
            card.className = 'scheme-card';
            
            const title = document.createElement('h4');
            title.textContent = scheme.title;
            
            const description = document.createElement('p');
            description.textContent = scheme.description.substring(0, 100) + (scheme.description.length > 100 ? '...' : '');
            
            const applyButton = document.createElement('button');
            applyButton.className = 'scheme-apply-btn';
            applyButton.textContent = 'Apply Now';
            applyButton.onclick = () => {
                window.location.href = scheme.apply_link || '#';
            };
            
            const detailsButton = document.createElement('button');
            detailsButton.className = 'scheme-details-btn';
            detailsButton.textContent = 'View Details';
            detailsButton.onclick = () => {
                showSchemeDetails(scheme);
            };
            
            const buttonContainer = document.createElement('div');
            buttonContainer.className = 'scheme-card-buttons';
            buttonContainer.appendChild(detailsButton);
            buttonContainer.appendChild(applyButton);
            
            card.appendChild(title);
            card.appendChild(description);
            card.appendChild(buttonContainer);
            
            cardsContainer.appendChild(card);
        });
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.appendChild(document.createTextNode('Here are some schemes that might interest you:'));
        messageDiv.appendChild(cardsContainer);
        
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function showSchemeDetails(scheme) {
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'scheme-details';
        
        const title = document.createElement('h4');
        title.textContent = scheme.title;
        
        const description = document.createElement('p');
        description.textContent = scheme.description;
        
        const eligibility = document.createElement('div');
        eligibility.innerHTML = `<strong>Eligibility:</strong> ${scheme.eligibility}`;
        
        const benefits = document.createElement('div');
        benefits.innerHTML = `<strong>Benefits:</strong> ${scheme.benefits}`;
        
        const applyButton = document.createElement('button');
        applyButton.className = 'scheme-apply-btn';
        applyButton.textContent = 'Apply Now';
        applyButton.onclick = () => {
            window.location.href = scheme.apply_link || '#';
        };
        
        detailsDiv.appendChild(title);
        detailsDiv.appendChild(description);
        detailsDiv.appendChild(eligibility);
        detailsDiv.appendChild(benefits);
        detailsDiv.appendChild(applyButton);
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.appendChild(detailsDiv);
        
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addMessage(message, isBot) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isBot ? 'bot' : 'user'}`;
        
        let messageText = message;
        
        // Make categories clickable
        const categories = ['education', 'healthcare', 'housing', 'agriculture', 'employment', 'family welfare'];
        categories.forEach(category => {
            const regex = new RegExp(`${category}`, 'gi');
            messageText = messageText.replace(regex, 
                `<span class="clickable-category" onclick="sendMessage('${category} schemes')">${category}</span>`
            );
        });
        
        messageDiv.innerHTML = messageText.replace(/\n/g, '<br>');
        chatbotMessages.appendChild(messageDiv);
        
        // Add quick replies for bot messages
        if (isBot) {
            if (messageText.toLowerCase().includes("how can i help you")) {
                addQuickReplies('initial');
            } else if (messageText.toLowerCase().includes("various categories") || messageText.toLowerCase().includes("which category")) {
                addQuickReplies('schemes');
            } else if (messageText.toLowerCase().includes("eligibility")) {
                addQuickReplies('eligibility');
            } else if (messageText.toLowerCase().includes("document")) {
                addQuickReplies('documents');
            } else if (messageText.toLowerCase().includes("specify") || messageText.toLowerCase().includes("help you better")) {
                addQuickReplies('help');
            }
        }
        
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function addQuickReplies(category) {
        // Remove existing quick replies
        const existingReplies = chatbotMessages.querySelector('.quick-replies');
        if (existingReplies) {
            existingReplies.remove();
        }

        const quickReplyContainer = document.createElement('div');
        quickReplyContainer.className = 'quick-replies';
        
        quickReplies[category].forEach(reply => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.textContent = reply;
            button.onclick = () => sendMessage(reply);
            quickReplyContainer.appendChild(button);
        });
        
        chatbotMessages.appendChild(quickReplyContainer);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    function showSuggestions(input) {
        const inputValue = input.toLowerCase();
        if (inputValue.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        const activeSuggestions = getActiveSuggestions();
        const filteredSuggestions = activeSuggestions.filter(suggestion => 
            suggestion.toLowerCase().includes(inputValue)
        ).slice(0, 5); // Limit to 5 suggestions

        if (filteredSuggestions.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        suggestionsContainer.innerHTML = '';
        filteredSuggestions.forEach(suggestion => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'suggestion-item';
            suggestionItem.textContent = suggestion;
            suggestionItem.addEventListener('click', () => {
                chatbotInput.value = suggestion;
                suggestionsContainer.style.display = 'none';
                chatbotInput.focus();
            });
            suggestionsContainer.appendChild(suggestionItem);
        });

        suggestionsContainer.style.display = 'block';
    }

    // Event Listeners
    chatbotToggle.addEventListener('click', () => {
        chatbotWindow.style.display = chatbotWindow.style.display === 'none' || chatbotWindow.style.display === '' ? 'flex' : 'none';
        if (chatbotWindow.style.display === 'flex') {
            initializeChat();
        }
    });

    chatbotClose.addEventListener('click', () => {
        chatbotWindow.style.display = 'none';
    });

    chatbotSend.addEventListener('click', () => sendMessage());

    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
            suggestionsContainer.style.display = 'none';
        }
    });

    // Add input event for suggestions
    chatbotInput.addEventListener('input', () => {
        showSuggestions(chatbotInput.value.trim());
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', (e) => {
        if (!suggestionsContainer.contains(e.target) && e.target !== chatbotInput) {
            suggestionsContainer.style.display = 'none';
        }
    });

    // Make sendMessage available globally for quick replies
    window.sendMessage = sendMessage;
});