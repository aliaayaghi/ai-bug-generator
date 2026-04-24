# Project: bug-report-ai

## Goal
Build a monorepo web app with:
- frontend: React + Vite
- backend: FastAPI
- database: SQLite first
- ORM/migrations: SQLAlchemy 2.x + Alembic

The app lets a user upload a screenshot, sends it to the backend, analyzes it with an AI vision provider, generates a structured bug report, stores the result, and shows the saved report in the UI.

## Architecture rules
- This is a modular monolith, not microservices.
- Keep backend code separated into:
  - api
  - core
  - db
  - repositories
  - schemas
  - services
- Routes must stay thin.
- Routes should parse requests, call services, and return responses.
- Services contain workflow and business logic.
- Repositories contain database access only.
- Database-specific details must stay out of routes and UI code.
- AI-provider-specific code must stay inside service or infrastructure files, not in routes.
- Start with SQLite, but keep the design ready for a later switch to PostgreSQL.
- Prefer simple, explicit code over clever abstractions.
- Do not introduce microservices, message queues, Docker orchestration, or authentication unless explicitly asked.
- Do not create generic base classes unless they are actually needed.

## Backend rules
- Use FastAPI.
- Use Pydantic models for API schemas.
- Use SQLAlchemy 2 style.
- Use Alembic for migrations.
- Use dependency injection for DB session access.
- Keep files small and focused.
- Do not put SQL queries directly inside route files.

## Frontend rules
- Use React + Vite.
- Keep the frontend structure simple and feature-oriented.
- Create a small shared API client layer.
- Do not call the AI provider directly from the frontend.
- Do not put backend URLs inline all over the app.

## Working rules for Codex
- For every task, start by listing:
  1. goal
  2. files to create or change
  3. commands to run for verification
- Then implement only the requested task.
- Do not change unrelated files.
- Do not add extra features.
- If a dependency is needed, explain exactly why before adding it.
- After making changes, report:
  - files changed
  - what was done
  - how to run or verify it
  - any follow-up risks or TODOs
- If the request is ambiguous, make the smallest reasonable assumption and state it.
- Prefer one small task at a time.

## Definition of done for most tasks
- Code compiles or runs for the requested scope.
- Naming is clean.
- No unrelated refactors.
- Clear verification steps are provided.