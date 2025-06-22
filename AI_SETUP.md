# 🧠 Real AI Setup Guide

This guide shows you how to enable **real AI agents** in your Cold Outreach System using GPT-4, sentence transformers, and other AI models.

## 🤖 Current State: Mock AI Agents

By default, the system runs with **mock AI agents** that simulate real AI behavior:
- ✅ Works out of the box
- ✅ No API keys required
- ✅ No external dependencies
- ⚠️ Simulated results only

## 🧠 Upgrade to Real AI Agents

To enable real AI functionality with GPT-4, sentence transformers, and intelligent web scraping:

### Step 1: Install AI Dependencies

```bash
# Install real AI dependencies
pip install -r requirements_ai.txt

# Or install individually:
pip install openai>=1.0.0 sentence-transformers>=2.2.0 torch>=2.0.0
```

### Step 2: Get OpenAI API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-...`)

### Step 3: Configure Environment Variables

Create a `.env` file in your project root:

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-api-key-here
USE_REAL_AI=true

# Optional: Email configuration for real email sending
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Or set environment variables directly:

```bash
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export USE_REAL_AI=true
```

### Step 4: Restart the System

```bash
python simple_dashboard.py
```

You should see:
```
🧠 Initializing REAL AI Agents with GPT-4 + Sentence Transformers
🧠 Real AI Agents: GPT-4 | Sentence Transformers | OpenAI Embeddings
```

## 🔬 Real AI Agents Overview

### 1. 🕷️ **Real Web Scraping Agent**
- **Technology**: Selenium + Playwright + GPT-4
- **Features**: 
  - Intelligent data extraction from Y Combinator, Product Hunt
  - AI-powered content classification
  - Dynamic startup description generation
  - Rate limiting and error handling

### 2. 🧠 **Real Semantic Matching Agent**
- **Technology**: Sentence Transformers + GPT-4
- **Model**: `all-MiniLM-L6-v2` for embeddings
- **Features**:
  - Semantic similarity scoring using embeddings
  - GPT-4 powered match reasoning
  - Hybrid scoring (70% semantic + 30% AI analysis)
  - Advanced profile-startup alignment

### 3. ✍️ **Real Email Generation Agent**
- **Technology**: GPT-4 Turbo
- **Features**:
  - Personalized cold email generation
  - Context-aware subject lines
  - Professional tone optimization
  - JSON-structured output parsing

### 4. 📧 **Real Email Dispatch Agent**
- **Technology**: SMTP + AI optimization
- **Features**:
  - Real email sending via SMTP
  - Deliverability optimization
  - Send-time optimization based on location
  - Success/failure tracking

## 🎛️ Configuration Options

### AI Model Selection

```python
# In ai_agents.py - customize models
SENTENCE_MODEL = 'all-MiniLM-L6-v2'  # Fast, good quality
# SENTENCE_MODEL = 'all-mpnet-base-v2'  # Better quality, slower

GPT_MODEL = 'gpt-4'  # Best quality
# GPT_MODEL = 'gpt-3.5-turbo'  # Faster, cheaper
```

### Scraping Sources

```python
# Enable/disable sources in ai_agents.py
ENABLED_SOURCES = {
    'ycombinator': True,
    'producthunt': True,
    'angellist': False,  # Coming soon
    'crunchbase': False  # Coming soon
}
```

## 💰 Cost Estimation

### OpenAI API Costs (GPT-4)
- **Email Generation**: ~$0.03 per email
- **Match Analysis**: ~$0.01 per startup
- **Content Classification**: ~$0.005 per startup

### Example Campaign (50 startups → 10 emails):
- Scraping + Classification: 50 × $0.005 = $0.25
- Matching Analysis: 50 × $0.01 = $0.50
- Email Generation: 10 × $0.03 = $0.30
- **Total**: ~$1.05 per campaign

## 🔧 Troubleshooting

### Common Issues

1. **ImportError: No module named 'sentence_transformers'**
   ```bash
   pip install sentence-transformers torch
   ```

2. **OpenAI API Error: Invalid API key**
   - Check your API key is correct
   - Ensure you have credits in your OpenAI account

3. **TensorFlow/PyTorch warnings**
   - These are normal and don't affect functionality
   - Warnings are suppressed in the code

4. **SMTP Email sending fails**
   - Check your email credentials
   - Use app passwords for Gmail
   - Ensure 2FA is enabled

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Performance Optimization

### For Large Campaigns (100+ startups):

1. **Use GPU acceleration** (if available):
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Batch processing** for embeddings:
   ```python
   # In ai_agents.py
   BATCH_SIZE = 32  # Process multiple startups at once
   ```

3. **Caching** for repeated operations:
   ```python
   USE_EMBEDDING_CACHE = True
   ```

## 📊 Monitoring & Analytics

Real AI agents provide detailed metrics:
- Semantic similarity scores
- GPT-4 confidence ratings
- Email generation quality metrics
- Delivery success rates
- Campaign performance analytics

## 🔄 Switching Between Mock and Real AI

You can switch at any time:

```bash
# Use real AI
export USE_REAL_AI=true

# Use mock AI (default)
export USE_REAL_AI=false
```

The system will automatically detect and switch modes without code changes.

## 🎯 Next Steps

Once real AI is enabled:
1. Test with a small campaign (5-10 startups)
2. Review generated emails for quality
3. Monitor API usage and costs
4. Scale up to larger campaigns
5. Customize prompts and models for your use case

---

**Ready to deploy real AI agents?** Follow the steps above and transform your cold outreach with GPT-4 powered intelligence! 🚀 