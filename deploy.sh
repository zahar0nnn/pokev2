#!/bin/bash

# Deployment script for Ubuntu VPS
echo "🚀 Deploying Phygitals Scraper to Ubuntu VPS..."

# Create deployment directory
mkdir -p deployment
cd deployment

# Copy all necessary files
echo "📦 Copying project files..."
cp ../*.py .
cp ../*.txt .
cp ../*.yaml .
cp ../*.sql .
cp -r ../templates .
cp -r ../static .

# Create a simple run script
cat > run.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Phygitals Scraper..."

# Activate virtual environment
source venv/bin/activate

# Start the web server in background
python3 app.py &
WEB_PID=$!

# Start the scraper
python3 scraper.py

# Cleanup on exit
trap "kill $WEB_PID" EXIT
EOF

chmod +x run.sh

# Create a simple stop script
cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Phygitals Scraper..."
pkill -f "python3 app.py"
pkill -f "python3 scraper.py"
echo "✅ Stopped"
EOF

chmod +x stop.sh

echo "✅ Deployment package created in 'deployment' folder"
echo "📦 Upload this folder to your VPS and run:"
echo "   cd deployment"
echo "   chmod +x setup_ubuntu.sh"
echo "   ./setup_ubuntu.sh"
echo "   ./run.sh"
