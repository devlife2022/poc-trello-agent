# Deployment Guide

This guide will walk you through deploying the Trello AI Assistant to **GitHub Pages** (frontend) and **Render** (backend services).

## Prerequisites

1. GitHub account
2. Render account (free tier) - [Sign up at render.com](https://render.com)
3. API Keys:
   - Anthropic API Key
   - Trello API Key and Token
   - Trello Board ID

---

## 📦 Part 1: Deploy Backend to Render

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Authorize Render to access your repository

### Step 2: Deploy MCP Server

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `poc-trello-agent`
3. Configure the service:
   - **Name**: `trello-ai-mcp`
   - **Region**: Oregon (Free)
   - **Branch**: `main`
   - **Root Directory**: `mcp-server`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Plan**: Free

4. Add Environment Variables:
   - `TRELLO_API_KEY` = (your Trello API key)
   - `TRELLO_API_TOKEN` = (your Trello token)
   - `TRELLO_DEFAULT_BOARD_ID` = (your board ID)
   - `PYTHON_VERSION` = `3.11.0`
   - `PORT` = `8080`

5. Click **"Create Web Service"**
6. Wait for deployment to complete (~5 minutes)
7. **Copy the service URL** (e.g., `https://trello-ai-mcp.onrender.com`)

### Step 3: Deploy FastAPI Backend

1. Click **"New +"** → **"Web Service"** again
2. Select the same repository
3. Configure:
   - **Name**: `trello-ai-backend`
   - **Region**: Oregon (Free)
   - **Branch**: `main`
   - **Root Directory**: `api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. Add Environment Variables:
   - `ANTHROPIC_API_KEY` = (your Anthropic API key)
   - `TRELLO_API_KEY` = (your Trello API key)
   - `TRELLO_API_TOKEN` = (your Trello token)
   - `TRELLO_DEFAULT_BOARD_ID` = (your board ID)
   - `MCP_SERVER_URL` = (URL from Step 2, e.g., `https://trello-ai-mcp.onrender.com`)
   - `CORS_ORIGINS` = `https://YOUR_GITHUB_USERNAME.github.io` (replace with your actual username)
   - `PYTHON_VERSION` = `3.11.0`

5. Click **"Create Web Service"**
6. Wait for deployment (~5 minutes)
7. **Copy the service URL** (e.g., `https://trello-ai-backend.onrender.com`)
8. Test the health endpoint: Visit `https://trello-ai-backend.onrender.com/api/health`

---

## 🌐 Part 2: Deploy Frontend to GitHub Pages

### Step 1: Update Frontend Environment Variable

1. In your local project, create `frontend/.env.production`:
   ```bash
   VITE_API_BASE_URL=https://trello-ai-backend.onrender.com
   ```
   (Replace with your actual Render backend URL from Part 1, Step 3)

2. Update `frontend/vite.config.ts` to set the base path:
   ```typescript
   base: '/poc-trello-agent/'
   ```
   (Use your repository name)

### Step 2: Enable GitHub Pages

1. Go to your GitHub repository
2. Click **Settings** → **Pages**
3. Under "Build and deployment":
   - **Source**: GitHub Actions
4. Click **Save**

### Step 3: Trigger Deployment

1. Commit and push all changes:
   ```bash
   git add .
   git commit -m "Add deployment configurations"
   git push origin main
   ```

2. Go to **Actions** tab in GitHub
3. Watch the "Deploy Frontend to GitHub Pages" workflow run
4. Once complete, your site will be available at:
   `https://YOUR_GITHUB_USERNAME.github.io/poc-trello-agent/`

### Step 4: Update Backend CORS (if needed)

If you used a placeholder in Step 1, update the `CORS_ORIGINS` environment variable in Render:
1. Go to Render Dashboard → `trello-ai-backend` service
2. Click **Environment** tab
3. Update `CORS_ORIGINS` to your actual GitHub Pages URL
4. Service will auto-redeploy

---

## 🔧 Configuration Summary

### Local Development URLs:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- MCP Server: Runs as subprocess

### Production URLs:
- Frontend: `https://YOUR_GITHUB_USERNAME.github.io/poc-trello-agent/`
- Backend: `https://trello-ai-backend.onrender.com`
- MCP Server: `https://trello-ai-mcp.onrender.com`

---

## 🧪 Testing the Deployment

1. Visit your GitHub Pages URL
2. You should see the chat interface
3. Type a message (e.g., "Show me all open tickets")
4. The app should communicate with the backend on Render

If you see CORS errors, double-check:
- `CORS_ORIGINS` in Render backend matches your GitHub Pages URL exactly
- Frontend `.env.production` has correct backend URL

---

## 💰 Cost Breakdown

| Service | Provider | Cost |
|---------|----------|------|
| Frontend Hosting | GitHub Pages | **FREE** |
| Backend API | Render (Free Tier) | **FREE** (750 hrs/month) |
| MCP Server | Render (Free Tier) | **FREE** (750 hrs/month) |
| **TOTAL** | | **$0/month** |

**Note**: Render free tier services sleep after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up.

---

## 🚀 Updating Your Deployment

### Frontend Changes:
```bash
git add frontend/
git commit -m "Update frontend"
git push origin main
```
GitHub Actions will auto-deploy.

### Backend Changes:
```bash
git add api/
git commit -m "Update backend"
git push origin main
```
Render will auto-deploy.

### MCP Server Changes:
```bash
git add mcp-server/
git commit -m "Update MCP server"
git push origin main
```
Render will auto-deploy.

---

## 🐛 Troubleshooting

### Frontend shows "Failed to fetch"
- Check that `VITE_API_BASE_URL` in frontend `.env.production` is correct
- Check browser console for CORS errors
- Verify backend is running: Visit backend URL `/api/health`

### Backend shows CORS errors
- Verify `CORS_ORIGINS` in Render includes your GitHub Pages URL
- Make sure there are no trailing slashes in URLs

### Backend won't start
- Check Render logs for errors
- Verify all environment variables are set
- Check that `MCP_SERVER_URL` is correct

### MCP Server connection fails
- Check MCP server logs in Render
- Verify Trello API credentials are correct
- Test Trello API directly

---

## 📚 Additional Resources

- [Render Documentation](https://render.com/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 🔐 Security Notes

- Never commit `.env` files with real API keys
- Store all secrets in Render environment variables
- Rotate API keys periodically
- Use GitHub Secrets for sensitive workflow variables (if needed)

---

## ✅ Checklist

Before deploying:
- [ ] Obtained Anthropic API key
- [ ] Obtained Trello API key and token
- [ ] Created Trello board and got board ID
- [ ] Created Render account
- [ ] Enabled GitHub Pages in repository settings
- [ ] Updated `CORS_ORIGINS` with actual GitHub Pages URL
- [ ] Updated frontend `.env.production` with actual backend URL
- [ ] Updated `vite.config.ts` with correct base path
- [ ] Committed all changes
- [ ] Tested deployment

Good luck with your deployment! 🎉
