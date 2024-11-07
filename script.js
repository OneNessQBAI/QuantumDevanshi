// Global variables
let optimizationResults = null;
let particleData = null;
let conversationHistory = [];

// Default particle configuration
const defaultParticleConfig = {
    mass: 1.67262192e-27,  // proton mass
    charge: 1.60217663e-19,  // elementary charge
    g_factor: 5.585694713,  // proton g-factor
    velocity: [1e5, 0, 0]
};

// Initialize the UI
document.addEventListener('DOMContentLoaded', () => {
    // Set default particle configuration
    document.getElementById('particle-config').value = JSON.stringify(defaultParticleConfig, null, 2);
    
    // Add event listeners
    document.getElementById('execute-btn').addEventListener('click', executeOptimization);
    document.getElementById('send-btn').addEventListener('click', sendChatMessage);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    document.getElementById('database-file').addEventListener('change', handleFileUpload);

    // Add welcome message with instructions
    const welcomeMessage = `Welcome to the Quantum Magnetic Field Optimizer! 🌟

I'm your quantum physics assistant, powered by GPT-4. I can help you with:

1. Analyzing magnetic field configurations
2. Interpreting particle measurements
3. Explaining quantum phenomena
4. Suggesting optimization strategies
5. Answering technical questions

To get started:
• Enter your OpenAI API key
• Configure your particle parameters or use defaults
• Upload custom data (optional)
• Click 'Execute Optimization'

Ask me anything about quantum magnetic fields and optimization!`;

    addMessage('ai', welcomeMessage);
});

// Show loading animation
function showLoading(message) {
    const loadingHtml = `
        <div class="loading-container">
            <div class="loading"></div>
            <span>${message}</span>
        </div>
    `;
    addMessage('system', loadingHtml, true);
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading('Uploading and processing file...');

    try {
        const text = await file.text();
        if (file.name.endsWith('.json')) {
            particleData = JSON.parse(text);
        } else if (file.name.endsWith('.csv')) {
            particleData = parseCSV(text);
        }
        addMessage('system', `File "${file.name}" uploaded and processed successfully`);
        
        // Analyze uploaded data with GPT-4
        const openaiKey = document.getElementById('openai-key').value;
        if (openaiKey) {
            showLoading('Analyzing uploaded data...');
            const analysis = await analyzeData(particleData, openaiKey);
            addMessage('ai', analysis);
        }
    } catch (error) {
        addMessage('system', `Error processing file: ${error.message}`);
    }
}

// Analyze uploaded data
async function analyzeData(data, apiKey) {
    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "gpt-4",
                messages: [{
                    role: "system",
                    content: "You are a quantum physics expert analyzing particle data. Provide insights about the data structure and potential implications for magnetic field optimization."
                }, {
                    role: "user",
                    content: `Analyze this particle data and suggest optimization strategies: ${JSON.stringify(data)}`
                }]
            })
        });

        const result = await response.json();
        if (result.error) throw new Error(result.error.message);
        return result.choices[0].message.content;
    } catch (error) {
        throw new Error(`Data analysis error: ${error.message}`);
    }
}

// Parse CSV data
function parseCSV(text) {
    const lines = text.split('\n');
    const headers = lines[0].split(',');
    const data = [];

    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        if (values.length === headers.length) {
            const entry = {};
            headers.forEach((header, index) => {
                entry[header.trim()] = values[index].trim();
            });
            data.push(entry);
        }
    }

    return data;
}

// Execute the optimization
async function executeOptimization() {
    const openaiKey = document.getElementById('openai-key').value;
    const endpoint = document.getElementById('custom-endpoint').value;
    const apiKey = document.getElementById('custom-api-key').value;
    let particleConfig;

    try {
        particleConfig = JSON.parse(document.getElementById('particle-config').value);
    } catch (error) {
        addMessage('system', 'Invalid particle configuration JSON');
        return;
    }

    // Show loading state
    document.getElementById('execute-btn').disabled = true;
    showLoading('Initializing quantum optimization...');

    try {
        // Simulate quantum optimization process with progress updates
        const results = await simulateOptimization(particleConfig, particleData);
        optimizationResults = results;
        
        // Display results
        displayResults(results);
        
        // Get GPT-4 analysis
        if (openaiKey) {
            showLoading('Analyzing results with GPT-4...');
            const analysis = await analyzeResults(results, openaiKey);
            addMessage('ai', analysis);
            
            // Add follow-up suggestions
            const suggestions = await getFollowUpSuggestions(results, openaiKey);
            addMessage('ai', suggestions);
        }
    } catch (error) {
        addMessage('system', `Error during optimization: ${error.message}`);
    } finally {
        document.getElementById('execute-btn').disabled = false;
    }
}

// Get follow-up suggestions
async function getFollowUpSuggestions(results, apiKey) {
    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "gpt-4",
                messages: [{
                    role: "system",
                    content: "You are a quantum physics expert. Suggest follow-up experiments or optimizations based on the results."
                }, {
                    role: "user",
                    content: `Based on these results, what follow-up experiments or optimizations would you suggest? ${JSON.stringify(results)}`
                }]
            })
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error.message);
        return data.choices[0].message.content;
    } catch (error) {
        throw new Error(`Error getting suggestions: ${error.message}`);
    }
}

