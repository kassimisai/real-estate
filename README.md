# Ready Set Realtor

An AI-driven platform for real estate professionals that automates lead engagement, transaction coordination, and integrates with various CRMs and third-party services.

## Features

- **AI-Powered Lead Management**
  - Automated lead qualification and scoring
  - Smart follow-up scheduling
  - Personalized communication templates

- **Calendar Integration**
  - Google Calendar integration
  - Automated appointment scheduling
  - Availability management

- **Email Automation**
  - Template-based notifications
  - Transaction updates
  - Performance reports

- **Analytics Dashboard**
  - Lead conversion metrics
  - Transaction tracking
  - Performance visualization

- **Multi-Agent Coordination**
  - Task assignment and tracking
  - Team collaboration tools
  - Resource sharing

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Celery
- **Database**: PostgreSQL
- **Cache**: Redis
- **Authentication**: JWT, Supabase
- **External Services**: Google Calendar API, OpenAI API
- **Email**: SMTP with async support
- **Testing**: pytest

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Node.js (for frontend)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ready-set-realtor.git
   cd ready-set-realtor
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

### Running the Application

1. Start the Redis server

2. Start the Celery worker:
   ```bash
   celery -A app.worker worker --loglevel=info
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Visit http://localhost:8000/docs for API documentation

### Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
ready-set-realtor/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── templates/
│   │   └── mcp/
│   ├── tests/
│   └── alembic/
├── frontend/
└── docs/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - your.email@example.com
Project Link: https://github.com/yourusername/ready-set-realtor
