# BlogZ Backend API

REST API for the BlogZ blogging platform, built with **FastAPI** and **MongoDB**.

## Tech Stack

- **FastAPI** — Modern async Python web framework
- **MongoDB** — NoSQL database (via Motor async driver)
- **JWT** — Token-based authentication
- **Pydantic v2** — Data validation and serialization
- **Docker** — Containerized deployment

## Quick Start

### 1. Prerequisites

- Python 3.11+
- MongoDB instance (local or [MongoDB Atlas](https://www.mongodb.com/atlas) free tier)

### 2. Setup

```bash
# Navigate to backend directory
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:
```
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/blogz
JWT_SECRET=your-random-secret-key
CORS_ORIGINS=http://localhost:8000,http://localhost:5500
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### 5. API Documentation

Once running, visit:
- **Swagger UI**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **ReDoc**: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user (protected) |

### Blogs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/blogs` | List published blogs |
| GET | `/api/blogs/categories` | List categories |
| GET | `/api/blogs/{id}` | Get single blog |
| POST | `/api/blogs` | Create blog (protected) |
| PUT | `/api/blogs/{id}` | Update blog (protected) |
| DELETE | `/api/blogs/{id}` | Delete blog (protected) |

### Stories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stories` | Get user's stories (protected) |
| POST | `/api/stories` | Create story (protected) |
| GET | `/api/stories/{id}` | Get single story |
| PUT | `/api/stories/{id}` | Update story (protected) |
| DELETE | `/api/stories/{id}` | Delete story (protected) |
| PATCH | `/api/stories/{id}/publish` | Publish a draft (protected) |
| GET | `/api/stories/{id}/stats` | Get story stats (protected) |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/profile` | Get profile (protected) |
| PUT | `/api/users/profile` | Update profile (protected) |
| POST | `/api/users/{id}/follow` | Follow user (protected) |
| POST | `/api/users/{id}/unfollow` | Unfollow user (protected) |
| GET | `/api/users/stats` | Get user stats (protected) |

### Library
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/library/lists` | Get reading lists (protected) |
| POST | `/api/library/lists` | Create list (protected) |
| PUT | `/api/library/lists/{id}` | Update list (protected) |
| DELETE | `/api/library/lists/{id}` | Delete list (protected) |
| POST | `/api/library/lists/{id}/stories` | Add story to list (protected) |
| GET | `/api/library/bookmarks` | Get bookmarks (protected) |
| POST | `/api/library/bookmarks/{story_id}` | Bookmark story (protected) |
| DELETE | `/api/library/bookmarks/{story_id}` | Remove bookmark (protected) |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments/{story_id}` | Get story comments |
| POST | `/api/comments/{story_id}` | Add comment (protected) |
| DELETE | `/api/comments/{id}` | Delete comment (protected) |

## Docker Deployment

```bash
# Build image
docker build -t blogz-backend .

# Run container
docker run -p 8000:8000 --env-file .env blogz-backend
```

## Deploy to Railway/Render

1. Push your code to GitHub
2. Connect your repo to Railway or Render
3. Set environment variables (`MONGODB_URI`, `JWT_SECRET`, `CORS_ORIGINS`)
4. The Dockerfile will be auto-detected and used for deployment
