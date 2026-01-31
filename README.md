# HerpTracker - Reptile Health Tracker

A web application to track reptile health records including feeding, shedding, measurements, and defecation.

## Features

- 🦎 **Reptile Management**: Add, edit, and delete reptile profiles with photos
- 🍽️ **Feeding Records**: Track what and when your reptiles eat
- 🐍 **Shedding Records**: Monitor shed cycles and completeness
- 📏 **Measurements**: Record length and weight over time
- 💩 **Defecation Records**: Keep track of waste elimination
- 📊 **Statistics**: View days since last feeding, shedding, and defecation

## Tech Stack

- **Backend**: Python Flask with SQLAlchemy
- **Database**: SQLite (lightweight, file-based)
- **Web Server**: Apache with mod_wsgi
- **Container**: Docker

## Quick Start

### Using Docker (Recommended)

1. Build and start the container:
   ```bash
   docker-compose up --build
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:
   ```bash
   python -c "from app import create_app; create_app().run(debug=True, port=5000)"
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
HerpTracker/
├── app/
│   ├── __init__.py      # Flask app factory
│   ├── models.py        # Database models
│   ├── routes.py        # API routes
│   ├── static/
│   │   ├── css/         # Stylesheets
│   │   ├── js/          # JavaScript
│   │   └── uploads/     # Reptile images
│   └── templates/       # HTML templates
├── instance/            # SQLite database (created at runtime)
├── config.py            # Configuration
├── wsgi.py              # WSGI entry point
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose config
└── apache.conf          # Apache configuration
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard |
| GET | `/reptile/<id>` | Reptile profile |
| POST | `/api/reptile` | Create reptile |
| PUT | `/api/reptile/<id>` | Update reptile |
| DELETE | `/api/reptile/<id>` | Delete reptile |
| POST | `/api/reptile/<id>/feeding` | Add feeding |
| POST | `/api/reptile/<id>/shedding` | Add shedding |
| POST | `/api/reptile/<id>/measurement` | Add measurement |
| POST | `/api/reptile/<id>/defecation` | Add defecation |

## Notes

- **Database persistence**: The SQLite database is stored in a Docker volume for persistence.
- **Image uploads**: Uploaded images are stored in a separate Docker volume.

## License

MIT License
