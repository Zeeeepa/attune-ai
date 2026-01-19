"""Empathy Framework - Minimal FastAPI Entrypoint

This is a minimal API entrypoint for deployment platforms that auto-detect FastAPI.
The Empathy Framework is primarily a CLI tool (`pip install empathy-framework`).

For the full wizards backend, see: deployments/wizards-backend/app.py
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Empathy Framework",
    description="Power tools for Claude Code. This is a minimal API - the framework is primarily CLI-based.",
    version="4.4.0",
    docs_url="/docs",
)


@app.get("/")
async def root():
    """Root endpoint with project info."""
    return {
        "name": "Empathy Framework",
        "version": "4.4.0",
        "description": "Power tools for Claude Code",
        "cli_install": "pip install empathy-framework",
        "docs": "https://smartaimemory.com/framework-docs/",
        "github": "https://github.com/Smart-AI-Memory/empathy-framework",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "4.4.0"}


@app.get("/docs-redirect")
async def docs_redirect():
    """Redirect to main documentation."""
    return RedirectResponse(url="https://smartaimemory.com/framework-docs/")
