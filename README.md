# Closet

Closet is a Telegram based wardrobe management application built with FastAPI.

The project allows users to create a Telegram linked account and manage their personal wardrobe. Users can add, update, delete, and view clothing items stored in their closet.

The project also includes an AI-powered recommendation endpoint using Gemini 2.5 Flash. Users can provide prompts such as:

```
I have a date tonight
```

or

```
I am meeting a friend
```

The AI analyzes the user's available clothing items and recommends the most suitable option, returning the result as structured JSON.

This project was built primarily to practice and demonstrate backend development skills, including:

* FastAPI
* SQLAlchemy
* SQLite
* REST API design
* AI integration with Gemini
* Dependency injection
* Testing with Pytest

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Gemini 2.5 Flash
* Pytest
* Uvicorn

## Dependencies

```txt
dotenv>=0.9.9
fastapi>=0.136.3
google-genai>=2.8.0
pytest>=9.0.3
sqlalchemy>=2.0.50
uvicorn>=0.49.0
```

## Running the Project

This project uses `uv` for package management.

Clone the repository:

```bash
git clone https://github.com/Iyosiprograming/closet.git
```

Create a virtual environment:

```bash
uv venv
```

Activate the environment and install dependencies:

```bash
uv sync
```

Navigate to the backend directory:

```bash
cd Backend
```

Run the application:

```bash
py main.py
```

## Future Improvements

Some features that could be added in future versions:

* Image upload and storage
* Outfit recommendations using multiple clothing items
* Weather-aware recommendations
* User authentication beyond Telegram IDs
* PostgreSQL support
* Recommendation history

## Project Goal

The goal of this project is to demonstrate practical backend development skills through a real world application that combines CRUD operations, database management, API development, and AI integration.

<img width="1920" height="1080" alt="Screenshot (3)" src="https://github.com/user-attachments/assets/081f77a6-bd00-4a8e-acfd-542755183ce2" />
<img width="1920" height="1080" alt="Screenshot (4)" src="https://github.com/user-attachments/assets/323a961e-1298-4980-a8a7-9b82cc467656" />
<img width="1920" height="1080" alt="Screenshot (5)" src="https://github.com/user-attachments/assets/8f970a28-3bbf-4352-8404-e9f92d04eb35" />


