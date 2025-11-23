@echo off
echo Pushing code to GitHub...
echo.

REM Initialize git if not already done
if not exist ".git" (
    echo Initializing git repository...
    git init
)

REM Add remote (remove if exists, then add)
git remote remove origin 2>nul
git remote add origin https://github.com/aaliyanahmed1/AI_Image_detector.git

REM Add all files
echo Adding all files...
git add .

REM Commit
echo Committing changes...
git commit -m "Initial commit: Image Authenticity Detector with Svelte frontend and FastAPI backend"

REM Set main branch and push
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo Done! Check your repository: https://github.com/aaliyanahmed1/AI_Image_detector
pause

