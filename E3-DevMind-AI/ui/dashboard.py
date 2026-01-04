"""
E3 DevMind AI Web Dashboard

Simple web interface using FastAPI + HTML templates.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# This would be integrated with the main FastAPI app
# For now, it's a placeholder showing the structure

templates = Jinja2Templates(directory="ui/templates")

async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "E3 DevMind AI Dashboard"
    })

async def agents_page(request: Request):
    """Agents overview page"""
    return templates.TemplateResponse("agents.html", {
        "request": request,
        "title": "Agents - E3 DevMind AI"
    })

async def knowledge_page(request: Request):
    """Knowledge base page"""
    return templates.TemplateResponse("knowledge.html", {
        "request": request,
        "title": "Knowledge Base - E3 DevMind AI"
    })
