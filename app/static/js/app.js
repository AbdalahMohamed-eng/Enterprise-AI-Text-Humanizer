document.addEventListener('alpine:init', () => {
  Alpine.data('humanizerApp', () => ({
    // State
    inputText: '',
    outputText: '',
    isStreaming: false,
    showDiff: false,
    diffHtml: '',
    mode: 'anti_ai',
    provider: 'groq',
    model: 'groq/llama-3.3-70b-versatile',
    strength: 'medium',
    showSettings: false,
    copied: false,
    
    // AI Detection Scores
    inputAiScore: null,
    outputAiScore: null,
    isDetecting: false,
    
    // Stats
    inputStats: null,
    outputStats: null,
    
    // API Keys (from localStorage)
    apiKeys: {
      openai: localStorage.getItem('humanizer_openai_key') || '',
      gemini: localStorage.getItem('humanizer_gemini_key') || '',
      groq: localStorage.getItem('humanizer_groq_key') || '',
      sapling: localStorage.getItem('humanizer_sapling_key') || ''
    },
    
    // Available models per provider
    availableModels: {
      groq: [
        {id: 'groq/llama-3.3-70b-versatile', name: 'Llama 3.3 70B (Recommended)'},
        {id: 'groq/llama-3.1-8b-instant', name: 'Llama 3.1 8B (Fast)'}
      ],
      openai: [
        {id: 'gpt-4o', name: 'GPT-4o (High Quality)'},
        {id: 'gpt-4o-mini', name: 'GPT-4o Mini (Fast)'}
      ],
      gemini: [
        {id: 'gemini/gemini-2.0-flash', name: 'Gemini 2.0 Flash (Fast & Smart)'},
        {id: 'gemini/gemini-1.5-flash', name: 'Gemini 1.5 Flash'}
      ]
    },
    
    // Computed Properties
    get inputWordCount() { 
      return this.inputText.trim() ? this.inputText.trim().split(/\s+/).length : 0; 
    },
    get inputCharCount() { 
      return this.inputText.length; 
    },
    get outputWordCount() { 
      return this.outputText.trim() ? this.outputText.trim().split(/\s+/).length : 0; 
    },
    get currentModels() { 
      return this.availableModels[this.provider] || []; 
    },
    get readingTimeMinutes() {
      const words = this.outputWordCount || this.inputWordCount;
      if (!words) return 0;
      return Math.max(1, Math.round(words / 200));
    },
    
    // Lifecycle
    init() {
      this.updateModel();
      this.$watch('provider', () => this.updateModel());
      document.documentElement.setAttribute('data-theme', 'light');
    },
    
    updateModel() {
      const models = this.currentModels;
      if (models.length > 0) {
        if (!models.find(m => m.id === this.model)) {
          this.model = models[0].id;
        }
      }
    },
    
    loadSample() {
      this.inputText = "In today's fast-paced digital landscape, it is important to remember that artificial intelligence plays a pivotal role in shaping our future. Delving deeper into this phenomenon reveals a multifaceted tapestry of technological innovation. Furthermore, it serves as a testament to human ingenuity, offering a myriad of comprehensive solutions to navigate modern challenges seamlessly.";
      this.outputText = '';
      this.inputAiScore = null;
      this.outputAiScore = null;
      this.showDiff = false;
    },
    
    clearInput() {
      this.inputText = '';
      this.outputText = '';
      this.inputAiScore = null;
      this.outputAiScore = null;
      this.showDiff = false;
      this.diffHtml = '';
    },
    
    saveApiKeys() {
      localStorage.setItem('humanizer_openai_key', this.apiKeys.openai);
      localStorage.setItem('humanizer_gemini_key', this.apiKeys.gemini);
      localStorage.setItem('humanizer_groq_key', this.apiKeys.groq);
      localStorage.setItem('humanizer_sapling_key', this.apiKeys.sapling);
      this.showSettings = false;
    },
    
    clearApiKeys() {
      this.apiKeys = {openai: '', gemini: '', groq: '', sapling: ''};
      localStorage.removeItem('humanizer_openai_key');
      localStorage.removeItem('humanizer_gemini_key');
      localStorage.removeItem('humanizer_groq_key');
      localStorage.removeItem('humanizer_sapling_key');
    },
    
    async startHumanization() {
      if (!this.inputText.trim() || this.isStreaming) return;
      this.outputText = '';
      this.showDiff = false;
      this.diffHtml = '';
      this.outputAiScore = null;
      this.isStreaming = true;
      
      const headers = {
        'Content-Type': 'application/json',
        'X-OpenAI-Key': this.apiKeys.openai,
        'X-Gemini-Key': this.apiKeys.gemini,
        'X-Groq-Key': this.apiKeys.groq
      };
      
      try {
        const response = await fetch('/api/v1/humanize', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            text: this.inputText,
            provider: this.provider,
            model: this.model,
            mode: this.mode,
            strength: this.strength,
            use_rules: true
          })
        });
        
        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          alert(err.detail || 'Unable to process request. Please ensure your API key is configured.');
          this.isStreaming = false;
          return;
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop();
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') break;
              this.outputText += data;
            }
          }
        }
      } catch (err) {
        console.error('Streaming error:', err);
        alert('Connection error occurred: ' + err.message);
      } finally {
        this.isStreaming = false;
      }
    },
    
    async checkAiScore() {
      if (!this.inputText.trim()) return;
      this.isDetecting = true;
      
      const headers = {
        'Content-Type': 'application/json',
        'X-Sapling-Key': this.apiKeys.sapling
      };

      try {
        const inputResp = await fetch('/api/v1/detect', {
          method: 'POST',
          headers,
          body: JSON.stringify({text: this.inputText, provider: 'auto'})
        });
        if (inputResp.ok) {
          const data = await inputResp.json();
          this.inputAiScore = data.ai_score_percent;
        }
        
        if (this.outputText.trim() && this.outputText.trim().length >= 50) {
          const outputResp = await fetch('/api/v1/detect', {
            method: 'POST',
            headers,
            body: JSON.stringify({text: this.outputText, provider: 'auto'})
          });
          if (outputResp.ok) {
            const data = await outputResp.json();
            this.outputAiScore = data.ai_score_percent;
          }
        }
      } catch (err) {
        console.error('Detection evaluation error:', err);
      } finally {
        this.isDetecting = false;
      }
    },
    
    toggleDiff() {
      this.showDiff = !this.showDiff;
      if (this.showDiff) this.computeDiff();
    },
    
    computeDiff() {
      if (!window.Diff || !this.inputText || !this.outputText) return;
      const diff = Diff.diffWords(this.inputText, this.outputText);
      this.diffHtml = diff.map(part => {
        if (part.added) return `<span class="diff-added">${this.escapeHtml(part.value)}</span>`;
        if (part.removed) return `<span class="diff-removed">${this.escapeHtml(part.value)}</span>`;
        return `<span>${this.escapeHtml(part.value)}</span>`;
      }).join('');
    },
    
    escapeHtml(unsafe) {
      return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
    },
    
    copyOutput() {
      if (!this.outputText) return;
      navigator.clipboard.writeText(this.outputText).then(() => {
        this.copied = true;
        setTimeout(() => {
          this.copied = false;
        }, 2000);
      });
    }
  }));
});
