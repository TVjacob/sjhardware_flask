# !/bin/bash
# render-build.sh — Render uses this instead of guessing

echo "Installing Python dependencies..."
pip install -r requirements.txt gunicorn

echo "Building Vue frontend..."
cd sjhardware-frontend
npm install
npm run build
cd ..

echo "Copying Vue build to Flask static folder..."
rm -rf app/static/*
cp -r sjhardware-frontend/dist/* app/static/

echo "Build complete! SJ Hardware ready for launch."