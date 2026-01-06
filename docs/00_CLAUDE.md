# CSDL Agency - Claude Code Context
# Comprehensive project documentation for AI assistants
# Last Updated: 2026-01-01

## Project Overview

**Name:** CSDL Agency (LUBTFY Platform)
**Type:** Full-stack AI Agent Platform with Client Dashboard & Embeddable Chat Widget
**Purpose:** Multi-agent AI system with customer-facing chat widgets deployed on client websites
**Status:** Production on VPS (72.62.59.75)

## Critical Paths - MEMORIZE THESE

### Local Development
```
/home/christian/csdl-agency/                    # Root project directory
├── CSDL-Agent-UI/platform/                     # Main platform
│   ├── backend/                                # FastAPI backend
│   │   ├── app/                                # Application code
│   │   └── .env                                # Environment config
│   └── frontend/                               # Next.js frontend
│
├── CSDL-Agent-Chat-Widget/                     # THE ONLY CHAT WIDGET (use this!)
│   └── widget/                                 # Widget source
│       ├── src/                                # React/TypeScript source
│       │   └── components/InputField/          # Has voice input support
│       └── dist/                               # Built files for deployment
│
├── Archon/                                     # Knowledge base system
├── csdl-14b/                                   # Fine-tuned model training
└── docs/                                       # Documentation
```

### VPS Production (72.62.59.75)
```
/opt/lubtfy/                                    # Main deployment root
├── dashboard/                                  # Client dashboard (Flask)
│   ├── app.py                                  # Main Flask application
│   ├── templates/                              # Jinja2 templates
│   │   ├── settings.html                       # Client settings page
│   │   ├── integrations.html                   # Integration marketplace
│   │   ├── analytics.html                      # Analytics dashboard
│   │   ├── billing.html                        # Billing page
│   │   ├── conversations.html                  # Chat history
│   │   └── ...                                 # Other templates
│   └── static/                                 # Static assets
│
├── configs/                                    # Configuration files
│   └── clients.json                            # Client configurations (CRITICAL)
│
├── agent-backend/                              # Python agent backend
├── agent-data/                                 # Agent runtime data
├── archon/                                     # Archon knowledge base
├── deployment-api/                             # Client deployment API
├── secrets/                                    # Secret keys
└── logs/                                       # Application logs

/var/www/                                       # Nginx served files
├── html/
│   └── widget.js                               # Widget loader script
└── widget/                                     # Built widget files
    ├── assets/
    │   ├── main-*.js                           # Main widget bundle
    │   └── index-*.css                         # Widget styles
    └── index.html                              # Widget HTML
```

## Chat Widget - IMPORTANT

**THE ONLY CHAT WIDGET PROJECT:**
```
/home/christian/csdl-agency/CSDL-Agent-Chat-Widget/widget/
```

**DO NOT USE:**
- ~~`/home/christian/csdl-agency/CSDL-Agent-UI/platform/widget/`~~ (DELETED - was redundant)

### Building & Deploying Widget

```bash
# Build locally
cd /home/christian/csdl-agency/CSDL-Agent-Chat-Widget/widget
npm run build

# Deploy to VPS
scp -r dist/* root@72.62.59.75:/var/www/widget/
```

### Widget Features
- Voice input (Web Speech API) - requires `enableVoiceInput: true` in client config
- File upload support
- Dark/Light theme
- Customizable branding (colors, logo)
- Real-time messaging via WebSocket

### Widget Configuration (in clients.json)
```json
{
  "clients": {
    "client-id": {
      "customization": {
        "widgetTitle": "Chat with Us",
        "primaryColor": "#0073E6",
        "enableVoice": true,
        "enableVoiceInput": true,
        "enableFileUpload": false,
        "theme": "dark"
      }
    }
  }
}
```

## Client Dashboard

**Location:** `/opt/lubtfy/dashboard/` on VPS
**Framework:** Flask + Jinja2
**Templates:** `/opt/lubtfy/dashboard/templates/`

### Key Dashboard Pages
| Route | Template | Purpose |
|-------|----------|---------|
| `/` | dashboard.html | Main dashboard |
| `/settings` | settings.html | Widget & voice settings |
| `/integrations` | integrations.html | Integration marketplace |
| `/analytics` | analytics.html | Usage analytics |
| `/billing` | billing.html | Subscription management |
| `/conversations` | conversations.html | Chat history |
| `/live-support` | live-support.html | Real-time support |

### Updating Dashboard Templates

