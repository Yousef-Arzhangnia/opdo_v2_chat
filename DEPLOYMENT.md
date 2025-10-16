# Deployment Guide

Quick guide to deploy the Optical Design Chat API to Render.com.

## Prerequisites

- Git repository (GitHub, GitLab, or Bitbucket)
- Anthropic API key from https://console.anthropic.com/settings/keys
- Render.com account (free)

## Step-by-Step Deployment

### 1. Push Code to Git Repository

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub/GitLab/Email

### 3. Connect Repository

1. From Render dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect account"** for GitHub/GitLab
3. Authorize Render to access your repositories
4. Select your `opdo_v2_chat` repository

### 4. Configure Service

Render will auto-detect the `render.yaml` file, but verify these settings:

- **Name**: `optical-design-api` (or your preferred name)
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Plan**: Free

### 5. Set Environment Variables

In the Render dashboard:

1. Go to **"Environment"** tab
2. Add environment variable:
   - **Key**: `ANTHROPIC_API_KEY`
   - **Value**: Your Anthropic API key (from console.anthropic.com)
3. (Optional) Add CORS configuration:
   - **Key**: `ALLOWED_ORIGINS`
   - **Value**: Your frontend URL(s), comma-separated
   - Example: `https://myapp.com,https://www.myapp.com`
   - Leave blank or use `*` to allow all origins

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying
3. Wait 2-3 minutes for initial deployment
4. Your API will be live at: `https://your-service-name.onrender.com`

### 7. Test Deployment

Test the health check endpoint:

```bash
curl https://your-service-name.onrender.com/
```

Expected response:
```json
{
  "status": "ok",
  "message": "Optical Design Chat API is running"
}
```

Test the design endpoint:

```bash
curl -X POST https://your-service-name.onrender.com/api/design \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Design a simple lens",
    "system_message": null,
    "previous_design": null,
    "added_data": null
  }'
```

### 8. Update Your Frontend

Update your frontend code to use the deployed URL:

```typescript
// Before (local development)
const API_URL = 'http://localhost:8000';

// After (production)
const API_URL = 'https://your-service-name.onrender.com';
```

Or use environment variables:

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

## Important Notes

### Free Tier Limitations

- **Cold Starts**: Service spins down after 15 minutes of inactivity
- **First Request Delay**: Takes 30-60 seconds to wake up after inactivity
- **Monthly Limit**: 750 hours/month (usually sufficient for low-traffic apps)

### Handling Cold Starts

**Option 1: Show Loading State**
```typescript
async function callAPI() {
  setLoading(true);
  setMessage("Waking up server (first request may take 30-60s)...");

  const response = await fetch(API_URL + '/api/design', {...});

  setLoading(false);
  return response;
}
```

**Option 2: Keep-Alive Service**
Use a cron job service to ping your API every 10 minutes:
- https://cron-job.org (free)
- Create a job that hits `https://your-service-name.onrender.com/` every 10 minutes

**Option 3: Upgrade to Paid Tier**
- $7/month for always-on service
- No cold starts
- Better for production apps

### Monitoring

View logs in Render dashboard:
1. Go to your service
2. Click **"Logs"** tab
3. See real-time logs of all requests and errors

### Updating Your Deployment

After making code changes:

```bash
git add .
git commit -m "Update API"
git push origin main
```

Render will automatically detect the push and redeploy (takes 1-2 minutes).

## Alternative Platforms

### Railway.app
- Similar free tier
- Easier setup but less generous free tier
- Visit https://railway.app

### Fly.io
- Better performance
- More complex setup
- Visit https://fly.io

### Vercel (Serverless)
- Need to modify code for serverless deployment
- Better for static sites with API routes
- Visit https://vercel.com

## Troubleshooting

### Build Failed
- Check `requirements.txt` has all dependencies
- Verify Python version in `runtime.txt` is supported (3.11.0)
- Check Render logs for specific error

### API Returns 500 Error
- Check environment variables are set correctly
- Verify `ANTHROPIC_API_KEY` is valid
- Check Render logs for error details

### CORS Errors
- Set `ALLOWED_ORIGINS` environment variable
- Include your frontend URL (with https://)
- Remove trailing slashes from URLs

### Cold Start Too Slow
- Upgrade to paid tier ($7/month)
- Use keep-alive service
- Show loading message to users

## Security Checklist

- ✅ `ANTHROPIC_API_KEY` stored in environment variables (not in code)
- ✅ CORS configured to only allow your frontend domain
- ✅ HTTPS enabled by default on Render
- ✅ `.env` file in `.gitignore` (never commit secrets)

## Cost Estimate

**Free Tier** (Render + Anthropic):
- Render: Free (750 hours/month)
- Anthropic API: Pay per use
  - ~$0.003 per request (Claude 3.5 Sonnet)
  - 1000 requests ≈ $3

**Paid Tier**:
- Render: $7/month (always-on)
- Anthropic API: Same pay-per-use pricing

## Support

- Render docs: https://render.com/docs
- Anthropic docs: https://docs.anthropic.com
- File issues: Create GitHub issue in your repository
