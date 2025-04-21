# Elegy

A modern, web-based document editor with real-time autosave and rich text editing capabilities.

## Description

Elegy provides a clean, distraction-free writing environment with automatic saving, document management, and a rich text editor. Built with Django and modern web technologies.

## Features

- Rich text editing with TipTap
- Real-time autosave
- Document management
- User authentication
- Clean, modern UI with TailwindCSS

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/elegy.git
cd elegy
```

2. Start the application:
```bash
docker compose up --build
```

3. Access the application at http://localhost:8000

4. Log in with:
   - Username: admin
   - Password: admin

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

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

```
elegy/
├── docs/               # Documentation
├── elegy/             # Main Django project
│   ├── editor/        # Editor application
│   ├── static/        # Static files
│   └── templates/     # HTML templates
├── data/              # SQLite database
├── docker-compose.yml # Docker configuration
├── Dockerfile         # Docker build file
└── requirements.txt   # Python dependencies
```

## Development

See [docs/README.md](docs/README.md) for detailed development documentation.

## License

This project is licensed under the MIT License.
