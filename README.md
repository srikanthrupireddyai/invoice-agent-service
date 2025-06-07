# Auth Integration Service

A microservice that handles authentication with multiple accounting systems, starting with Zoho and easily extensible to other providers like QuickBooks and Xero.

## Project Structure

```
/invoice-agent-service
  /app
    /api
      /routes          - API endpoint definitions
    /core              - Core application components
    /db                - Database models and repositories
    /integrations      - Integration implementations for different accounting systems
    /schemas           - Pydantic models for request/response schemas
    /services          - Business logic and services
  .env                 - Environment variables (not committed to git)
  .env.example         - Example environment variables
  main.py              - Application entry point
  requirements.txt     - Dependencies
```

## Setup

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment: 
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your credentials
5. Run the application: `uvicorn main:app --reload`

## API Documentation

When the service is running, you can access the OpenAPI documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
