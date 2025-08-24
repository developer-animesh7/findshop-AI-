# 🚀 One-Click Project Launcher

This directory contains scripts to run the entire AI Shopping Helper project with a single command. Choose the method that works best for your system.

## 🎯 Quick Start Options

### Option 1: Python Script (Recommended)
```bash
python run_project.py
```

### Option 2: Shell Script (macOS/Linux)
```bash
./run.sh
```

### Option 3: Batch File (Windows)
Double-click `run.bat` or run from command prompt:
```cmd
run.bat
```

## ✨ What These Scripts Do

The launcher automatically handles:

1. **✅ Environment Setup**
   - Checks Python version compatibility (3.8+)
   - Creates virtual environment if needed
   - Activates the virtual environment

2. **📦 Dependency Management**
   - Upgrades pip to latest version
   - Installs all required packages from requirements.txt
   - Handles FastAPI, SQLite, and all project dependencies

3. **🗄️ Database Initialization**
   - Creates SQLite database file
   - Sets up all required tables
   - Populates default product categories:
     - Headphones & Earphones
     - Smartphones
     - Laptops & Computers
     - Trimmers & Grooming
     - Kitchen Appliances
     - Clothing & Fashion
     - General Products

4. **🌐 Server Startup**
   - Starts FastAPI server on `http://localhost:8000`
   - Enables hot-reload for development
   - Monitors server health

5. **🎯 Browser Launch**
   - Automatically opens your default browser
   - Navigates to the application homepage
   - Ready to use immediately!

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512MB RAM minimum
- **Storage**: 100MB free space for dependencies

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python -c "from backend.database.db_connection import init_db; init_db()"

# 5. Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Application URLs

Once running, access these URLs:

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:8000 | Web interface for product analysis |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Server status endpoint |

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal to gracefully stop the server.

## 🐛 Troubleshooting

### Common Issues:

**Port 8000 already in use:**
```bash
# Kill any existing processes on port 8000
pkill -f uvicorn
# Or on Windows:
taskkill /f /im python.exe
```

**Permission denied on scripts:**
```bash
chmod +x run.sh
```

**Python not found:**
- Make sure Python 3.8+ is installed
- Try `python3` instead of `python`
- On Windows, ensure Python is in PATH

**Module import errors:**
- Delete `venv` folder and run the script again
- This will create a fresh virtual environment

## 📚 Features Overview

The AI Shopping Helper provides:

- **🤖 AI-Powered Analysis**: Smart product quality scoring
- **💰 Price Comparison**: Multi-platform price checking
- **🔍 Alternative Finder**: Discover better value products
- **📊 Category Scorecards**: Specialized analysis per product type
- **🖼️ Image Analysis**: Product analysis from images
- **📱 Web Interface**: User-friendly web application
- **🔌 REST API**: Programmatic access to all features

## 📞 Support

If you encounter any issues:

1. Check the terminal output for error messages
2. Ensure all system requirements are met
3. Try the manual setup process
4. Delete the `venv` folder and run the script again

---

**Happy Shopping! 🛒✨**
