"""
FastAPI application with Neon PostgreSQL and SQLModel.

Run with:
    uv run uvicorn main:app --reload
"""
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Session, select, col

from database import get_async_session, init_async_db


# =============================================================================
# Models
# =============================================================================

class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class User(UserBase, table=True):
    """User database model."""
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str


class UserCreate(UserBase):
    """User creation schema with password."""
    password: str


class UserRead(UserBase):
    """User response schema."""
    id: int


class UserUpdate(BaseModel):
    """User update schema - all fields optional."""
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class PostBase(BaseModel):
    """Base post model."""
    title: str
    content: str | None = None
    published: bool = False


class Post(PostBase, table=True):
    """Post database model."""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    author: User | None = None


class PostCreate(PostBase):
    """Post creation schema."""
    user_id: int


class PostRead(PostBase):
    """Post response schema."""
    id: int
    user_id: int


class PostWithAuthor(PostRead):
    """Post schema with nested author."""
    author: UserRead | None = None


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    # Initialize database tables
    await init_async_db()
    yield
    # Cleanup on shutdown (close connections, etc.)


# =============================================================================
# App Initialization
# =============================================================================

app = FastAPI(
    title="FastAPI + Neon + SQLModel",
    description="Example FastAPI application with Neon PostgreSQL and SQLModel",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health Check
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FastAPI with Neon PostgreSQL and SQLModel",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# =============================================================================
# User Routes
# =============================================================================

@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    session=Depends(get_async_session)
):
    """Create a new user."""
    # Check if email already exists
    result = await session.execute(
        select(User).where(User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user (hash password in production!)
    db_user = User.model_validate(user)
    db_user.hashed_password = user.password  # Use bcrypt in production!

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[UserRead])
async def list_users(
    offset: int = 0,
    limit: int = 100,
    session=Depends(get_async_session)
):
    """List all users with pagination."""
    result = await session.execute(
        select(User).offset(offset).limit(limit)
    )
    users = result.scalars().all()
    return users


@app.get("/users/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session=Depends(get_async_session)):
    """Get a specific user by ID."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@app.patch("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    session=Depends(get_async_session)
):
    """Update a user."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update only provided fields
    user_data = user_update.model_dump(exclude_unset=True)
    for field, value in user_data.items():
        setattr(user, field, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, session=Depends(get_async_session)):
    """Delete a user."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    await session.delete(user)
    await session.commit()


# =============================================================================
# Post Routes
# =============================================================================

@app.post("/posts/", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    session=Depends(get_async_session)
):
    """Create a new post."""
    # Verify user exists
    user = await session.get(User, post.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_4044_NOT_FOUND,
            detail="User not found"
        )

    db_post = Post.model_validate(post)
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post


@app.get("/posts/", response_model=List[PostWithAuthor])
async def list_posts(
    offset: int = 0,
    limit: int = 100,
    session=Depends(get_async_session)
):
    """List all posts with author information (relationship loading)."""
    result = await session.execute(
        select(Post)
        .offset(offset)
        .limit(limit)
    )
    posts = result.scalars().all()

    # Load authors for each post
    for post in posts:
        await session.refresh(post, ["author"])

    return posts


@app.get("/posts/{post_id}", response_model=PostWithAuthor)
async def get_post(post_id: int, session=Depends(get_async_session)):
    """Get a specific post by ID with author."""
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    await session.refresh(post, ["author"])
    return post


# =============================================================================
# Advanced Query Examples
# =============================================================================

@app.get("/users/search/")
async def search_users(
    q: str | None = None,
    session=Depends(get_async_session)
):
    """Search users by name or email."""
    if not q:
        return []

    result = await session.execute(
        select(User).where(
            (col(User.full_name).icontains(q)) | (col(User.email).icontains(q))
        )
    )
    return result.scalars().all()


@app.get("/posts/by-author/{author_id}")
async def posts_by_author(
    author_id: int,
    session=Depends(get_async_session)
):
    """Get all posts by a specific author."""
    result = await session.execute(
        select(Post).where(Post.user_id == author_id)
    )
    return result.scalars().all()


@app.get("/stats/")
async def get_stats(session=Depends(get_async_session)):
    """Get database statistics."""
    from sqlalchemy import func

    user_count_result = await session.execute(
        select(func.count()).select_from(User)
    )
    post_count_result = await session.execute(
        select(func.count()).select_from(Post)
    )

    return {
        "total_users": user_count_result.scalar(),
        "total_posts": post_count_result.scalar(),
    }
