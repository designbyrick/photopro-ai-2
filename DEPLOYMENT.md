# PhotoPro AI - Deployment Guide

This guide covers the complete deployment process for PhotoPro AI, including backend (Railway) and frontend (Vercel) deployment.

## 🚀 Quick Deployment Checklist

- [ ] Railway backend deployment
- [ ] Vercel frontend deployment  
- [ ] AWS S3 bucket setup
- [ ] Replicate API configuration
- [ ] Domain and SSL setup
- [ ] Environment variables configuration
- [ ] Database migration
- [ ] Health checks and monitoring

## 📋 Prerequisites

### Required Accounts
- [Railway](https://railway.app) account
- [Vercel](https://vercel.com) account
- [AWS](https://aws.amazon.com) account
- [Replicate](https://replicate.com) account

### Required Services
- PostgreSQL database (Railway)
- AWS S3 bucket
- Replicate API access
- Domain name (optional)

## 🔧 Backend Deployment (Railway)

### 1. Connect Repository to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your PhotoPro AI repository
5. Select the `backend` folder as the root directory

### 2. Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# JWT Authentication
SECRET_KEY=your-super-secret-jwt-key-here

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=us-east-1

# Replicate API
REPLICATE_API_TOKEN=your-replicate-api-token

# CORS Origins
CORS_ORIGINS=https://photopro-ai.vercel.app,https://www.photopro-ai.com
```

### 3. Add PostgreSQL Database

1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically set the `DATABASE_URL` environment variable
3. The database will be automatically connected to your backend service

### 4. Deploy Backend

Railway will automatically deploy when you push to the main branch. The deployment process:

1. Installs Python dependencies from `requirements.txt`
2. Runs database migrations automatically
3. Starts the FastAPI application with Gunicorn
4. Exposes the service on a public URL

### 5. Verify Backend Deployment

Check your backend is running:
```bash
curl https://your-railway-url.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🎨 Frontend Deployment (Vercel)

### 1. Connect Repository to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Set the root directory to `frontend`
5. Framework preset: "Create React App"

### 2. Configure Environment Variables

In Vercel dashboard, go to your project → Settings → Environment Variables:

```bash
# Backend API URL
REACT_APP_API_URL=https://your-railway-url.railway.app

# WebSocket URL
REACT_APP_WS_URL=wss://your-railway-url.railway.app

# Build optimization
GENERATE_SOURCEMAP=false
```

### 3. Configure Build Settings

In Vercel project settings:

- **Build Command**: `npm run build`
- **Output Directory**: `build`
- **Install Command**: `npm install`

### 4. Deploy Frontend

Vercel will automatically deploy when you push to the main branch. The deployment process:

1. Installs Node.js dependencies
2. Builds the React application
3. Deploys to Vercel's CDN
4. Provides a public URL

### 5. Verify Frontend Deployment

Visit your Vercel URL and verify:
- [ ] Application loads correctly
- [ ] Login/signup forms work
- [ ] API calls are successful
- [ ] WebSocket connection works

## ☁️ AWS S3 Setup

### 1. Create S3 Bucket

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com)
2. Click "Create bucket"
3. Choose a unique bucket name (e.g., `photopro-ai-images`)
4. Select region (e.g., `us-east-1`)
5. Configure public access settings:
   - Uncheck "Block all public access"
   - Acknowledge the warning

### 2. Configure Bucket Policy

Add this policy to allow public read access to uploaded images:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

### 3. Create IAM User

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam)
2. Create new user: `photopro-ai-s3-user`
3. Attach policy: `AmazonS3FullAccess`
4. Create access keys
5. Add keys to Railway environment variables

## 🤖 Replicate API Setup

### 1. Create Replicate Account

1. Go to [Replicate](https://replicate.com)
2. Sign up for an account
3. Go to Account → API tokens
4. Create a new token

### 2. Configure API Token

Add the token to Railway environment variables:
```bash
REPLICATE_API_TOKEN=r8_your_token_here
```

### 3. Test API Integration

Verify the API works by checking the backend logs for successful connections.

## 🔐 Security Configuration

### 1. JWT Secret Key

Generate a strong secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. CORS Configuration

Ensure CORS is properly configured for your frontend domain:
```python
allow_origins=["https://photopro-ai.vercel.app", "https://www.photopro-ai.com"]
```

### 3. Rate Limiting

The application includes rate limiting (100 requests/minute per IP) to prevent abuse.

## 📊 Monitoring and Health Checks

### 1. Railway Monitoring

Railway provides built-in monitoring:
- CPU and memory usage
- Request logs
- Error tracking
- Automatic restarts

### 2. Vercel Analytics

Vercel provides:
- Performance metrics
- User analytics
- Error tracking
- Real-time logs

### 3. Custom Health Checks

The application includes health check endpoints:
- `/health` - Basic health check
- `/` - API information

## 🚀 Production Checklist

### Pre-Launch
- [ ] All environment variables configured
- [ ] Database migrations completed
- [ ] S3 bucket permissions set
- [ ] Replicate API working
- [ ] CORS properly configured
- [ ] SSL certificates active
- [ ] Domain DNS configured

### Post-Launch
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify all features work
- [ ] Test user registration
- [ ] Test photo generation
- [ ] Monitor credit system

## 🔧 Troubleshooting

### Common Issues

**Backend not starting:**
- Check environment variables
- Verify database connection
- Check logs in Railway dashboard

**Frontend API errors:**
- Verify `REACT_APP_API_URL` is correct
- Check CORS configuration
- Ensure backend is running

**File upload issues:**
- Verify S3 credentials
- Check bucket permissions
- Verify file size limits

**WebSocket connection failed:**
- Check `REACT_APP_WS_URL` configuration
- Verify WebSocket support in Railway
- Check firewall settings

### Debug Commands

```bash
# Check backend health
curl https://your-backend-url.railway.app/health

# Check API documentation
open https://your-backend-url.railway.app/docs

# Test file upload
curl -X POST https://your-backend-url.railway.app/photos/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test-image.jpg"
```

## 📞 Support

For deployment issues:
1. Check Railway logs
2. Check Vercel logs
3. Verify environment variables
4. Test API endpoints manually
5. Check AWS S3 permissions

## 🎉 Success!

Once deployed, your PhotoPro AI application will be live and ready for users! 

- **Backend**: `https://your-backend-url.railway.app`
- **Frontend**: `https://your-frontend-url.vercel.app`
- **API Docs**: `https://your-backend-url.railway.app/docs`

Happy deploying! 🚀