```bash
# Edit locally
# Templates are in /tmp/ during development sessions

# Upload to VPS
scp /tmp/settings.html root@72.62.59.75:/opt/lubtfy/dashboard/templates/
scp /tmp/app.py root@72.62.59.75:/opt/lubtfy/dashboard/

# Restart dashboard
ssh root@72.62.59.75 "systemctl restart lubtfy-dashboard"
```

## Configuration Files

### clients.json (CRITICAL)
**Location:** `/opt/lubtfy/configs/clients.json`
**Purpose:** All client configurations, API keys, customizations

```json
{
  "clients": {
    "lubtfy_ltd": {
      "name": "LUBTFY Ltd",
      "email": "client@example.com",
      "plan": "professional",
      "customization": {
        "widgetTitle": "Chat with Us",
        "primaryColor": "#0073E6",
        "enableVoice": true,
        "enableVoiceInput": true,
        "voiceProvider": "hume",
        "humeApiKey": "...",
        "elevenlabsApiKey": "..."
      },
      "subscription": {
        "plan": "professional",
        "monthlyQuota": 10000,
        "usedQuota": 1234
      }
    }
  }
}
```

### Environment Variables

**Backend (.env):** `/home/christian/csdl-agency/CSDL-Agent-UI/platform/.env`

Key sections:
```bash
# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant (Local)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Qdrant Cloud (Client Agents)
QDRANT_CLOUD_URL=https://...
QDRANT_CLOUD_API_KEY=...

# LLM Configuration
LLM_PROVIDER=hybrid
LLAMA_SERVER_URL=http://localhost:8080        # CSDL-14B
OLLAMA_BASE_URL=http://localhost:11434         # Single agents

# Tiered Models
OLLAMA_REASONING_MODEL=qwen2.5:14b-instruct-q4_K_M
OLLAMA_CONTENT_MODEL=qwen2.5:7b-instruct-q4_K_M
OLLAMA_CODER_MODEL=qwen2.5-coder:14b-instruct-q4_K_M

# CSDL Compression (85-92% token reduction)
CSDL_COMPRESSION_ENABLED=true
CSDL_DEFAULT_LEVEL=semantic

# CSDL-14B Model (llama.cpp server)
CSDL_14B_ENABLED=true
CSDL_14B_SERVER_URL=http://localhost:8080
```

## CSDL Compression System

CSDL (Context-Semantic Dynamic Language) reduces tokens by 85-92% for agent communication.

**Compression Levels:**
- `basic`: ~50% reduction (preserves readability)
- `enhanced`: ~70% reduction (optimized structure)
- `semantic`: ~85-92% reduction (embedding-based, highest)

**Used For:**
- Agent-to-agent communication
- Infinite memory system
- Knowledge base storage

## Voice Integration

### Supported Providers
1. **Hume AI** - Emotionally expressive TTS
2. **ElevenLabs** - High-quality voice synthesis
3. **Browser Speech API** - Voice input (free, built-in)

### Voice Settings Location
- Dashboard UI: `/settings` → Voice Settings tab
- Config: `clients.json` → `customization.voiceProvider`, `humeApiKey`, `elevenlabsApiKey`

### API Key Masking Pattern
```python
def mask_api_key(key):
    if not key or len(key) < 8:
        return None
    return key[:4] + "••••••••" + key[-4:]
```

## Integrations Marketplace

**Template:** `/opt/lubtfy/dashboard/templates/integrations.html`

### Available Integrations
| Integration | Status | Icon |
|------------|--------|------|
| Slack | Active | Inline SVG |
| Discord | Coming Soon | Inline SVG |
| WhatsApp | Coming Soon | Inline SVG |
| Zapier | Active | Inline SVG |
| HubSpot | Coming Soon | Orange sprocket SVG |
| Calendly | Coming Soon | 3 interlocking C's SVG |
| Google Calendar | Coming Soon | Inline SVG |

