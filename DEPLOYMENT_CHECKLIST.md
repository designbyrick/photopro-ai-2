# 🚀 PhotoPro AI - Production Deployment Checklist

## Pre-Deployment Setup

### ✅ Backend Preparation
- [ ] All code committed to repository
- [ ] Environment variables documented
- [ ] Database migrations ready
- [ ] Production setup script tested
- [ ] Health check endpoints working
- [ ] Monitoring configured

### ✅ Frontend Preparation  
- [ ] Build process tested locally
- [ ] Environment variables configured
- [ ] API endpoints updated
- [ ] WebSocket configuration ready
- [ ] Production build optimized

### ✅ External Services
- [ ] AWS S3 bucket created
- [ ] S3 permissions configured
- [ ] Replicate API account setup
- [ ] API tokens generated
- [ ] Domain name registered (optional)

## 🚀 Deployment Steps

### Step 1: Railway Backend Deployment

1. **Connect Repository**
   ```bash
   # Go to Railway Dashboard
   # New Project → Deploy from GitHub repo
   # Select your repository
   # Set root directory to: backend
   ```

2. **Add PostgreSQL Database**
   ```bash
   # In Railway dashboard
   # New → Database → PostgreSQL
   # Database will auto-connect to your service
   ```

3. **Configure Environment Variables**
   ```bash
   # In Railway project settings → Variables
   DATABASE_URL=postgresql://... (auto-set by Railway)
   SECRET_KEY=your-super-secret-jwt-key
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_BUCKET_NAME=your-s3-bucket-name
   AWS_REGION=us-east-1
   REPLICATE_API_TOKEN=your-replicate-token
   CORS_ORIGINS=https://your-frontend-url.vercel.app
   ```

4. **Deploy Backend**
   ```bash
   # Railway auto-deploys on push to main
   git add .
   git commit -m "Deploy PhotoPro AI backend"
   git push origin main
   ```

5. **Verify Backend Deployment**
   ```bash
   # Check health endpoint
   curl https://your-railway-url.railway.app/health
   
   # Check API docs
   open https://your-railway-url.railway.app/docs
   ```

### Step 2: Vercel Frontend Deployment

1. **Connect Repository**
   ```bash
   # Go to Vercel Dashboard
   # New Project → Import from GitHub
   # Select your repository
   # Set root directory to: frontend
   # Framework: Create React App
   ```

2. **Configure Environment Variables**
   ```bash
   # In Vercel project settings → Environment Variables
   REACT_APP_API_URL=https://your-railway-url.railway.app
   REACT_APP_WS_URL=wss://your-railway-url.railway.app
   GENERATE_SOURCEMAP=false
   ```

3. **Deploy Frontend**
   ```bash
   # Vercel auto-deploys on push to main
   git add .
   git commit -m "Deploy PhotoPro AI frontend"
   git push origin main
   ```

4. **Verify Frontend Deployment**
   ```bash
   # Visit your Vercel URL
   # Test login/signup
   # Test photo upload
   # Test photo generation
   ```

### Step 3: AWS S3 Setup

1. **Create S3 Bucket**
   ```bash
   # AWS S3 Console → Create bucket
   # Name: photopro-ai-images (or your choice)
   # Region: us-east-1
   # Uncheck "Block all public access"
   ```

2. **Configure Bucket Policy**
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

3. **Create IAM User**
   ```bash
   # AWS IAM Console → Create user
   # Username: photopro-ai-s3-user
   # Attach policy: AmazonS3FullAccess
   # Create access keys
   # Add keys to Railway environment variables
   ```

### Step 4: Replicate API Setup

1. **Create Replicate Account**
   ```bash
   # Go to https://replicate.com
   # Sign up for account
   # Go to Account → API tokens
   # Create new token
   ```

2. **Configure API Token**
   ```bash
   # Add to Railway environment variables
   REPLICATE_API_TOKEN=r8_your_token_here
   ```

## 🔍 Post-Deployment Verification

