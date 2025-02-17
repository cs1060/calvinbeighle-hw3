#!/bin/bash

# Create necessary directories
mkdir -p backend/uploads backend/organized

# Install backend dependencies
cd backend
python -m pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Create .env files
echo "OPENAI_API_KEY=your_api_key_here" > ../backend/.env
echo "VITE_API_URL=http://localhost:5000/api" > .env.local

echo "Setup complete! To run the application:"
echo "1. Start backend: cd backend && python app.py"
echo "2. Start frontend: cd frontend && npm run dev" 