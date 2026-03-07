# Rententia Backend

FastAPI-based backend for the Retentia Platform. 

## Pre-requisites
- Python 3.8+
- SQLite

## Getting Started

1. Clone the Repository
2. Create a .env file based on .env.example
    ```bash
    cp .env.example .env
    ```
3. Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Run the Application
    ```bash
    uvicorn app.main:app --reload
    ```
## Testing
From the project root, run:
```
pytest
```
Run Specific Test Files
```
pytest tests/test_import.py
```
## Contributing
1. Fork and clone the repository
2. Create a branch (git checkout -b branch-name)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request linking the issue