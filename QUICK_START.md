# Quick Start - Free Deployment on Render + GitHub Pages

Follow these steps to deploy your Trello AI Assistant for **FREE** using GitHub and Render.

## ⏱️ Time Required: ~20 minutes

---

## Step 1: Get Your API Keys (5 min)

### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy and save it

### Trello API Credentials
1. Go to [trello.com/power-ups/admin](https://trello.com/power-ups/admin)
2. Click "New" to create a new Power-Up
3. Copy your **API Key**
4. Click "Token" link to generate a token
5. Authorize and copy your **Token**

### Trello Board ID
1. Open your Trello board
2. Add `.json` to the end of the URL (e.g., `trello.com/b/abc123.json`)
3. Find the `"id"` field in the JSON
4. Copy the board ID

---

## Step 2: Deploy to Render (10 min)

### A. Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Get Started"
3. Sign up with GitHub
4. Authorize Render to access your repositories

### B. Deploy MCP Server First
1. Click **"New +"** → **"Web Service"**
2. Select your `poc-trello-agent` repository
3. Fill in:
   - **Name**: `trello-ai-mcp`
   - **Region**: Oregon (Free)
   - **Root Directory**: `mcp-server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Instance Type**: Free
4. Click "Advanced" and add environment variables:
   ```
   TRELLO_API_KEY = (paste your Trello API key)
   TRELLO_API_TOKEN = (paste your Trello token)
   TRELLO_DEFAULT_BOARD_ID = (paste your board ID)
   PYTHON_VERSION = 3.11.0
   PORT = 8080
   ```
5. Click **"Create Web Service"**
6. ⏳ Wait 3-5 minutes for deployment
7. **✅ Copy the URL** (looks like: `https://trello-ai-mcp-xyz.onrender.com`)

### C. Deploy Backend API
1. Click **"New +"** → **"Web Service"** again
2. Select your `poc-trello-agent` repository again
3. Fill in:
   - **Name**: `trello-ai-backend`
   - **Region**: Oregon (Free)
   - **Root Directory**: `api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free
4. Click "Advanced" and add environment variables:
   ```
   ANTHROPIC_API_KEY = (paste your Anthropic API key)
   TRELLO_API_KEY = (paste your Trello API key)
   TRELLO_API_TOKEN = (paste your Trello token)
   TRELLO_DEFAULT_BOARD_ID = (paste your board ID)
   MCP_SERVER_URL = (paste MCP server URL from step B.7)
   CORS_ORIGINS = https://YOUR_GITHUB_USERNAME.github.io
   PYTHON_VERSION = 3.11.0
   ```
   **⚠️ Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username!**

5. Click **"Create Web Service"**
6. ⏳ Wait 3-5 minutes for deployment
7. **✅ Copy the URL** (looks like: `https://trello-ai-backend-xyz.onrender.com`)
8. Test it: Visit `https://trello-ai-backend-xyz.onrender.com/api/health`
   - You should see JSON with `"status": "healthy"`

---

## Step 3: Update Frontend Config (2 min)

1. In your local project, edit `frontend/.env.production`:
   ```bash
   VITE_API_BASE_URL=https://trello-ai-backend-xyz.onrender.com
   ```
   (Replace with your actual backend URL from Step 2.C.7)

2. Commit and push:
   ```bash
   git add frontend/.env.production
   git commit -m "Configure production backend URL"
   git push origin main
   ```

---

## Step 4: Deploy Frontend to GitHub Pages (3 min)

1. Go to your GitHub repository on github.com
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
5. Click **Save**

6. Go to the **Actions** tab
7. You should see "Deploy Frontend to GitHub Pages" workflow running
8. ⏳ Wait 2-3 minutes
9. Once complete (green checkmark ✅), your app is live at:
   ```
   https://YOUR_GITHUB_USERNAME.github.io/poc-trello-agent/
   ```

---

## Step 5: Test Your Deployment! 🎉

1. Visit your GitHub Pages URL
2. You should see the chat interface
3. Try asking: **"Show me all open tickets"**
4. The AI should respond!

---

## 🐛 Troubleshooting

### "Failed to fetch" error
- Check that `VITE_API_BASE_URL` in `frontend/.env.production` matches your Render backend URL
- Make sure you committed and pushed the changes
- Try re-running the GitHub Actions workflow

### CORS error in browser console
- Go to Render → `trello-ai-backend` → Environment
- Verify `CORS_ORIGINS` exactly matches: `https://YOUR_GITHUB_USERNAME.github.io`
- No trailing slashes!
- Save and wait for auto-redeploy

### Backend health check fails
- Check Render logs: Dashboard → `trello-ai-backend` → Logs
- Verify all environment variables are set correctly
- Check MCP server is running: Visit MCP server URL

### First request takes 30+ seconds
- This is normal! Render free tier "sleeps" after 15 min of inactivity
- First request "wakes up" the service (~30 sec)
- Subsequent requests are fast

---

## 💰 Cost: $0/month

- GitHub Pages: FREE
- Render (2 services): FREE (750 hours/month each)
- Total: **Completely FREE!**

---

## 🔄 Updating Your App

### Update Frontend
```bash
git add frontend/
git commit -m "Update UI"
git push origin main
```
GitHub Actions auto-deploys in ~3 minutes.

### Update Backend
```bash
git add api/
git commit -m "Update API"
git push origin main
```
Render auto-deploys in ~5 minutes.

---

## 📚 Next Steps

- [Read full deployment guide](./DEPLOYMENT.md) for advanced configuration
- Set up custom domain (optional)
- Add monitoring and analytics
- Customize the system prompt

---

## ✅ Deployment Checklist

- [ ] Got Anthropic API key
- [ ] Got Trello API key & token
- [ ] Got Trello board ID
- [ ] Created Render account
- [ ] Deployed MCP server to Render
- [ ] Deployed backend to Render
- [ ] Updated frontend `.env.production`
- [ ] Enabled GitHub Pages
- [ ] Tested the live app

**All done? Congratulations! 🎉 Your Trello AI Assistant is now live!**
