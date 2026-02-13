# BlackFeel Sign-In Security Application

A secure authentication system with email verification, rate limiting, account lockout protection, and social login capabilities.

## Features

- **Secure Authentication**: Email/password sign-in with bcrypt hashing
- **Email Verification**: Secure email verification system
- **Rate Limiting**: Protection against brute force attacks
- **Account Lockout**: Temporary lockout after multiple failed attempts
- **Social Login**: Google OAuth integration with PKCE
- **CSRF Protection**: Secure token handling
- **Phone Number Validation**: International phone number support

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT tokens, OAuth2 with PKCE
- **Rate Limiting**: SlowAPI

### Frontend
- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Runtime**: Node.js

## Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL
- Bun (optional, for backend runtime)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd blackfeel-signin-security
```

### 2. Backend Setup

#### Navigate to the backend directory:
```bash
cd backend
```

#### Install Python Dependencies:
```bash
pip install -r requirements.txt
```

#### Set up Virtual Environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Environment Variables:
Create a `.env` file in the backend directory with the following variables:

```env
DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your-super-secret-key-here
REFRESH_SECRET_KEY=your-refresh-token-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
MAX_FAILED_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
FRONTEND_URL=http://localhost:3000
VERIFY_TOKEN=your-verify-token
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379/0
```

#### Initialize the Database:
```bash
python reset_db.py
```

#### Run the Backend Server:
```bash
uvicorn app.main:app --reload --port 8000
```

Or using Bun (if configured):
```bash
bun run index.ts
```

The backend will be available at `http://127.0.0.1:8000`.

### 3. Frontend Setup

#### Navigate to the frontend directory:
```bash
cd frontend
```

#### Install Dependencies:
```bash
npm install
# or
yarn install
# or
bun install
```

#### Environment Variables:
Create a `.env.local` file in the frontend directory with the following variables:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
GOOGLE_CLIENT_ID=your-google-client-id
FRONTEND_URL=http://localhost:3000
```

#### Run the Development Server:
```bash
npm run dev
# or
yarn dev
# or
bun run dev
```

The frontend will be available at `http://localhost:3000`.

## Project Structure

```
blackfeel-signin-security/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── reset_db.py
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── next.config.js
└── README.md
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login
- `GET /api/auth/verify-email` - Email verification
- `POST /api/auth/resend-verification` - Resend verification
- `GET /api/auth/callback/google` - Google OAuth callback


## Database Schema

The application uses PostgreSQL with SQLAlchemy ORM. Key tables include:
- `users` - User accounts with authentication info
- `verification_tokens` - Email verification tokens
- `login_attempts` - Failed login attempt tracking
- `oauth_accounts` - Social login associations

## Security Features

1. **Password Security**: BCrypt hashing with configurable parameters
2. **Rate Limiting**: Prevents brute force attacks
3. **Account Lockout**: Temporarily locks accounts after failed attempts
4. **JWT Tokens**: Secure session management
5. **PKCE**: Enhanced OAuth security for public clients
6. **CSRF Protection**: Token-based request validation
7. **Input Validation**: Comprehensive data validation

## Development

### Running Tests
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm run test
```

### Database Migration
For database schema changes, use Alembic:
```bash
# Create migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head
```

### Ngrok Configuration
The application supports tunneling with ngrok for external access during development:
```bash
ngrok http --url=overtense-kimberli-protrusile.ngrok-free.dev 8000
```

## Deployment

### Environment Configuration
For production deployment, ensure the following:
- Use strong, unique values for all secret keys
- Configure HTTPS for both frontend and backend
- Set up proper database connection pooling
- Configure Redis for rate limiting
- Set up proper logging and monitoring

### Production Builds
```bash
# Backend (using uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
npm run start
```

## Troubleshooting

1. **Database Connection Issues**: Verify PostgreSQL is running and credentials are correct
2. **CORS Errors**: Check that frontend URL is included in CORS middleware origins
3. **OAuth Issues**: Ensure redirect URIs match between application and OAuth provider

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.