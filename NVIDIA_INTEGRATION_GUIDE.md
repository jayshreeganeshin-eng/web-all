# NVIDIA NIM Integration Guide

## Overview

web-all now supports **NVIDIA NIM** (NVIDIA Inference Microservices) as an AI provider, alongside OpenRouter, Groq, HuggingFace, and Ollama. This integration works seamlessly in both **GUI** and **CLI** modes, supporting both **online** and **localhost** deployments.

---

## 🚀 Getting Your NVIDIA API Key

1. Visit [build.nvidia.com](https://build.nvidia.com)
2. Sign up or log in to your NVIDIA account
3. Navigate to the API section
4. Generate a new API key (starts with `nvapi-` or is a long alphanumeric string)
5. Copy your API key securely

---

## 🖥️ GUI Usage

### Step 1: Start the Server
```bash
web-all serve -p 8000
```

### Step 2: Configure AI Settings
1. Open your browser to `http://localhost:8000`
2. Click on the **"🤖 AI Settings"** tab
3. Check **"Enable AI Features"**
4. Select **"🚀 NVIDIA NIM"** from the provider cards
5. Paste your NVIDIA API key in the API Key field
6. (Optional) Specify a model (default: `meta/llama3-70b-instruct`)
7. Click **"💾 Save AI Configuration"**

### Step 3: Clone with AI Enhancement
1. Go to **"🚀 Clone Website"** tab
2. Enter your target URL
3. Check **"🤖 Enable AI Analysis"**
4. Click **"🚀 Start Cloning"**

The AI will automatically:
- Generate summaries
- Extract structured data
- Auto-tag content
- Filter irrelevant content

---

## 💻 CLI Usage

### Basic Usage with NVIDIA
```bash
web-all clone https://example.com \
  --ai-enabled \
  --ai-provider nvidia \
  --ai-key "your-nvidia-api-key-here"
```

### With Custom Model
```bash
web-all clone https://example.com \
  --ai-enabled \
  --ai-provider nvidia \
  --ai-key "your-nvidia-api-key-here" \
  --ai-model "meta/llama3-70b-instruct"
```

### Using Environment Variable
```bash
export NVIDIA_API_KEY="your-nvidia-api-key-here"
web-all clone https://example.com --ai-enabled --ai-provider nvidia
```

### Full Capture with AI
```bash
web-all clone https://example.com \
  --everything \
  --ai-provider nvidia \
  --ai-key "your-nvidia-api-key-here"
```

---

## 🔧 Available NVIDIA Models

Popular models available through NVIDIA NIM:

- `meta/llama3-70b-instruct` (default) - High-quality Llama 3 70B
- `meta/llama3-8b-instruct` - Faster, lighter Llama 3 8B
- `mistralai/mistral-large` - Mistral's largest model
- `google/gemma-7b` - Google's Gemma model
- `microsoft/phi-3` - Microsoft's Phi-3 model

Specify any model using `--ai-model`:
```bash
web-all clone https://example.com \
  --ai-provider nvidia \
  --ai-key "your-key" \
  --ai-model "mistralai/mistral-large"
```

---

## 🌐 Online vs Localhost

### Online Mode (Default)
All AI providers work online by default. No special configuration needed.

```bash
# Works immediately with internet connection
web-all clone https://example.com --ai-enabled --ai-provider nvidia --ai-key "your-key"
```

### Localhost Mode (Ollama Only)
For completely offline AI, use Ollama:

```bash
# Install Ollama first: https://ollama.ai
ollama pull llama3

# Use locally
web-all clone https://example.com --ai-enabled --ai-provider ollama
```

### Hybrid Setup
You can run the web-all server locally while using cloud AI:

```bash
# Terminal 1: Start server
web-all serve -p 8000

# Terminal 2: Use CLI or access GUI at http://localhost:8000
# All AI features work with cloud providers
```

---

## 📊 Comparison of AI Providers

| Provider | Free Tier | Speed | Quality | Best For |
|----------|-----------|-------|---------|----------|
| **NVIDIA NIM** | ✅ Yes | ⚡⚡⚡ Fast | ⭐⭐⭐⭐⭐ Excellent | Production, enterprise |
| **Groq** | ✅ Yes | ⚡⚡⚡⚡ Fastest | ⭐⭐⭐⭐ Very Good | Real-time applications |
| **OpenRouter** | ✅ Yes | ⚡⚡ Medium | ⭐⭐⭐⭐ Very Good | Multiple model choices |
| **HuggingFace** | ✅ Yes | ⚡ Slow-Medium | ⭐⭐⭐ Good | Experimentation |
| **Ollama** | ✅ Free | ⚡⚡ Depends on hardware | ⭐⭐⭐⭐ Good | Offline, privacy |

---

## 🔍 Troubleshooting

### "Valid NVIDIA API key required"
- Ensure your API key is at least 10 characters
- Check for extra spaces or quotes
- Verify key format (should start with `nvapi-` or be a long string)

### "AI analysis failed"
- Check your internet connection
- Verify API key is valid and has credits
- Try a different model
- Check NVIDIA service status at [status.nvidia.com](https://status.nvidia.com)

### GUI Not Showing NVIDIA Option
- Refresh the page (Ctrl+F5)
- Clear browser cache
- Ensure you're using web-all v4.2.0+

---

## 📝 Example Output

After cloning with NVIDIA AI enabled, you'll find:

```
output/
├── example_com/
│   ├── index.html          # Cloned webpage
│   ├── ai_analysis.json    # Structured AI analysis
│   └── SUMMARY.md          # Human-readable summary
```

**SUMMARY.md** example:
```markdown
# AI Analysis Summary: https://example.com

## Summary
This webpage provides information about example domain usage...

## Tags
example, domain, documentation, web, testing

## Structured Data
{
  "type": "documentation",
  "title": "Example Domain",
  "description": "Information about example.com"
}
```

---

## 🔐 Security Best Practices

1. **Never commit API keys** to version control
2. Use environment variables in production:
   ```bash
   export NVIDIA_API_KEY="your-key"
   ```
3. Rotate keys periodically
4. Monitor API usage on NVIDIA dashboard
5. Use separate keys for development and production

---

## 📚 Additional Resources

- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim/)
- [build.nvidia.com](https://build.nvidia.com) - Get API keys
- [NVIDIA API Catalog](https://catalog.ngc.nvidia.com/) - Browse models
- [web-all GitHub](https://github.com/jayshreeganeshin-eng/web-all) - Report issues

---

## ✅ Quick Start Checklist

- [ ] Get NVIDIA API key from build.nvidia.com
- [ ] Install/update web-all: `pip install -U web-all`
- [ ] Test CLI: `web-all clone https://example.com --ai-enabled --ai-provider nvidia --ai-key "your-key"`
- [ ] Or start GUI: `web-all serve -p 8000`
- [ ] Configure AI in GUI settings
- [ ] Clone your first site with AI enhancement!

---

**Version**: web-all v4.2.0+  
**Last Updated**: 2024  
**Support**: Open an issue on GitHub for assistance
