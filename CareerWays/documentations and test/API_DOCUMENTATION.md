# CareerWays API Documentation

Base URL: `http://localhost:5000/api`

## Authentication Endpoints

### POST /auth/signup
Register a new user.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-04-24T10:00:00"
  }
}
```

---

### POST /auth/login
Login a user.

**Request:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-04-24T10:00:00"
  }
}
```

---

### POST /auth/verify
Verify JWT token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Token valid",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-04-24T10:00:00"
  }
}
```

---

### POST /auth/refresh
Refresh JWT token.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Token refreshed",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### POST /auth/logout
Logout user.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

## Assessment Endpoints

### POST /assessments/analyze
Analyze student response and generate recommendations.

**Request:**
```json
{
  "response": "I'm passionate about technology and love programming. I've worked with Python and JavaScript. My goal is to become a software engineer.",
  "userType": "guest"
}
```

**Response (200):**
```json
{
  "message": "Assessment analyzed successfully",
  "assessment_id": "550e8400-e29b-41d4-a716-446655440000",
  "skills": ["python", "javascript", "programming"],
  "interests": ["Technology", "Engineering"],
  "sentiment": "Positive",
  "experience": "python javascript worked engineer",
  "courses": [
    {
      "id": "course-001",
      "name": "BS Information Technology",
      "description": "Comprehensive IT education...",
      "match_score": 92.5,
      "difficulty": "Advanced"
    }
  ],
  "match_scores": {
    "course-001": 92.5,
    "course-002": 85.3
  },
  "overall_match_score": 88.9
}
```

---

### GET /assessments/<id>
Get assessment results by ID.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_response": "I'm passionate about technology...",
  "skills": ["python", "javascript"],
  "interests": ["Technology"],
  "sentiment": "Positive",
  "sentiment_score": 0.8,
  "experience": "python javascript worked",
  "courses": [
    {
      "id": "course-001",
      "name": "BS Information Technology",
      "description": "...",
      "match_score": 92.5
    }
  ],
  "match_score": 88.9,
  "created_at": "2026-04-24T10:00:00"
}
```

---

### GET /assessments/list
List all assessments for current user (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Assessments retrieved",
  "assessments": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "date": "2026-04-24",
      "match_score": 88.9,
      "courses": ["course-001", "course-002"],
      "created_at": "2026-04-24T10:00:00"
    }
  ]
}
```

---

### DELETE /assessments/<id>
Delete assessment (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Assessment deleted"
}
```

---

## Recommendation Endpoints

### GET /recommendations/courses
Get all available courses.

**Response (200):**
```json
{
  "message": "Courses retrieved",
  "courses": [
    {
      "id": "course-001",
      "name": "BS Information Technology",
      "description": "Comprehensive IT education...",
      "duration": "4 years",
      "difficulty": "Advanced",
      "career_path": "IT Professional",
      "skills_learned": ["Programming", "Networking"],
      "category": "IT"
    }
  ],
  "count": 22
}
```

---

### GET /recommendations/courses/<id>
Get detailed course information.

**Response (200):**
```json
{
  "message": "Course retrieved",
  "course": {
    "id": "course-001",
    "name": "BS Information Technology",
    "description": "...",
    "duration": "4 years",
    "difficulty": "Advanced",
    "career_path": "IT Professional",
    "skills_learned": ["Programming", "Networking", "Database"],
    "career_prospects": "Work as Software Developer or IT Consultant",
    "requirements": "Strong problem-solving skills",
    "category": "IT",
    "favorites_count": 15,
    "is_favorited": true
  }
}
```

---

### GET /recommendations/search?q=query
Search courses by keyword.

**Response (200):**
```json
{
  "message": "Search completed",
  "query": "programming",
  "courses": [
    {
      "id": "course-001",
      "name": "BS Information Technology",
      "description": "...",
      "category": "IT"
    }
  ],
  "count": 3
}
```

---

### GET /recommendations/categories
Get all course categories.

**Response (200):**
```json
{
  "message": "Categories retrieved",
  "categories": ["IT", "Healthcare", "Business", "Education", "Arts", "Hospitality"]
}
```

---

### GET /recommendations/categories/<category>
Get courses by category.

**Response (200):**
```json
{
  "message": "Courses retrieved",
  "category": "IT",
  "courses": [
    {
      "id": "course-001",
      "name": "BS Information Technology",
      "description": "..."
    }
  ],
  "count": 5
}
```

---

## User Endpoints

### GET /users/profile
Get user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Profile retrieved",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-04-24T10:00:00",
    "assessments_count": 3,
    "favorites_count": 5
  }
}
```

---

### PUT /users/profile
Update user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "name": "John Smith",
  "email": "johnsmith@example.com"
}
```

**Response (200):**
```json
{
  "message": "Profile updated",
  "user": {
    "id": 1,
    "name": "John Smith",
    "email": "johnsmith@example.com",
    "created_at": "2026-04-24T10:00:00"
  }
}
```

---

### POST /users/change-password
Change user password (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "old_password": "password123",
  "new_password": "newpassword123"
}
```

**Response (200):**
```json
{
  "message": "Password updated successfully"
}
```

---

### GET /users/favorites
Get user favorite courses (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Favorites retrieved",
  "favorites": [
    {
      "id": "course-001",
      "name": "BS Information Technology",
      "description": "...",
      "saved_at": "2026-04-24T09:00:00"
    }
  ],
  "count": 5
}
```

---

### POST /users/favorites
Add course to favorites (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "course_id": "course-001"
}
```

**Response (201):**
```json
{
  "message": "Course added to favorites"
}
```

---

### DELETE /users/favorites/<course_id>
Remove course from favorites (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Course removed from favorites"
}
```

---

### GET /users/stats
Get user statistics (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "message": "Statistics retrieved",
  "stats": {
    "assessments_completed": 5,
    "favorite_courses": 8,
    "average_match_score": 85.5
  }
}
```

---

### DELETE /users/delete-account
Delete user account (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Account deleted successfully"
}
```

---

## Favorite Endpoints (Alias)

### GET /favorites
Get all favorites (alias for /users/favorites).

---

### POST /favorites
Add favorite (alias for /users/favorites).

---

### DELETE /favorites/<course_id>
Remove favorite (alias).

---

## Health Check

### GET /health
Check API health status.

**Response (200):**
```json
{
  "status": "healthy",
  "message": "CareerWays API is running"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "message": "Missing required fields"
}
```

### 401 Unauthorized
```json
{
  "message": "Invalid email or password"
}
```

### 403 Forbidden
```json
{
  "message": "Forbidden"
}
```

### 404 Not Found
```json
{
  "message": "Resource not found"
}
```

### 409 Conflict
```json
{
  "message": "Email already registered"
}
```

### 500 Internal Server Error
```json
{
  "message": "Error: {error details}"
}
```

---

## Authentication

All endpoints require Bearer token authentication except:
- POST /auth/signup
- POST /auth/login
- POST /assessments/analyze (for guests)
- GET /recommendations/* (public access)
- GET /health

Include token in Authorization header:
```
Authorization: Bearer <token>
```

---

## Rate Limiting

Currently no rate limiting. Implement for production.

---

## Pagination

Currently no pagination. Add for large result sets.

---

## Versioning

Current API Version: v1
Future: http://localhost:5000/api/v1/

---

**Last Updated**: 2026-04-24
