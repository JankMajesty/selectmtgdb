# MTG Database Query Interface

A Flask web application for querying Magic: The Gathering card data from a SQLite database populated via the Scryfall API.

## Features

- Read-only SQL query interface with security validations
- Pre-built sample queries for common searches
- Interactive schema browser
- Support for MTG blocks: Urza's, Masques, and Invasion
- Responsive web UI with dark/light mode support

## Local Development

### Prerequisites
- Python 3.11+
- uv (recommended) or pip

### Setup
```bash
# Install dependencies
uv sync

# Populate database (optional - for local development)
uv run python main.py --clean --sets all

# Run the web application
uv run python web_app.py
```

Visit `http://localhost:5000` to access the query interface.

## Deployment to Render

This app is configured for easy deployment to Render using the included `render.yaml` file.

### Steps:
1. Push your code to a GitHub repository
2. Connect your GitHub repo to Render
3. Render will automatically detect the `render.yaml` configuration
4. The app will build and deploy automatically

### Production Notes:
- The deployed version creates an empty database with schema only
- To populate with card data, you would need to run the data collection script separately
- The app uses Gunicorn as the production WSGI server

## Database Schema

The database uses a normalized schema with the following main tables:
- `Card` - Core card information
- `Artist`, `Rarity`, `CardSet` - Lookup tables
- `Color`, `CardType`, `SubType` - Card characteristics
- Junction tables for many-to-many relationships

## Security

- Read-only database access
- SQL injection protection
- Query validation (SELECT and WITH only)
- Result limits (1000 rows max)