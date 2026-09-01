# GitHub Setup

## 1. Create repository
Create a new GitHub repository, for example:

`intelligent-software-defect-tracking-system`

## 2. Upload
Upload all project files from this folder.

## 3. Commit
```bash
git init
git add .
git commit -m "Initial intelligent defect tracking dashboard"
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

## 4. Streamlit deployment
Use the GitHub repository in Streamlit Community Cloud and select:

`app.py`

The deployment automatically reads `requirements.txt`.

## 5. Important
Do not commit private API keys or `.streamlit/secrets.toml`.
