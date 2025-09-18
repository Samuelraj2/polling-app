# Real-Time Polling Application - Python Backend

A modern real-time polling application built with FastAPI, SQLAlchemy, PostgreSQL, and WebSockets.

## Features

- **RESTful API** for CRUD operations on users, polls, and votes
- **Real-time updates** via WebSockets when votes are cast
- **Secure password hashing** using bcrypt
- **Relational database design** with proper foreign key relationships
- **Many-to-many relationship** handling for user votes
- **CORS support** for frontend integration

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Real-time Communication**: WebSockets
- **Password Hashing**: Passlib with bcrypt
- **Data Validation**: Pydantic

## Database Schema

### Models and Relationships

- **User**: id, name, email, password_hash, created_at
- **Poll**: id, question, is_published, created_at, updated_at, creator_id
- **PollOption**: id, text, poll_id, created_at
- **Vote**: Many-to-many relationship table linking users to poll options

### Relationships

- **One-to-Many**: User → Polls (one user can create many polls)
- **One-to-Many**: Poll → PollOptions (one poll can have many options)
- **Many-to-Many**: User ↔ PollOptions (users can vote on multiple options, options can be voted by multiple users)

## Setup and Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd polling-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**
   ```sql
   CREATE DATABASE polling_db;
   CREATE USER polling_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE polling_db TO polling_user;
   ```

5. **Set environment variable**
   ```bash
   export DATABASE_URL="postgresql://polling_user:your_password@localhost/polling_db"
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`
Interactive API documentation at `http://localhost:8000/docs`

## API Endpoints

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users` - Get all users (paginated)

### Polls
- `POST /api/polls?creator_id={id}` - Create a new poll
- `GET /api/polls/{poll_id}` - Get poll by ID with vote counts
- `GET /api/polls` - Get all published polls (paginated)

### Votes
- `POST /api/votes?user_id={id}` - Cast a vote

### WebSocket
- `WS /ws/{poll_id}` - Real-time poll updates

## Usage Examples

### Create a User
```bash
curl -X POST "http://localhost:8000/api/users" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John Doe",
       "email": "john@example.com",
       "password": "securepassword"
     }'
```

### Create a Poll
```bash
curl -X POST "http://localhost:8000/api/polls?creator_id=1" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is your favorite programming language?",
       "is_published": true,
       "options": [
         {"text": "Python"},
         {"text": "JavaScript"},
         {"text": "Java"},
         {"text": "Go"}
       ]
     }'
```

### Cast a Vote
```bash
curl -X POST "http://localhost:8000/api/votes?user_id=1" \
     -H "Content-Type: application/json" \
     -d '{
       "poll_option_id": 1
     }'
```

## Real-time Features

### WebSocket Connection

Connect to a poll's real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/1');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'poll_update') {
        // Update UI with new vote counts
        console.log('Poll updated:', data.poll);
    }
};
```

When a vote is cast, all connected clients subscribed to that poll will receive an instant update with the new vote counts.

## Testing

### Manual Testing
1. Start the server
2. Open `http://localhost:8000/docs` for interactive API testing
3. Create users and polls using the API
4. Test real-time functionality by connecting to WebSocket endpoints

### Example Test Flow
1. Create two users
2. Create a poll with the first user
3. Connect to the poll's WebSocket endpoint
4. Cast votes from different users
5. Observe real-time updates in the WebSocket connection

## Production Considerations

- Set up proper environment variables for database connection
- Configure CORS appropriately for your frontend domain
- Implement authentication and authorization
- Add input validation and error handling
- Set up logging and monitoring
- Use connection pooling for database
- Implement rate limiting
- Add comprehensive tests

## Architecture Notes

This application demonstrates:
- **Clean Architecture**: Separation of concerns with clear layers
- **Database Design**: Proper relational model with foreign keys
- **Real-time Communication**: Efficient WebSocket implementation
- **RESTful Design**: Standard HTTP methods and status codes
- **Data Validation**: Pydantic models for request/response validation