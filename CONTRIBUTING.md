# Contributing to AI Text Humanizer

First off, thank you for considering contributing to AI Text Humanizer! It's people like you that make open-source software such a great community.

## Development Setup

1. Fork and clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment.
4. Install dependencies: `pip install -r requirements.txt` and `pip install pytest ruff httpx`
5. Download required models:
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
   ```
6. Run the local dev server: `uvicorn app.main:app --reload`

## Coding Standards

- We use **Ruff** for linting and formatting.
- Run `ruff check .` to check for lint errors.
- Run `ruff format .` to format your code before submitting a PR.
- Ensure all new features or bug fixes have corresponding tests in the `tests/` directory.

## Pull Request Process

1. Create a new branch for your feature (`git checkout -b feature/amazing-feature`).
2. Make your changes and commit them with clear, descriptive messages.
3. Push to your fork and submit a Pull Request against the `main` branch.
4. Ensure the CI pipeline (GitHub Actions) passes successfully.

We look forward to your contributions!