### Backend Health Checks
- [ ] `/health` returns 200 OK
- [ ] `/health/detailed` shows all services healthy
- [ ] `/docs` loads API documentation
- [ ] Database connection working
- [ ] S3 connection working
- [ ] Replicate API connection working

### Frontend Functionality Tests
- [ ] Application loads without errors
- [ ] User registration works
- [ ] User login works
- [ ] Photo upload works
- [ ] Photo generation works
- [ ] WebSocket connection works
- [ ] Credit system works
- [ ] Admin dashboard accessible

### Integration Tests
- [ ] End-to-end photo generation flow
- [ ] Credit deduction working
- [ ] Real-time status updates
- [ ] File download working
- [ ] Error handling working

## 🚨 Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check Railway logs
# Verify environment variables
# Check database connection
# Test locally first
```

**Frontend API errors:**
```bash
# Check REACT_APP_API_URL
# Verify CORS settings
# Check network tab in browser
# Test API endpoints directly
```

**File upload issues:**
```bash
# Check S3 credentials
# Verify bucket permissions
# Check file size limits
# Test S3 connection
```

**WebSocket connection failed:**
```bash
# Check REACT_APP_WS_URL
# Verify WebSocket support
# Check firewall settings
# Test WebSocket endpoint
```

### Debug Commands

```bash
# Test backend health
curl https://your-backend-url.railway.app/health

# Test API documentation
open https://your-backend-url.railway.app/docs

# Test file upload
curl -X POST https://your-backend-url.railway.app/photos/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test-image.jpg"

# Check system metrics
curl https://your-backend-url.railway.app/metrics/system
```

## 📊 Monitoring Setup

### Railway Monitoring
- [ ] CPU and memory usage
- [ ] Request logs
- [ ] Error tracking
- [ ] Automatic restarts

### Vercel Analytics
- [ ] Performance metrics
- [ ] User analytics
- [ ] Error tracking
- [ ] Real-time logs

### Custom Monitoring
- [ ] Health check endpoints
- [ ] System metrics
- [ ] Application metrics
- [ ] External service status

## 🔐 Security Checklist

- [ ] JWT secret key is strong and unique
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation working
- [ ] File upload restrictions
- [ ] Admin access secured
- [ ] Environment variables secured

## 🎉 Launch Checklist

### Pre-Launch
- [ ] All tests passing
- [ ] Performance acceptable
- [ ] Security review complete
- [ ] Monitoring active
- [ ] Backup strategy in place
- [ ] Documentation complete

### Launch Day
- [ ] Deploy to production
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify all features work
- [ ] Test user registration
- [ ] Test photo generation
- [ ] Monitor credit system

### Post-Launch
- [ ] Monitor for 24 hours
- [ ] Check user feedback
- [ ] Review performance metrics
- [ ] Fix any issues
- [ ] Plan next improvements

## 📞 Support Contacts

- **Railway Support**: [Railway Help](https://railway.app/help)
- **Vercel Support**: [Vercel Support](https://vercel.com/support)
- **AWS Support**: [AWS Support](https://aws.amazon.com/support)
- **Replicate Support**: [Replicate Help](https://replicate.com/help)

## 🎯 Success Metrics

After successful deployment, you should have:

- ✅ **Backend**: `https://your-backend-url.railway.app`
- ✅ **Frontend**: `https://your-frontend-url.vercel.app`
- ✅ **API Docs**: `https://your-backend-url.railway.app/docs`
- ✅ **Health Check**: `https://your-backend-url.railway.app/health`
- ✅ **Admin Dashboard**: Accessible via frontend
- ✅ **Real-time Updates**: WebSocket working
- ✅ **File Storage**: S3 integration working
- ✅ **AI Processing**: Replicate API working

## 🚀 Next Steps

After successful deployment:

1. **User Testing**: Invite beta users
2. **Performance Monitoring**: Track metrics
3. **Feature Iteration**: Based on feedback
4. **Scaling**: As user base grows
5. **Advanced Features**: Mobile app, enterprise features

---

**🎉 Congratulations! Your PhotoPro AI application is now live and ready for users!**