// Send chat message
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    const openaiKey = document.getElementById('openai-key').value;

    if (!message) return;

    // Clear input
    input.value = '';

    // Display user message
    addMessage('user', message);
    
    // Add to conversation history
    conversationHistory.push({
        role: "user",
        content: message
    });

    if (!openaiKey) {
        addMessage('system', 'Please enter your OpenAI API key to use the chat feature.');
        return;
    }

    showLoading('Getting GPT-4 response...');

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${openaiKey}`
            },
            body: JSON.stringify({
                model: "gpt-4",
                messages: [
                    {
                        role: "system",
                        content: `You are a quantum physics expert specializing in magnetic field optimization. 
                                Current optimization results: ${JSON.stringify(optimizationResults)}
                                Maintain context of the conversation and provide detailed, technical responses 
                                while making complex concepts accessible.`
                    },
                    ...conversationHistory
                ],
                temperature: 0.7,
                max_tokens: 500
            })
        });

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error.message);
        }
        
        const aiResponse = data.choices[0].message.content;
        addMessage('ai', aiResponse);
        
        // Add to conversation history
        conversationHistory.push({
            role: "assistant",
            content: aiResponse
        });
        
        // Keep conversation history manageable
        if (conversationHistory.length > 10) {
            conversationHistory = conversationHistory.slice(-10);
        }
    } catch (error) {
        addMessage('system', `Error: ${error.message}`);
    }
}

// Simulate quantum optimization
async function simulateOptimization(config, data) {
    const steps = ['Initializing quantum circuit...',
                  'Preparing particle states...',
                  'Optimizing magnetic field configuration...',
                  'Measuring quantum states...',
                  'Finalizing results...'];
    
    for (const step of steps) {
        showLoading(step);
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Generate simulated results
    const results = {
        timestamp: new Date().toISOString(),
        configuration: config,
        magnetic_field: {
            strength: Math.random() * 100,
            direction: [
                Math.random() - 0.5,
                Math.random() - 0.5,
                Math.random() - 0.5
            ]
        },
        particle_measurements: Array(10).fill(0).map(() => ({
            position: [Math.random() * 10, Math.random() * 10, Math.random() * 10],
            momentum: [Math.random() * 5, Math.random() * 5, Math.random() * 5],
            spin: Math.random() * 2 - 1,
            energy_level: Math.floor(Math.random() * 5)
        })),
        optimization_score: Math.random() * 100,
        quantum_states: {
            superposition: Math.random(),
            entanglement: Math.random(),
            coherence: Math.random()
        }
    };

    // If we have custom data, incorporate it
    if (data) {
        results.custom_data = data;
    }

    return results;
}

// Analyze results using GPT-4
async function analyzeResults(results, apiKey) {
    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "gpt-4",
                messages: [{
                    role: "system",
                    content: "You are a quantum physics expert analyzing magnetic field optimization results. Provide detailed insights about the optimization results, including magnetic field configuration, particle measurements, and quantum states. Use technical language but make it accessible."
                }, {
                    role: "user",
                    content: `Analyze these quantum magnetic field optimization results and provide insights: ${JSON.stringify(results)}`
                }]
            })
        });

        const data = await response.json();
        if (data.error) {
            throw new Error(data.error.message);
        }
        return data.choices[0].message.content;
    } catch (error) {
        throw new Error(`GPT-4 analysis error: ${error.message}`);
    }
}

// Display results in the UI
function displayResults(results) {
    const container = document.getElementById('results-container');
    
    // Create a formatted display of the results
    const formattedResults = `
        <h3>Optimization Results</h3>
        <div class="result-section">
            <h4>Magnetic Field Configuration</h4>
            <p>Strength: ${results.magnetic_field.strength.toFixed(2)} Tesla</p>
            <p>Direction: [${results.magnetic_field.direction.map(d => d.toFixed(3)).join(', ')}]</p>
        </div>
        
        <div class="result-section">
            <h4>Quantum States</h4>
            <p>Superposition: ${(results.quantum_states.superposition * 100).toFixed(2)}%</p>
            <p>Entanglement: ${(results.quantum_states.entanglement * 100).toFixed(2)}%</p>
            <p>Coherence: ${(results.quantum_states.coherence * 100).toFixed(2)}%</p>
        </div>
        
        <div class="result-section">
            <h4>Particle Measurements</h4>
            <ul>
                ${results.particle_measurements.map((m, i) => `
                    <li>Particle ${i + 1}:
                        <ul>
                            <li>Position: [${m.position.map(p => p.toFixed(2)).join(', ')}]</li>
                            <li>Momentum: [${m.momentum.map(p => p.toFixed(2)).join(', ')}]</li>
                            <li>Spin: ${m.spin.toFixed(3)}</li>
                            <li>Energy Level: ${m.energy_level}</li>
                        </ul>
                    </li>
                `).join('')}
            </ul>
        </div>
        
        <div class="result-section">
            <h4>Overall Performance</h4>
            <p>Optimization Score: ${results.optimization_score.toFixed(2)}%</p>
            <p>Timestamp: ${new Date(results.timestamp).toLocaleString()}</p>
        </div>
    `;
    
    container.innerHTML = formattedResults;
}

// Add a message to the chat
function addMessage(type, content, isHtml = false) {
    const container = document.getElementById('chat-container');
    const message = document.createElement('div');
    message.className = `message ${type}`;
    
    if (isHtml) {
        message.innerHTML = content;
    } else {
        message.textContent = content;
    }
    
    container.appendChild(message);
    container.scrollTop = container.scrollHeight;
}
