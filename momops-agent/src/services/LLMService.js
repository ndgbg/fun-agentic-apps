// Lightweight Llama Integration with Performance Optimizations
import * as webllm from "@mlc-ai/web-llm";

export class LLMService {
  constructor() {
    this.engine = null;
    this.isInitialized = false;
    this.isInitializing = false;
    this.initializationPromise = null;
    this.loadingProgress = 0;
    this.useDemo = true; // Start with demo, upgrade to real LLM
    this.modelSize = 'small'; // Track model size for UI
  }

  // Lightweight initialization - only when needed
  async initialize(forceReal = false) {
    if (this.isInitialized && !forceReal) return true;
    if (this.isInitializing) return this.initializationPromise;

    // If not forced and demo is working, stay with demo
    if (!forceReal && this.useDemo) {
      return this._initializeDemo();
    }

    this.isInitializing = true;
    console.log('🧠 Initializing lightweight Llama...');

    this.initializationPromise = this._initializeLlama();
    
    try {
      await this.initializationPromise;
      this.isInitialized = true;
      this.isInitializing = false;
      this.useDemo = false;
      console.log('🧠 Llama ready!');
      return true;
    } catch (error) {
      this.isInitializing = false;
      console.warn('🧠 Llama failed, using enhanced demo:', error);
      this.useDemo = true;
      return this._initializeDemo();
    }
  }

  async _initializeLlama() {
    // Use smallest available model for performance
    const selectedModel = "Llama-3.2-1B-Instruct-q4f32_1-MLC"; // ~600MB instead of 2GB
    this.modelSize = 'small';
    
    try {
      this.engine = await webllm.CreateMLCEngine(selectedModel, {
        initProgressCallback: (report) => {
          this.loadingProgress = Math.round((report.progress || 0) * 100);
          console.log(`🧠 Loading Llama: ${this.loadingProgress}% - ${report.text}`);
          
          // Emit progress event for UI updates
          window.dispatchEvent(new CustomEvent('llmProgress', { 
            detail: { progress: this.loadingProgress, text: report.text }
          }));
        },
        // Performance optimizations
        logLevel: "ERROR", // Reduce logging overhead
        useWebWorker: true, // Use web worker to avoid blocking main thread
      });
      
      console.log('🧠 Llama 1B model loaded successfully');
      return true;
    } catch (error) {
      console.error('🧠 Llama initialization failed:', error);
      throw error;
    }
  }

  async _initializeDemo() {
    console.log('🧠 Using enhanced demo AI...');
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate brief loading
    this.isInitialized = true;
    this.useDemo = true;
    return true;
  }

