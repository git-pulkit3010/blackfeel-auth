# BlackFeel Auth Project Setup Guide

This guide is designed for macOS users to set up and run the BlackFeel Auth project from scratch.

## 1. Prerequisites (Install these first)

Open your **Terminal** app (Command + Space, type "Terminal") and run the following commands one by one.

### Step 1: Install Homebrew (The Mac Package Manager)
Copy and paste this command into Terminal and press Enter. Follow the on-screen instructions (you might need to enter your Mac password).
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install Required Tools
Once Homebrew is installed, run this command to install Python, Node.js, and PostgreSQL:
```bash
brew install python node postgresql git
```

### Step 3: Start the Database Service
Start the PostgreSQL database service so it runs in the background:
```bash
brew services start postgresql
```

---

## 2. Project Setup

### Step 1: Download the Project
(If you haven't already cloned the repository)
Navigate to where you want the project folder to be (e.g., Desktop):
```bash
cd ~/Desktop
git clone <YOUR_REPO_URL_HERE>
cd blackfeel-auth
```
*(Replace `<YOUR_REPO_URL_HERE>` with the actual Git link if you have it, or just navigate to the folder if you downloaded it manually).*

### Step 2: Setup the Database
We need to create the specific user and database that the application expects. Copy and paste this **entire block** into Terminal:

```bash
psql postgres -c "CREATE USER blackfeel_auth_admin WITH PASSWORD 'pulkit3010';"
psql postgres -c "CREATE DATABASE signin_db OWNER blackfeel_auth_admin;"
psql postgres -c "ALTER USER blackfeel_auth_admin CREATEDB;"
```

---

## 3. Backend Setup (The Server)

Open a **new** Terminal window (Command + T) or tab for the backend.

### Step 1: Go to the backend folder
```bash
cd backend
```

### Step 2: Set up Python Environment
Create a virtual environment (a safe space for dependencies):
```bash
python3 -m venv venv
source venv/bin/activate
```
*(You should see `(venv)` appear at the start of your command line).*

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create the configuration file.
1. Run: `nano .env`
2. Copy and paste the text below into the window:

```ini
# Database
SQLALCHEMY_DATABASE_URL=postgresql://blackfeel_auth_admin:pulkit3010@localhost/signin_db

# Security (Change these for production!)
SECRET_KEY=change_this_to_a_secure_random_string_for_access_token
REFRESH_SECRET_KEY=change_this_to_a_secure_random_string_for_refresh_token
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Resend)
RESEND_API_KEY=re_123456789  # Replace with your actual Resend API Key
RESEND_FROM_EMAIL=noreply@yourdomain.com

# WhatsApp (Optional - Required for WhatsApp features)
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# General
BASE_URL=http://localhost:3000
```
3. Press `Ctrl + O` then `Enter` to save.
4. Press `Ctrl + X` to exit.

### Step 5: Run the Backend
```bash
uvicorn app.main:app --reload
```
You should see: `Application startup complete`. Keep this terminal window **OPEN**.

---

## 4. Frontend Setup (The User Interface)

Open a **new** Terminal window (Command + T) for the frontend.

### Step 1: Go to the frontend folder
Navigate to the project folder first, then into frontend:
```bash
cd ~/Desktop/blackfeel-auth/frontend
```
*(Adjust the path if you saved the project somewhere else).*

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Configure Environment Variables
1. Run: `nano .env.local`
2. Copy and paste the text below:

```ini
NEXT_PUBLIC_API_URL=http://localhost:8000
```
3. Press `Ctrl + O` then `Enter` to save.
4. Press `Ctrl + X` to exit.

### Step 4: Run the Frontend
```bash
npm run dev
```
You should see: `Ready in [...]`. Keep this terminal window **OPEN**.

---

## 5. How to Use

1.  Open your browser (Chrome/Safari) and go to: `http://localhost:3000`
2.  You should see the Sign In / Sign Up page.

### Optional: Ngrok (For External Access / Webhooks)
If you need to test features like WhatsApp Webhooks (which require a public URL), you will need `ngrok`.

1.  **Install:** `brew install ngrok/ngrok/ngrok`
2.  **Run:** Open a new terminal and run `ngrok http 8000`
3.  Copy the `https://....ngrok-free.app` URL and update your `BASE_URL` in `backend/.env` with it.
