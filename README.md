# PhotoPro AI - Professional Photo Generation Platform

An AI-powered web application that transforms user photos into professional headshots using advanced AI technology. Built with FastAPI backend and React frontend.

## 🚀 Features

- **AI Photo Generation**: Transform photos into professional headshots using Replicate API
- **Multiple Styles**: Corporate, Creative, Formal, and Casual styles
- **User Authentication**: JWT-based authentication with secure password hashing
- **Credit System**: Free credits on signup, upgradeable plans
- **Photo Gallery**: View and download generated photos
- **Responsive Design**: Modern gradient UI with mobile support
- **Real-time Processing**: Live status updates for photo generation

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM for database operations
- **JWT**: Token-based authentication
- **AWS S3**: Image storage
- **Replicate API**: AI photo processing
- **Railway**: Backend deployment

### Frontend
- **React 18**: Modern React with hooks
- **React Router**: Client-side routing
- **Axios**: HTTP client with interceptors
- **React Dropzone**: File upload handling
- **React Hot Toast**: Notifications
- **Lucide React**: Modern icons
- **Vercel**: Frontend deployment

## 📁 Project Structure

```
photopro-ai/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── auth.py                 # Authentication utilities
│   ├── config.py               # Configuration settings
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile               # Railway deployment
│   ├── railway.json           # Railway configuration
│   └── runtime.txt            # Python version
├── frontend/
│   ├── public/
│   │   └── index.html          # HTML template
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── contexts/          # React contexts
│   │   ├── services/          # API services
│   │   ├── App.js             # Main app component
│   │   └── index.js           # Entry point
│   ├── package.json           # Node dependencies
│   └── vercel.json            # Vercel deployment
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL database
- AWS S3 bucket
- Replicate API account

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Run the application:**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your backend URL
   ```

4. **Start development server:**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/photopro_ai

# JWT Authentication
SECRET_KEY=your-secret-key-change-in-production

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=your-s3-bucket-name
AWS_REGION=us-east-1

# Replicate API
REPLICATE_API_TOKEN=your-replicate-api-token
```

### Frontend Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
```

## 🚀 Deployment

### Backend (Railway)

1. **Connect your GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push to main branch**

### Frontend (Vercel)

1. **Connect your GitHub repository to Vercel**
2. **Set environment variables in Vercel dashboard**
3. **Deploy automatically on push to main branch**

## 📊 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - User login
- `GET /users/me` - Get current user
- `GET /users/me/credits` - Get user credits

### Photos
- `POST /photos/upload` - Upload image
- `POST /photos/generate` - Generate professional photo
- `GET /photos/history` - Get photo history
- `GET /photos/{id}` - Get specific photo

### Credits
- `POST /credits/purchase` - Purchase credits/upgrade plan
- `GET /credits/history` - Get credit history

## 🎨 Features Overview

### User Authentication
- Secure JWT token-based authentication
- Password hashing with bcrypt
- Protected routes and API endpoints
- Automatic token refresh

### Photo Generation
- Drag & drop file upload
- Image validation (format, size, dimensions)
- Multiple AI styles (Corporate, Creative, Formal, Casual)
- Real-time processing status
- Thumbnail generation

### Credit System
- Free 3 credits on signup
- Credit deduction per photo generation
- Plan upgrades (Free, Pro, Enterprise)
- Transaction history

### User Interface
- Modern gradient design
- Responsive mobile-first layout
- Real-time notifications
- Photo gallery with download
- User profile management

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation and sanitization
- File type and size validation
- Secure API endpoints

## 📱 Responsive Design

- Mobile-first approach
- Touch-friendly interface
- Adaptive layouts
- Modern CSS Grid and Flexbox
- Smooth animations and transitions

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📈 Performance

- Optimized image processing
- Lazy loading for photos
- Efficient database queries
- CDN-ready static assets
- Minimal bundle size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔮 Future Enhancements

- Batch photo processing
- Advanced AI models
- Social sharing features
- API rate limiting
- Advanced analytics
- Mobile app development

---

Built with ❤️ using FastAPI, React, and AI technology.
