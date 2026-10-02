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
    isDarkTheme: true,
    
    // AI Scores
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
      openai: [{id: 'gpt-4o', name: 'GPT-4o'}, {id: 'gpt-4o-mini', name: 'GPT-4o Mini'}],
      gemini: [{id: 'gemini/gemini-2.0-flash', name: 'Gemini 2.0 Flash'}, {id: 'gemini/gemini-1.5-flash', name: 'Gemini 1.5 Flash'}],
      groq: [{id: 'groq/llama-3.3-70b-versatile', name: 'Llama 3.3 70B'}, {id: 'groq/llama-3.1-8b-instant', name: 'Llama 3.1 8B'}]
    },
    
    // Computed
    get inputWordCount() { return this.inputText.trim() ? this.inputText.trim().split(/\s+/).length : 0; },
    get outputWordCount() { return this.outputText.trim() ? this.outputText.trim().split(/\s+/).length : 0; },
    get currentModels() { return this.availableModels[this.provider] || []; },
    
    // Methods
    init() {
      // Set initial model based on provider
      this.updateModel();
      // Watch provider changes
      this.$watch('provider', () => this.updateModel());
      
      // Initialize theme based on preference or current default (dark)
      this.isDarkTheme = true;
      document.documentElement.setAttribute('data-theme', 'dark');
    },
    
    updateModel() {
      const models = this.currentModels;
      if (models.length > 0) {
        // Only change if the current model is not in the new provider's list
        if (!models.find(m => m.id === this.model)) {
            this.model = models[0].id;
        }
      }
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
    
    toggleTheme() {
      this.isDarkTheme = !this.isDarkTheme;
      document.documentElement.setAttribute('data-theme', this.isDarkTheme ? 'dark' : 'light');
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
          const err = await response.json();
          alert(err.detail || 'Failed to humanize');
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
              // Simple unescaping or parsing if it's json. Assuming raw stream
              this.outputText += data; 
            }
            if (line.startsWith('event: error')) {
               console.error("Stream error event received.");
            }
          }
        }
      } catch (err) {
        console.error('Stream error:', err);
        alert('Connection error: ' + err.message);
      } finally {
        this.isStreaming = false;
        // Optionally run AI detection automatically after humanization completes
        // this.checkAiScore(); 
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
        // Check input score
        const inputResp = await fetch('/api/v1/detect', {
          method: 'POST',
          headers,
          body: JSON.stringify({text: this.inputText, provider: 'auto'})
        });
        if (inputResp.ok) {
          const data = await inputResp.json();
          this.inputAiScore = data.ai_score_percent;
        }
        
        // Check output score if available
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
        console.error('Detection error:', err);
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
      // Using word diff for better readability in UI
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
        // Brief visual feedback
        const btn = document.getElementById('copy-btn');
        if (btn) { 
            const originalText = btn.innerHTML;
            btn.textContent = '✓ Copied!'; 
            setTimeout(() => btn.innerHTML = '📋 Copy', 1500); 
        }
      });
    }
  }));
});