  // Smart chat response - uses Llama if available, demo if not
  async generateChatResponse(userMessage, babyContext) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    if (!this.useDemo && this.engine) {
      return this._generateLlamaResponse(userMessage, babyContext);
    } else {
      return this._generateDemoResponse(userMessage, babyContext);
    }
  }

  async _generateLlamaResponse(userMessage, babyContext) {
    const systemPrompt = this._buildSystemPrompt(babyContext);
    
    try {
      const response = await this.engine.chat.completions.create({
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage }
        ],
        temperature: 0.7,
        max_tokens: 300, // Limit tokens for faster response
        stream: false, // Disable streaming for simplicity
      });

      return response.choices[0].message.content;
    } catch (error) {
      console.error('🧠 Llama response failed, falling back to demo:', error);
      this.useDemo = true; // Fallback to demo on error
      return this._generateDemoResponse(userMessage, babyContext);
    }
  }

  _buildSystemPrompt(babyContext) {
    const { babyName, babyAge, recentActivities } = babyContext;
    
    return `You are a helpful baby care assistant. Keep responses under 150 words.

BABY INFO:
- Name: ${babyName || 'Baby'}
- Age: ${babyAge?.months || 0} months
- Recent activities: ${this._summarizeActivities(recentActivities)}

Be warm, supportive, and reference the baby's actual data when relevant. If asked about health concerns, recommend consulting a pediatrician.`;
  }

  // Enhanced demo responses (fallback)
  async _generateDemoResponse(userMessage, babyContext) {
    // Simulate thinking time
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const { babyName, recentActivities } = babyContext;
    const message = userMessage.toLowerCase();
    
    // Enhanced contextual responses
    if (message.includes('sleep') || message.includes('nap')) {
      const sleepData = this._analyzeSleepFromActivities(recentActivities);
      return `Looking at ${babyName || 'your baby'}'s sleep patterns: ${sleepData.summary}. ${sleepData.advice} 😴`;
    }
    
    if (message.includes('feed') || message.includes('eat') || message.includes('hungry')) {
      const feedData = this._analyzeFeedingFromActivities(recentActivities);
      return `Based on ${babyName || 'your baby'}'s feeding data: ${feedData.summary}. ${feedData.advice} 🍼`;
    }
    
    if (message.includes('how') && (message.includes('doing') || message.includes('is'))) {
      const activities = recentActivities?.length || 0;
      return `${babyName || 'Your baby'} is doing wonderfully! I can see ${activities} recent activities logged. The patterns show healthy development. What specific aspect would you like me to analyze? 📊`;
    }
    
    return `I'm here to help with ${babyName || 'your baby'}'s care! I can analyze patterns in feeding, sleep, and development. What would you like to know? (Note: I'm using enhanced pattern matching - real AI available on request!) 🤖`;
  }

  // Agent analysis with Llama integration
  async generateAgentAnalysis(observation, previousDecisions = []) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    if (!this.useDemo && this.engine) {
      return this._generateLlamaAgentAnalysis(observation);
    } else {
      return this._generateDemoAgentAnalysis(observation);
    }
  }

  async _generateLlamaAgentAnalysis(observation) {
    const prompt = `Analyze this baby care situation and provide recommendations:

CURRENT STATE:
- Time since last feed: ${observation.babyState?.timeSinceLastFeed || 0} minutes
- Time since last nap: ${observation.babyState?.timeSinceLastNap || 0} minutes
- Baby name: ${observation.babyName || 'Baby'}

Provide a JSON response with immediate actions needed:
{
  "immediateActions": [
    {
      "type": "proactive_notification",
      "priority": "high|medium|low",
      "title": "Brief title",
      "message": "Detailed message",
      "reasoning": "Why this is needed",
      "confidence": 0.8
    }
  ],
  "insights": ["Key observations"]
}`;

    try {
      const response = await this.engine.chat.completions.create({
        messages: [{ role: "user", content: prompt }],
        temperature: 0.3,
        max_tokens: 400,
      });

      return this._parseAgentResponse(response.choices[0].message.content);
    } catch (error) {
      console.error('🧠 Llama agent analysis failed:', error);
      return this._generateDemoAgentAnalysis(observation);
    }
  }

  _generateDemoAgentAnalysis(observation) {
    const decisions = {
      immediateActions: [],
      plannedActions: [],
      insights: ['Enhanced AI analysis (demo mode)'],
      riskFactors: []
    };

    // Smart pattern-based decisions with proper time formatting
    const timeSinceFeed = observation.babyState?.timeSinceLastFeed || 0;
    const timeSinceNap = observation.babyState?.timeSinceLastNap || 0;
    
    if (isFinite(timeSinceFeed) && timeSinceFeed > 200) {
      const timeFormatted = this._formatTimeAgo(timeSinceFeed);
      decisions.immediateActions.push({
        type: 'proactive_notification',
        priority: 'high',
        title: '🧠 Smart Feeding Alert',
        message: `${observation.babyName || 'Baby'} typically feeds every 3 hours. Current gap: ${timeFormatted}.`,
        reasoning: 'Pattern analysis suggests feeding window approaching',
        confidence: 0.85,
        userActions: [
          { label: 'Prepare Feed', action: 'start_feed' },
          { label: 'Not Ready', action: 'dismiss_feed' }
        ]
      });
    }

    if (isFinite(timeSinceNap) && timeSinceNap > 150) {
      const timeFormatted = this._formatTimeAgo(timeSinceNap);
      decisions.immediateActions.push({
        type: 'proactive_notification',
        priority: 'medium',
        title: '🧠 Sleep Pattern Alert',
        message: `Baby has been awake for ${timeFormatted}. Optimal wake windows are 1.5-2 hours.`,
        reasoning: 'Preventing overtiredness based on developmental needs',
        confidence: 0.8,
        userActions: [
          { label: 'Start Sleep Routine', action: 'start_nap' },
          { label: 'Still Alert', action: 'snooze_15' }
        ]
      });
    }

    return decisions;
  }

  // Helper function to format time properly
  _formatTimeAgo(minutes) {
    if (!minutes || !isFinite(minutes) || minutes < 0) {
      return 'just now';
    }
    
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    
    if (hours === 0) {
      return `${mins}m`;
    } else if (mins === 0) {
      return `${hours}h`;
    } else {
      return `${hours}h ${mins}m`;
    }
  }

  // Upgrade to real Llama on demand
  async upgradeToLlama() {
    if (!this.useDemo) return true; // Already using Llama
    
    console.log('🧠 Upgrading to real Llama...');
    return this.initialize(true); // Force real initialization
  }

  // Helper methods
  _summarizeActivities(activities) {
    if (!activities || activities.length === 0) return 'No recent activities';
    return `${activities.length} activities in last 24h`;
  }

  _analyzeSleepFromActivities(activities) {
    const naps = activities?.filter(a => a.type === 'nap') || [];
    if (naps.length === 0) {
      return {
        summary: 'no recent naps logged',
        advice: 'Try tracking naps for better insights!'
      };
    }
    
    const totalSleep = naps.reduce((sum, nap) => sum + (nap.duration || 0), 0);
    return {
      summary: `${naps.length} naps, ${Math.floor(totalSleep / 60)}h total`,
      advice: 'Sleep patterns look healthy!'
    };
  }

  _analyzeFeedingFromActivities(activities) {
    const feeds = activities?.filter(a => a.type === 'feed') || [];
    if (feeds.length === 0) {
      return {
        summary: 'no recent feeds logged',
        advice: 'Start tracking for personalized insights!'
      };
    }
    
    return {
      summary: `${feeds.length} feeds tracked`,
      advice: 'Feeding frequency looks good!'
    };
  }

  _parseAgentResponse(response) {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
    } catch (error) {
      console.error('Failed to parse Llama response:', error);
    }
    
    return {
      immediateActions: [],
      insights: [response.substring(0, 100)],
      riskFactors: []
    };
  }

  // Status methods
  isReady() {
    return this.isInitialized;
  }

  getStatus() {
    if (this.isInitialized && !this.useDemo) return 'llama_ready';
    if (this.isInitialized && this.useDemo) return 'demo_ready';
    if (this.isInitializing) return 'loading_llama';
    return 'not_initialized';
  }

  getModelInfo() {
    return {
      isDemo: this.useDemo,
      modelSize: this.modelSize,
      loadingProgress: this.loadingProgress
    };
  }
}

// Singleton instance
export const llmService = new LLMService();