### Icon Guidelines
- Always use inline SVG (external URLs fail)
- HubSpot: Orange (#FF7A59) sprocket design
- Calendly: Three interlocking C-shapes (blue/cyan gradient)

## Services & Ports

### Local Development
| Service | Port | Command |
|---------|------|---------|
| Backend (FastAPI) | 8000 | `uvicorn app.main:app --reload` |
| Frontend (Next.js) | 3000 | `npm run dev` |
| PostgreSQL | 5432 | Docker or system |
| Redis | 6379 | Docker or system |
| Qdrant | 6333 | Docker |
| llama.cpp (CSDL-14B) | 8080 | `llama-server` |
| Ollama | 11434 | `ollama serve` |

### VPS Production
| Service | Port | Description |
|---------|------|-------------|
| Nginx | 80/443 | Reverse proxy |
| Dashboard | 5000 | Flask dashboard |
| Agent Backend | 8001 | Python agent API |
| Deployment API | 8002 | Client deployment |
| Widget | (static) | Served from /var/www/widget |

## Common SSH Commands

```bash
# Connect to VPS
ssh root@72.62.59.75

# View logs
docker logs lubtfy-dashboard --tail 50
journalctl -u lubtfy-dashboard -f

# Restart services
systemctl restart lubtfy-dashboard
systemctl restart nginx

# Check service status
systemctl status lubtfy-dashboard
systemctl status nginx

# Edit client config
nano /opt/lubtfy/configs/clients.json

# View nginx config
cat /etc/nginx/sites-enabled/agents
cat /etc/nginx/conf.d/widget.locations
```

## Deployment Workflow

### Updating Dashboard
```bash
# 1. Edit template locally (in /tmp/ during session)
# 2. Upload to VPS
scp /tmp/<template>.html root@72.62.59.75:/opt/lubtfy/dashboard/templates/

# 3. Restart dashboard
ssh root@72.62.59.75 "systemctl restart lubtfy-dashboard"
```

### Updating Widget
```bash
# 1. Build widget
cd /home/christian/csdl-agency/CSDL-Agent-Chat-Widget/widget
npm run build

# 2. Deploy to VPS
scp -r dist/* root@72.62.59.75:/var/www/widget/

# 3. Clear browser cache or hard refresh
```

### Updating Backend
```bash
# 1. Make changes locally
# 2. Push to git
git add . && git commit -m "message" && git push

# 3. Pull on VPS and restart
ssh root@72.62.59.75 "cd /opt/lubtfy/agent-backend && git pull && systemctl restart lubtfy-agent"
```

## Project Structure Summary

```
csdl-agency/
├── CLAUDE.md                          # THIS FILE - AI context
├── CSDL-Agent-UI/                     # Main platform
│   └── platform/
│       ├── backend/                   # FastAPI backend
│       ├── frontend/                  # Next.js frontend
│       └── .env                       # Environment config
│
├── CSDL-Agent-Chat-Widget/            # Chat widget (THE ONLY ONE)
│   ├── widget/                        # Widget source & build
│   ├── backend/                       # Widget backend
│   └── deployment/                    # Deployment configs
│
├── Archon/                            # Knowledge base system
├── csdl-14b/                          # Fine-tuned model
├── csdl-anlt/                         # Compression system
├── docs/                              # Documentation
└── scripts/                           # Utility scripts
```

## Troubleshooting

### Widget not showing voice button
1. Check `clients.json` → `enableVoiceInput: true`
2. Ensure using correct widget from `/home/christian/csdl-agency/CSDL-Agent-Chat-Widget/`
3. Rebuild and redeploy widget

### Dashboard changes not appearing
1. Clear browser cache (Ctrl+Shift+R)
2. Check template was uploaded: `ssh root@72.62.59.75 "ls -la /opt/lubtfy/dashboard/templates/"`
3. Restart dashboard: `systemctl restart lubtfy-dashboard`

### API keys not saving
1. Check `clients.json` permissions: `chmod 644 /opt/lubtfy/configs/clients.json`
2. Verify JSON syntax: `python3 -c "import json; json.load(open('/opt/lubtfy/configs/clients.json'))"`

### Widget loader 404
1. Check `/var/www/html/widget.js` exists
2. Verify nginx config serves it correctly
3. Check for correct asset paths in loader

## Git Workflow

```bash
# Main repository
cd /home/christian/csdl-agency
git status
git add .
git commit -m "Description of changes"
git push

# Widget repository (separate)
cd /home/christian/csdl-agency/CSDL-Agent-Chat-Widget
git status
git add .
git commit -m "Description of changes"
git push
```

## Important Notes

1. **Always use the correct widget:** `/home/christian/csdl-agency/CSDL-Agent-Chat-Widget/`
2. **External image URLs fail:** Always use inline SVG for icons
3. **Voice input requires:** `enableVoice: true` AND `enableVoiceInput: true`
4. **API keys should be masked:** Show `xxxx••••••••xxxx` format in UI
5. **Templates are Jinja2:** Use `{{ variable }}` and `{% if %}` syntax
6. **Widget is React/TypeScript:** Build with `npm run build`

---

**VPS IP:** 72.62.59.75
**Domain:** agents.lubtfy.com
**Last Updated:** 2026-01-01
