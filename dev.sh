#!/bin/bash

# Start the backend server
cd backend
python3 app.py &
BACKEND_PID=$!

# Start the frontend development server
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Handle cleanup on script termination
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

# Wait for both processes
wait
