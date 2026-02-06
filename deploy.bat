@echo off
echo ==========================================
echo      GITHUB DEPLOYMENT ASSISTANT
echo ==========================================

echo [1/5] Initializing Git Repository...
git init
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/
    pause
    exit /b
)

echo.
echo [2/5] Adding files...
git add .

echo.
echo [3/5] Committing files...
git commit -m "Initial commit: Lead Scraper Pro (v1.0)"

echo.
echo ==========================================
echo [ACTION REQUIRED]
echo Please create a NEW repository on GitHub.
echo Copy the HTTPS URL (e.g., https://github.com/YourUser/lead-scraper.git)
echo ==========================================
set /p REPO_URL="Paste your GitHub Repository URL here: "

echo.
echo [4/5] Linking remote repository...
git branch -M main
git remote add origin %REPO_URL%

echo.
echo [5/5] Pushing to GitHub...
git push -u origin main

echo.
echo ==========================================
echo DONE! Check your GitHub repository.
echo ==========================================
pause
