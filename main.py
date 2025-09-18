from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import  Session
from datetime import datetime
import json

from database import get_db
from schemas import (
    UserCreate, UserResponse, PollCreate, PollResponse,
    VoteCreate, VoteResponse, PollOptionResponse
)
from database import User, Poll, PollOption, user_poll_option_votes
from websocket import manager
from auth import hash_password, verify_password

app = FastAPI(title="Real-Time Polling API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.on_event("startup")
async def startup():
    from database import create_tables
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

@app.get("/api/users", response_model=list[UserResponse])
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

@app.get("/api/polls", response_model=list[PollResponse])
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