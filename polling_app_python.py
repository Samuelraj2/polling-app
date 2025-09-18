# Real-Time Polling Application - Python Backend
# Requirements: FastAPI, SQLAlchemy, PostgreSQL, WebSockets

# README.md
"""
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
"""

# docker-compose.yml
"""
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: polling_db
      POSTGRES_USER: polling_user
      POSTGRES_PASSWORD: polling_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://polling_user:polling_password@db/polling_db
    depends_on:
      - db
    volumes:
      - ./:/app

volumes:
  postgres_data:
"""

# Dockerfile
"""
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# requirements.txt
"""
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
websockets==11.0.3
python-multipart==0.0.6
"""

# database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/polling_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Many-to-many relationship table for votes
user_poll_option_votes = Table(
    'votes',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('poll_option_id', Integer, ForeignKey('poll_options.id'), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    polls = relationship("Poll", back_populates="creator")
    voted_options = relationship("PollOption", secondary=user_poll_option_votes, back_populates="voters")

class Poll(Base):
    __tablename__ = "polls"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="polls")
    options = relationship("PollOption", back_populates="poll", cascade="all, delete-orphan")

class PollOption(Base):
    __tablename__ = "poll_options"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500), nullable=False)
    poll_id = Column(Integer, ForeignKey("polls.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    poll = relationship("Poll", back_populates="options")
    voters = relationship("User", secondary=user_poll_option_votes, back_populates="voted_options")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# schemas.py - Pydantic models for API
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PollOptionCreate(BaseModel):
    text: str

class PollOptionResponse(BaseModel):
    id: int
    text: str
    vote_count: int = 0
    
    class Config:
        from_attributes = True

class PollCreate(BaseModel):
    question: str
    options: List[PollOptionCreate]
    is_published: bool = False

class PollResponse(BaseModel):
    id: int
    question: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    creator_id: int
    options: List[PollOptionResponse]
    
    class Config:
        from_attributes = True

class VoteCreate(BaseModel):
    poll_option_id: int

class VoteResponse(BaseModel):
    user_id: int
    poll_option_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# main.py - FastAPI application
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import List
import json
import asyncio

app = FastAPI(title="Real-Time Polling API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.poll_subscribers: dict = {}  # poll_id -> [websockets]
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Remove from poll subscribers
        for poll_id, connections in self.poll_subscribers.items():
            if websocket in connections:
                connections.remove(websocket)
    
    def subscribe_to_poll(self, poll_id: int, websocket: WebSocket):
        if poll_id not in self.poll_subscribers:
            self.poll_subscribers[poll_id] = []
        if websocket not in self.poll_subscribers[poll_id]:
            self.poll_subscribers[poll_id].append(websocket)
    
    async def broadcast_poll_update(self, poll_id: int, data: dict):
        if poll_id in self.poll_subscribers:
            disconnected = []
            for connection in self.poll_subscribers[poll_id]:
                try:
                    await connection.send_text(json.dumps(data))
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.poll_subscribers[poll_id].remove(conn)

manager = ConnectionManager()

# API Routes

@app.on_event("startup")
async def startup():
    create_tables()

# User endpoints
@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/users", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Poll endpoints
@app.post("/api/polls", response_model=PollResponse)
def create_poll(poll: PollCreate, creator_id: int, db: Session = Depends(get_db)):
    # Verify creator exists
    creator = db.query(User).filter(User.id == creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    
    # Create poll
    db_poll = Poll(
        question=poll.question,
        is_published=poll.is_published,
        creator_id=creator_id
    )
    db.add(db_poll)
    db.commit()
    db.refresh(db_poll)
    
    # Create poll options
    for option_data in poll.options:
        db_option = PollOption(
            text=option_data.text,
            poll_id=db_poll.id
        )
        db.add(db_option)
    
    db.commit()
    
    # Return poll with options and vote counts
    return get_poll_with_votes(db_poll.id, db)

@app.get("/api/polls/{poll_id}", response_model=PollResponse)
def get_poll(poll_id: int, db: Session = Depends(get_db)):
    return get_poll_with_votes(poll_id, db)

@app.get("/api/polls", response_model=List[PollResponse])
def get_polls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    polls = db.query(Poll).filter(Poll.is_published == True).offset(skip).limit(limit).all()
    return [get_poll_with_votes(poll.id, db) for poll in polls]

def get_poll_with_votes(poll_id: int, db: Session):
    poll = db.query(Poll).filter(Poll.id == poll_id).first()
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    # Get options with vote counts
    options_with_votes = []
    for option in poll.options:
        vote_count = len(option.voters)
        option_response = PollOptionResponse(
            id=option.id,
            text=option.text,
            vote_count=vote_count
        )
        options_with_votes.append(option_response)
    
    return PollResponse(
        id=poll.id,
        question=poll.question,
        is_published=poll.is_published,
        created_at=poll.created_at,
        updated_at=poll.updated_at,
        creator_id=poll.creator_id,
        options=options_with_votes
    )

# Vote endpoints
@app.post("/api/votes", response_model=VoteResponse)
async def cast_vote(vote: VoteCreate, user_id: int, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify poll option exists
    poll_option = db.query(PollOption).filter(PollOption.id == vote.poll_option_id).first()
    if not poll_option:
        raise HTTPException(status_code=404, detail="Poll option not found")
    
    # Check if user already voted for this poll
    existing_votes = db.query(user_poll_option_votes).filter(
        user_poll_option_votes.c.user_id == user_id
    ).all()
    
    poll_option_ids_for_poll = [opt.id for opt in poll_option.poll.options]
    for existing_vote in existing_votes:
        if existing_vote.poll_option_id in poll_option_ids_for_poll:
            raise HTTPException(status_code=400, detail="User has already voted for this poll")
    
    # Cast the vote
    if poll_option not in user.voted_options:
        user.voted_options.append(poll_option)
        db.commit()
    
    # Broadcast real-time update
    poll_data = get_poll_with_votes(poll_option.poll_id, db)
    await manager.broadcast_poll_update(poll_option.poll_id, {
        "type": "poll_update",
        "poll": poll_data.dict()
    })
    
    return VoteResponse(
        user_id=user_id,
        poll_option_id=vote.poll_option_id,
        created_at=datetime.utcnow()
    )

# WebSocket endpoint
@app.websocket("/ws/{poll_id}")
async def websocket_endpoint(websocket: WebSocket, poll_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    manager.subscribe_to_poll(poll_id, websocket)
    
    # Send initial poll data
    try:
        poll_data = get_poll_with_votes(poll_id, db)
        await websocket.send_text(json.dumps({
            "type": "initial_data",
            "poll": poll_data.dict()
        }))
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)