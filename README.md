# School Timetable Web App

## Overview
This application allows users to search for elementary, middle, or high schools in South Korea and view their daily timetables using the NEIS (National Education Information System) open API.

## Project Structure
```
school-timetable-app/
├── backend/      # Flask API and backend logic
│   ├── app.py    # Main Flask application
│   ├── .env      # Stores the NEIS API key (must be created by the user)
│   └── ...       # Other backend files (e.g., venv)
├── frontend/     # React User Interface
│   ├── public/   # Static assets for React app
│   ├── src/      # React components and logic
│   │   ├── components/ # Reusable React components
│   │   ├── App.js      # Main React app component
│   │   └── ...
│   ├── package.json # Frontend dependencies
│   └── ...
└── README.md     # This file
```

## Prerequisites
- Python 3.7+
- Node.js (v16+ recommended) and npm (or yarn)

## Setup and Running the Application

### Backend (Flask)
1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
2.  **Create and populate `.env` file:**
    Create a file named `.env` inside the `backend` directory and add your NEIS API key:
    ```
    neis_api_key=YOUR_API_KEY_HERE
    ```
    Replace `YOUR_API_KEY_HERE` with your actual NEIS API key.
3.  **Install Python dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    # Create and activate a virtual environment (optional but recommended)
    # python -m venv venv
    # source venv/bin/activate  # On Windows: venv\Scripts\activate

    pip install Flask python-dotenv requests flask-cors
    ```
    (Alternatively, if a `requirements.txt` was provided: `pip install -r requirements.txt`)

4.  **Run the backend server:**
    ```bash
    python app.py
    ```
    The backend server will start on `http://localhost:5000`.

### Frontend (React)
1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```
    (Or if you use yarn: `yarn install`)

3.  **Run the frontend development server:**
    ```bash
    npm start
    ```
    (Or if you use yarn: `yarn start`)
    The frontend development server will start on `http://localhost:3000` and will make API calls to the backend at `http://localhost:5000`. Ensure the backend server is running.

## How to Use
1.  Open your browser and go to `http://localhost:3000`.
2.  In the "학교 검색" (School Search) section, type the name of the school you want to find and click "검색" (Search).
3.  A list of matching schools will appear. Click on the desired school from the list.
4.  The selected school's name will appear, and input fields for "학년" (Grade), "반" (Class), and "날짜" (Date YYYYMMDD) will be available.
5.  Fill in the grade, class number, and date (e.g., 20231128).
6.  Click "시간표 조회" (Get Timetable).
7.  The timetable for the selected school, grade, class, and date will be displayed.
8.  To search for another school, click "학교 선택 해제" (Clear School Selection).

## Important Note on Integration
Due to environmental constraints encountered during development (specifically regarding the persistence and accessibility of build artifacts across different execution contexts), the Flask application in the `backend` is **not** configured to serve the static React build files directly in this version.

Therefore, to run and use the application, **both the Flask backend development server and the React frontend development server must be running concurrently** as described in the setup instructions. The React frontend (on `http://localhost:3000`) is configured to make API calls to the Flask backend (on `http://localhost:5000`).
