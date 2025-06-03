# Whiteboard Collaboration App

A full-stack Django web application for real-time whiteboard collaboration with advanced security features and machine learning integration.

## Features

- **Real-time Collaboration**: Multiple users can draw simultaneously using WebSockets
- **Authentication System**: User registration, login, and permission-based access
- **Drawing Tools**: Freehand drawing, shapes, text, eraser with customizable colors and thickness
- **Database Integration**: PostgreSQL/SQLite with Django ORM for persistent storage
- **Security**: CSRF protection, input sanitization, and optional data encryption
- **Analytics Dashboard**: Chart.js visualization for whiteboard usage statistics
- **Export Functionality**: Download whiteboards as PNG images
- **ML Integration**: Shape recognition suggestions using TensorFlow.js

## Technology Stack

- **Backend**: Django 4.2.7 with Django Channels for WebSockets
- **Frontend**: HTML5 Canvas with Fabric.js 5.3.1
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: Redis with Django Channels
- **Charts**: Chart.js 4.4.3
- **Security**: Django's built-in security features + custom implementations

## Setup Instructions

### Prerequisites

- Python 3.8+
- Redis Server
- PostgreSQL (for production)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd Django_Attempt
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Redis server**:
   ```bash
   redis-server
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

1. **Register/Login**: Create an account or login to start using whiteboards
2. **Create Whiteboard**: Click "Create New Whiteboard" and set privacy settings
3. **Drawing Tools**: Use the toolbar to select drawing tools, colors, and thickness
4. **Real-time Collaboration**: Share whiteboard URLs with others for simultaneous editing
5. **Save & Export**: Whiteboards auto-save; use export button to download as PNG
6. **Analytics**: Admins can view usage statistics in the dashboard

## Security Features

- CSRF protection on all forms and AJAX requests
- User authentication and authorization
- Input sanitization and validation
- Optional data encryption for sensitive whiteboards
- Secure WebSocket connections

## Machine Learning Integration

The app includes suggestions for shape recognition using TensorFlow.js:
- Converts rough shapes to perfect geometric forms
- Client-side processing for better performance
- Extensible architecture for additional ML features

## Deployment

### Heroku Deployment

1. Install Heroku CLI and login
2. Create Heroku app: `heroku create your-app-name`
3. Add Redis addon: `heroku addons:create heroku-redis:mini`
4. Add PostgreSQL: `heroku addons:create heroku-postgresql:mini`
5. Set environment variables:
   ```bash
   heroku config:set DJANGO_SETTINGS_MODULE=whiteboard_app.settings
   heroku config:set SECRET_KEY=your-secret-key
   ```
6. Deploy: `git push heroku main`
7. Run migrations: `heroku run python manage.py migrate`

### Render Deployment

1. Connect your GitHub repository to Render
2. Add Redis and PostgreSQL services
3. Set environment variables in Render dashboard
4. Deploy with automatic builds

## API Endpoints

- `GET /` - Homepage with whiteboard list
- `POST /create/` - Create new whiteboard
- `GET /whiteboard/<int:id>/` - View/edit whiteboard
- `POST /api/save-whiteboard/` - Save whiteboard data
- `GET /analytics/` - Admin analytics dashboard
- WebSocket: `/ws/whiteboard/<int:id>/` - Real-time collaboration

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## Testing

Run tests with:
```bash
python manage.py test
```

Test WebSocket connections locally by opening multiple browser tabs to the same whiteboard.

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the GitHub repository.
