# 🔧 Replicate API Setup Guide

This guide will help you set up the Replicate API integration for PhotoPro AI.

## 📋 Prerequisites

1. **Replicate Account**: Sign up at [replicate.com](https://replicate.com)
2. **API Token**: Get your API token from your Replicate account
3. **Credits**: Ensure you have sufficient credits in your Replicate account

## 🚀 Setup Steps

### 1. Create Replicate Account

1. Go to [replicate.com](https://replicate.com)
2. Sign up for a free account
3. Verify your email address

### 2. Get API Token

1. Log into your Replicate account
2. Go to **Account** → **API tokens**
3. Click **Create token**
4. Copy the token (starts with `r8_`)

### 3. Configure Environment Variables

Add your Replicate API token to your environment:

```bash
# In your .env file
REPLICATE_API_TOKEN=r8_your_token_here
```

### 4. Test Integration

Run the test script to verify everything works:

```bash
cd backend
python test_replicate.py
```

## 🎨 Supported Styles

The integration supports 4 professional photo styles:

- **Corporate**: Business professional look
- **Creative**: Artistic and modern style  
- **Formal**: Traditional professional appearance
- **Casual**: Smart casual business look

## 💰 Pricing

Replicate charges per prediction:
- **PhotoMaker model**: ~$0.10-0.50 per generation
- **Processing time**: 30-60 seconds per photo
- **Quality**: High-resolution professional results

## 🔧 Model Configuration

The integration uses the **PhotoMaker** model with optimized parameters:

```python
model_params = {
    "corporate": {"style_strength": 25, "steps": 50},
    "creative": {"style_strength": 30, "steps": 60},
    "formal": {"style_strength": 20, "steps": 50},
    "casual": {"style_strength": 35, "steps": 55}
}
```

## 🚨 Troubleshooting

### Common Issues

**"Replicate API not configured"**
- Check your `REPLICATE_API_TOKEN` environment variable
- Ensure the token is valid and active

**"No output from AI model"**
- Check your Replicate account credits
- Verify the model is available
- Check your internet connection

**"AI processing failed"**
- Check Replicate API status
- Verify your account has sufficient credits
- Try again in a few minutes

### Debug Commands

```bash
# Test API connection
python test_replicate.py

# Check environment variables
echo $REPLICATE_API_TOKEN

# Test with curl (if backend is running)
curl -X POST http://localhost:8000/photos/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "original_url=https://example.com/image.jpg" \
  -F "style=corporate"
```

## 📊 Monitoring

Track your Replicate usage:
1. **Replicate Dashboard**: Monitor API calls and costs
2. **Application Logs**: Check backend logs for errors
3. **Credit System**: Monitor user credit consumption

## 🎯 Next Steps

After setting up Replicate API:

1. **Test locally**: Run the test script
2. **Deploy backend**: Push to Railway
3. **Configure production**: Set environment variables
4. **Test end-to-end**: Generate a real photo
5. **Monitor usage**: Track costs and performance

## 📞 Support

- **Replicate Docs**: [replicate.com/docs](https://replicate.com/docs)
- **Replicate Support**: [replicate.com/help](https://replicate.com/help)
- **PhotoPro AI Issues**: Check project documentation

---

**🎉 Once configured, your PhotoPro AI will be able to generate professional headshots using advanced AI technology!**
