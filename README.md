# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite application that uses Google's Gemini API to generate a personalized 7-day workout plan, a nutrition/recovery tip, and a revised plan from user feedback.

## Architecture

- Frontend: HTML, CSS, Jinja2
- Backend: FastAPI
- AI: Google Gemini using the google-genai Python SDK
- Database: SQLite + SQLAlchemy
- Validation: Pydantic
- Server: Uvicorn

## Features

1. Personalized 7-day workout generation
2. Goal-aware planning
3. Intensity-aware planning
4. Nutrition/recovery tip
5. Feedback-based plan regeneration
6. SQLite persistence
7. Admin dashboard
8. JSON API
9. Swagger API documentation
10. Responsive frontend

## Requirements

- Python 3.11+
- Gemini API key
- VS Code recommended

## Windows Setup

Open the FitBuddy folder in VS Code.

Open:

Terminal → New Terminal

Create the virtual environment:

```powershell
py -3.11 -m venv .venv