# ❓ Frequently Asked Questions (FAQ)

## Q: What databases are supported?
A: PostgreSQL (default), SQLite (for quick testing), and MongoDB (NoSQL, optional).

## Q: How do I switch databases?
A: Change `database_type` in `app/core/config.py` and update `.env` and `docker-compose.yml` as needed.

## Q: How do I add a new model?
A: See `docs/EXTENDING_TEMPLATE.md` for step-by-step instructions for both SQL and MongoDB models.

## Q: How do I run tests?
A: Use `pytest` or the provided test scripts. See README and `docs/GETTING_STARTED.md`.

## Q: How do I deploy to production?
A: Follow the deployment steps in the README and `docs/GETTING_STARTED.md`. Use Docker for best results.

## Q: Is this template open source?
A: Yes! Licensed under MIT. Contributions are welcome.

## Q: Where can I get help?
A: Check the guides in `docs/`, open an issue on GitHub, or ask in FastAPI community channels.
