# AI-Native Task Manager

A conversational task management system where users manage **tasks, reminders, and appointments** through natural language chat with AI agents.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      USER (Chat)                        │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│              Tasks Manager Agent (Orchestrator)          │
│         • Understands user intent                        │
│         • Routes to appropriate tools/agents             │
│         • Confirms actions with user                     │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
┌────────────▼────────────┐  ┌────────────▼───────────────┐
│    Tasks MCP Server     │  │  Appointment Booking Agent │
│  • CRUD task operations │  │  • Schedule appointments   │
│  • Database mutations   │  │  • Booking workflows       │
└────────────┬────────────┘  └────────────────────────────┘
             │
┌────────────▼────────────┐
│   Notifications System  │
│  • Reminders            │
│  • Alerts               │
└─────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Language** | Python 3.12+ |
| **Package Manager** | `uv` |
| **Agent Protocol** | MCP (Model Context Protocol) |
| **API** | FastAPI |
| **UI** | Next.js |
| **Container Registry** | GitHub Container Registry (ghcr.io) |
| **Deployment** | Kubernetes |

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| Tasks MCP Server | CRUD operations for tasks via MCP tools | Planned |
| Tasks Manager Agent | Main orchestrator - handles user chat | Planned |
| Appointment Booking Agent | Handles scheduling workflows | Planned |
| Notifications Service | Reminders & alerts | Planned |
| API Layer | REST endpoints | Planned |
| UI (Next.js) | Web interface | Planned |
| K8s Deployments | Helm charts, manifests | Planned |

## Key Principles

- **Test-first development** - Write tests before code
- **Docs-first** - Check official docs before coding
- **Kubernetes-ready** - Design for K8s from day one
- **Idempotent operations** - Safe retries
- **No guessing** - Confirm ambiguous dates/times with user
- **Small, reviewable changes**

## Getting Started

```bash
# Clone the repo
git clone https://github.com/musman7888/native-ai-task-manager.git
cd native-ai-task-manager

# Setup instructions coming soon...
```

## Project Structure

```
native-ai-task-manager/
├── AGENTS.md           # Project constitution & principles
├── CLAUDE.md           # Claude Code instructions
├── GEMINI.md           # Gemini instructions
├── README.md           # This file
├── services/           # Backend services (coming soon)
│   ├── tasks-mcp/      # Tasks MCP Server
│   └── notifications/  # Notifications service
├── agents/             # AI Agents (coming soon)
├── ui/                 # Next.js frontend (coming soon)
└── deployments/        # K8s manifests & Helm charts (coming soon)
```

## License

MIT
