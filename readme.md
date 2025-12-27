# AI Research Automation Agent

AI Research Automation Agent is a multi-agent AI system that autonomously performs technical research, technology comparisons, and analytical reporting.
It processes real-world web data, applies LLM-based reasoning, and generates professional-quality research reports through an end-to-end automated pipeline.

The system is designed for rapid research, objective comparison, and structured report generation, accessible via a production-ready API.

## Live Demo

- **API**: https://airesearchautomationagent-production.up.railway.app
- **Swagger**: https://airesearchautomationagent-production.up.railway.app/docs

## Problem

Researching technical topics and technology comparisons is time-consuming and fragmented.
Developers and researchers must manually plan research steps, search multiple sources, analyze content, and synthesize results into structured reports. This process is inefficient, error-prone, and difficult to scale.

## Solution

AI Research Automation Agent automates the entire research workflow using a multi-agent architecture.
Each agent is responsible for a specific research phase—planning, web search, analysis, and reporting—resulting in fast, consistent, and reproducible research outputs.

## Key Features

- Multi-agent research orchestration
- Autonomous research planning
- Real-world web data collection (Tavily Search API)
- LLM-powered analysis (Gemini 1.5 Flash / Pro)
- Markdown-based professional report generation
- Modular and extensible Python architecture
- Production-ready FastAPI backend
- Public API access with Swagger documentation

## Architecture Notes

- **Planner agent** decomposes research objectives into executable steps
- **Web search agent** retrieves up-to-date information from the internet
- **Analysis agent** synthesizes insights using LLM reasoning
- **Report agent** generates structured Markdown reports
- **Orchestrator** coordinates agents in a deterministic pipeline
- **FastAPI** exposes the system as an HTTP API
- **Docker** ensures environment parity across development and production

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **AI / LLM**: Google Gemini 1.5 (Flash / Pro)
- **Web Search**: Tavily Search API
- **Architecture**: Multi-agent orchestration
- **Infra**: Docker, Railway
- **Output**: Markdown-based report generation

## Getting Started

### Option 1: Docker (Recommended)

Build the Docker image:

```bash
docker build -t ai-research-automation-agent .
```

Run the container:

```bash
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_gemini_key \
  -e TAVILY_API_KEY=your_tavily_key \
  ai-research-automation-agent
```

Access Swagger UI:

```
http://localhost:8000/docs
```

### Option 2: Local Development

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn src.api.app:app --reload
```

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_key
TAVILY_API_KEY=your_tavily_key
SEARCH_API_KEY=your_tavily_key
DEFAULT_MODE=overview
DEFAULT_DEPTH=short
```

In production, these variables are injected via Railway's environment configuration.

## API Endpoints

### POST /research/overview

```json
{
  "topic": "vector databases",
  "depth": "short"
}
```

### POST /research/compare

```json
{
  "item_a": "PostgreSQL",
  "item_b": "MongoDB",
  "depth": "detailed"
}
```

### POST /research/custom

```json
{
  "query": "LLM training vs inference",
  "depth": "detailed"
}
```

## Example Output

```markdown
# Overview Report: Vector Databases

## Summary
LLM-generated technical summary...

## Key Points
- Vector representations
- Search performance
- Embedding-based querying

## Pros
- High retrieval accuracy

## Cons
- Increased computational cost in some scenarios
```

## Deployment

This project is Dockerized and deployed to Railway as a production service.

- Dockerfile-based build
- Dynamic port handling (`$PORT`)
- Public HTTP exposure
- Production-grade FastAPI runtime

**Live deployment**: https://airesearchautomationagent-production.up.railway.app

## Roadmap

- [ ] PDF report generation
- [ ] Multi-source citation tracking
- [ ] Advanced evaluation metrics for research quality
- [ ] Frontend dashboard for report visualization
- [ ] Support for additional LLM providers

## Contributing

Issues and pull requests are welcome.
For significant changes, please open an issue first to discuss scope and design.
