# Render Deployment Guide

## Quick Deploy to Render

1. **Push your code to GitHub** (if not already done)
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Sign up/login with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your repository

3. **Render will automatically detect** the `render.yaml` configuration

## Configuration Details

- **Build Command**: `pip install -r requirements.txt && python main.py --clean --sets urzas`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT web_app:app`
- **Python Version**: 3.11.0

## What happens during deployment:

1. Dependencies are installed from `requirements.txt`
2. Database is populated with MTG cards from Urza's block
3. Web application starts on the assigned port

## Post-deployment:

Your MTG database will be accessible at the Render-provided URL with:
- Interactive SQL query interface
- Sample queries
- Database schema browser
- Read-only access for security

## Local Development:

```bash
# Install dependencies
uv sync

# Run locally
uv run python web_app.py
```

## Database Notes:

The SQLite database (`mtg_database.db`) will be created during the build process and populated with MTG card data from the Scryfall API. The database includes cards from Urza's block by default, but you can modify the `--sets` parameter in `render.yaml` to include other sets.
