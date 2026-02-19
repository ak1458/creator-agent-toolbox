# Deploy to Render + Vercel (Production)

## Step 1: Prepare Backend for Render

### 1.1 Update `backend/.env` (don't commit this)

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=gsk_your_groq_key_here
OPENAI_BASE_URL=https://api.groq.com/openai/v1
DATABASE_URL=sqlite:///data/app.db
CHECKPOINT_DB_URL=sqlite:///data/checkpoints.db
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=false
SECRET_KEY=your-random-secret-key-here
```

### 1.2 Verify Files Exist

- `backend/render.yaml` ✓
- `backend/requirements.txt` ✓
- `backend/Dockerfile` ✓

## Step 2: Push to GitHub

```bash
cd creator-agent-toolbox
git init
git add .
git commit -m "Ready for Render deployment"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/creator-agent-toolbox.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy Backend to Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Sign up with GitHub
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repo
5. Configure:
   - **Name**: `creator-agent-api`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

6. Add Environment Variables (in Render dashboard):

   | Key | Value |
   |-----|-------|
   | `OPENAI_API_KEY` | `gsk_your_groq_key_here` |
   | `OPENAI_BASE_URL` | `https://api.groq.com/openai/v1` |
   | `LLM_PROVIDER` | `openai` |
   | `ALLOWED_ORIGINS` | `http://localhost:5173` |
   | `DEBUG` | `false` |
   | `DATABASE_URL` | `sqlite:///data/app.db` |
   | `CHECKPOINT_DB_URL` | `sqlite:///data/checkpoints.db` |

7. Add Disk (for SQLite persistence):
   - **Name**: `data`
   - **Mount Path**: `/opt/render/project/src/data`
   - **Size**: 1 GB

8. Click **"Create Web Service"**

9. Wait 5 minutes for build

10. Test: `curl https://creator-agent-api.onrender.com/api/v1/health`

## Step 4: Deploy Frontend to Vercel

### 4.1 Update Frontend API URL

Edit `frontend/.env.production`:

```bash
VITE_API_BASE_URL=https://creator-agent-api.onrender.com
```

### 4.2 Push Frontend

```bash
git add frontend/.env.production
git commit -m "Update API URL for production"
git push
```

### 4.3 Deploy to Vercel

```bash
npm install -g vercel
cd frontend
vercel --prod
```

Follow prompts:

- Set up and deploy "frontend"? **Y**
- Which scope? [Your username]
- Link to existing project? **n**
- Project name? **creator-agent-dashboard**

Get URL: `https://creator-agent-dashboard.vercel.app`

## Step 5: Connect Backend ↔ Frontend

1. Copy your Vercel URL
2. Go to Render Dashboard → Your Service → Environment
3. Update `ALLOWED_ORIGINS`:

   ```
   https://creator-agent-dashboard.vercel.app,http://localhost:5173
   ```

4. Save (auto-redeploys)

## Step 6: Test Full Flow

```bash
# Create workflow via deployed API
curl -X POST https://creator-agent-api.onrender.com/api/v1/workflows/start \
  -H "Content-Type: application/json" \
  -d '{"topic": "Deployment Test", "platforms": ["youtube"]}'

# Should return workflow with scripts (using Groq)
```

## Your Live URLs

```
Frontend: https://creator-agent-dashboard.vercel.app
Backend:  https://creator-agent-api.onrender.com
API Docs: https://creator-agent-api.onrender.com/docs
```

## Troubleshooting

### Render Build Fails

- Check build logs in Render dashboard
- Ensure `requirements.txt` has all dependencies
- Try `poetry export -f requirements.txt --output requirements.txt`

### CORS Errors

- Verify `ALLOWED_ORIGINS` includes your Vercel URL
- Check Render service redeployed after env update

### Groq Rate Limit

- Free tier: 20 requests/minute
- Monitor at <https://console.groq.com>

### Render Sleeping

- Free tier sleeps after 15 mins idle
- First request after sleep takes 30-60s
- Use UptimeRobot (free) to ping every 10 mins

## Cost

- **Groq**: Free (20 req/min)
- **Render**: Free (sleeps when idle)
- **Vercel**: Free (unlimited)
- **Total**: $0/month
