const OpenAI = require('openai');
const { Logger } = require('./logger');

const GEMINI_MODELS = [
  'gemini-3.5-flash',
  'gemini-3.8-flash',
  'gemini-3.5-flash-lite',
  'gemini-3.7-flash',
];
const GEMINI_DEFAULT_MODEL = GEMINI_MODELS[0];

const PROVIDERS = {
  openai: {
    name: 'OpenAI',
    baseURL: 'https://api.openai.com/v1',
    defaultModel: 'gpt-5.6',
    models: ['gpt-5.6', 'gpt-5.6-terra', 'gpt-5.6-luna'],
    envKey: 'OPENAI_API_KEY',
  },
  openrouter: {
    name: 'OpenRouter',
    baseURL: 'https://openrouter.ai/api/v1',
    defaultModel: 'openai/gpt-5.6-sol',
    models: ['openai/gpt-5.6-sol', 'anthropic/claude-fable-5', 'google/gemini-3.7-flash', 'moonshotai/kimi-k3', 'z-ai/glm-5.3'],
    envKey: 'OPENROUTER_API_KEY',
  },
  kimi: {
    name: 'Kimi (Moonshot AI)',
    baseURL: 'https://api.moonshot.ai/v1',
    defaultModel: 'kimi-k3',
    models: ['kimi-k3', 'kimi-k2.7-code', 'kimi-k2.6'],
    envKey: 'MOONSHOT_API_KEY',
  },
  mimo: {
    name: 'MiMo (Xiaomi)',
    baseURL: 'https://api.xiaomimimo.com/v1',
    defaultModel: 'mimo-v2.5-pro',
    models: ['mimo-v2.5-pro', 'mimo-v2.5'],
    envKey: 'MIMO_API_KEY',
  },
  glm: {
    name: 'GLM (Zhipu AI)',
    baseURL: 'https://api.z.ai/api/paas/v4/',
    defaultModel: 'glm-5.3',
    models: ['glm-5.3', 'glm-5.2', 'glm-5.1'],
    envKey: 'GLM_API_KEY',
  },
};

class AITextService {
  constructor(credentials = {}) {
    this.logger = new Logger('AITextService');
    this.client = null;
    this.gemini = null;
    this.model = null;
    this.providerName = null;

    this._init(credentials);
  }

  _init(credentials) {
    const openaiKey = credentials.openai?.apiKey || process.env.OPENAI_API_KEY;
    if (openaiKey) {
      this._initOpenAICompatible(PROVIDERS.openai, openaiKey);
    }

    const geminiKey = credentials.gemini?.apiKey || process.env.GEMINI_API_KEY;
    if (geminiKey) {
      this._initGemini(geminiKey, credentials.gemini?.model);
    }

    if (!this.client && !this.gemini) {
      this.logger.warn('No AI text provider configured — text generation unavailable');
    }
  }

  _initOpenAICompatible(preset, apiKey, model) {
    this.client = new OpenAI({ apiKey, baseURL: preset.baseURL });
    this.model = model || preset.defaultModel;
    this.providerName = preset.name;
    this.logger.info(`${preset.name} initialized (model: ${this.model})`);
  }

  _initGemini(apiKey, model) {
    try {
      const { GoogleGenAI } = require('@google/genai');
      this.gemini = new GoogleGenAI({ apiKey });
      this.geminiModel = model || GEMINI_DEFAULT_MODEL;
      if (!this.providerName) this.providerName = 'Google Gemini';
      this.logger.info(`Gemini initialized (model: ${this.geminiModel})`);
    } catch (error) {
      this.logger.error('Failed to initialize Gemini:', error.message);
    }
  }

  async generateText(prompt, options = {}) {
    const maxTokens = options.maxTokens || 2048;
    const temperature = options.temperature ?? 0.7;

    if (this.client) {
      const params = {
        model: options.model || this.model,
        messages: [{ role: 'user', content: prompt }],
        temperature,
      };

      try {
        const response = await this.client.chat.completions.create({
          ...params,
          max_completion_tokens: maxTokens,
        });
        return this._extractContent(response);
      } catch (error) {
        if (
          error &&
          error.status === 400 &&
          /max(_completion)?_tokens/i.test(error.message || '')
        ) {
          try {
            const response = await this.client.chat.completions.create({
              ...params,
              max_tokens: maxTokens,
            });
            return this._extractContent(response);
          } catch (retryErr) {
            error = retryErr;
          }
        }

        this.logger.warn(`Primary provider (${this.providerName}) failed: ${error.message}. Falling back to Gemini...`);
        if (!this.gemini) throw error;
      }
    }

    if (this.gemini) {
      const model = options.model || this.geminiModel || GEMINI_DEFAULT_MODEL;
      const config = { maxOutputTokens: maxTokens };
      if (!/^gemini-3\.(?:[5-9]|\d{2,})-/.test(model)) config.temperature = temperature;
      
      const candidateModels = [model, ...GEMINI_MODELS.filter(m => m !== model)];
      let lastError = null;

      for (const targetModel of candidateModels) {
        try {
          const response = await this.gemini.models.generateContent({
            model: targetModel,
            contents: prompt,
            config,
          });
          const text = response && response.text;
          if (typeof text === 'string' && text.trim()) {
            return text;
          }
        } catch (err) {
          lastError = err;
          this.logger.warn(`Gemini model ${targetModel} encountered error (${err.message?.slice(0, 150)}), trying fallback model...`);
        }
      }

      if (lastError) throw lastError;
      throw new Error(
        `Gemini returned an empty response. Check the API key and model quota.`
      );
    }

    throw new Error('No AI text provider configured');
  }

  _extractContent(response) {
    const content =
      response &&
      response.choices &&
      response.choices[0] &&
      response.choices[0].message
        ? response.choices[0].message.content
        : null;

    if (typeof content !== 'string' || !content.trim()) {
      // A null/empty body used to surface as cryptic "Unexpected end of JSON input"
      // in the agents' JSON parsers. Report the real cause instead.
      throw new Error(
        `${this.providerName} returned an empty response. Check the API key and model quota.`
      );
    }
    return content;
  }

  isAvailable() {
    return !!(this.client || this.gemini);
  }
}

module.exports = { AITextService, PROVIDERS, GEMINI_MODELS, GEMINI_DEFAULT_MODEL };
