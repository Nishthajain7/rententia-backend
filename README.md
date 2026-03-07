# Retentia Backend

Retentia is a Memory-First Revision Platform designed to improve long-term learning retention. The system **predicts when users are likely to forget** a concept and intervenes with timely, personalized revisions.

Unlike traditional EdTech platforms that focus on content completion or test scores, Retentia **tracks forgetting at the concept level** and **schedules revisions** for those concepts when their recall is about to decline. Instead of revising the entire syllabus repeatedly, students are guided on **exactly what to revise**, saving time and effort.


## Pre-requisites
- Python 3.11+
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