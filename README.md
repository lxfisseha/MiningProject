# MiningProject

Try the live demo here:
https://miningproject-production.up.railway.app/

## What you can try
- Register and log in (make sure to approve the new user by logging in to the admin)
- Create profile for mining roles
- Create service requests for consulting, licenses, or mineral trading
- Upload and download profile documents
- Track request status and review request details

## Demo users you can use
- Admin: `admin@gmail.com` / `password`
- Staff: `staff@gmail.com` / `password`
- Buyer: `buyer@gmail.com` / `password`
- Consultant: `consultant@gmail.com` / `password`
- License Holder: `licenseholder@gmail.com` / `password`
- Equipment Owner: `equipmentowner@gmail.com` / `password`

Open the live URL and sign in with one of the accounts or create a new account to explore the app.

## Important Disclaimer

This is a **demo/portfolio project**, not a production-ready application. Please keep the following in mind:

- **Not hosting-ready** — uses SQLite (a dev database), local file storage, and has no real deployment pipeline.
- **Security is intentionally weak** — hardcoded secrets, no proper credential management, and no production-grade auth hardening.
- **May contain bugs** — some bugs and issues are **intentionally left in** the codebase for learning/review purposes. Do not judge the developer's coding skills based on this repo.
- **Missing production features** — no CI/CD, no background jobs, no caching, no structured logging, no health checks, no integration tests.
- **Incomplete areas** — some features are stubbed out or have placeholder code.

This project is meant to demonstrate FastAPI + HTMX architecture patterns, not to serve as a reference for production systems.
