# Trailing Versus

A Django application for creating and sharing trail verses.

## Naming Convention Note

In this project, we use "Versus" as the plural form of "Verse" in our code and URLs, even though this is not technically correct English (where "verses" would be the proper plural). This was a deliberate stylistic choice to give the project a unique identity and maintain consistency with the trail/hiking theme.

## Description

Trailing Versus is a Django application for creating and sharing verses inspired by hiking trails and outdoor experiences. Built with modern web technologies and a focus on user experience.

## Features

- Create and edit trail verses
- Syllable counting and manual override
- Verse grading system
- Clean, modern UI with Bootstrap 5
- Texas-themed styling

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trailingversus.git
cd trailingversus
```

2. Start the application:
```bash
docker compose up --build
```

3. Access the application at http://localhost:8000

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

```
trailingversus/
├── webapp/             # Main Django project
│   ├── trailing/      # Project configuration
│   │   ├── templates/ # Project-level templates
│   │   └── settings/ # Django settings
│   └── versus/       # Verses application
├── docker-compose.yml # Docker configuration
├── Dockerfile        # Docker build file
└── requirements.txt  # Python dependencies
```

## Development

See [docs/README.md](docs/README.md) for detailed development documentation.

## License

This project is licensed under the MIT License.
