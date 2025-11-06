# 💕 Pizoo Dating App

**Modern dating application for the MENA region with AI-powered matching**

[![Deploy](https://vercel.com/button)](https://vercel.com/import/project?template=https://github.com/Shatha-db/pizoo)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![License](https://img.shields.io/badge/license-private-red)]()

---

## 🌟 Features

- 🌍 **9 Languages** - Full internationalization support
- 🎥 **Video/Voice Calls** - LiveKit integration
- 💬 **Real-time Chat** - Instant messaging
- 🔐 **Secure Authentication** - JWT + OAuth2
- 🖼️ **Image Upload** - Cloudinary integration
- 📱 **Progressive Web App** - Mobile-first design
- 🌙 **RTL Support** - Arabic language optimized
- 🔒 **GDPR Compliant** - Privacy-first approach

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and Yarn
- Python 3.11+
- MongoDB 5.0+

### Installation

```bash
# Clone repository
git clone https://github.com/Shatha-db/pizoo.git
cd pizoo

# Install frontend
cd frontend
yarn install

# Install backend
cd ../backend
pip install -r requirements.txt
```

### Configuration

Create `.env` files:

**Backend (`backend/.env`):**
```env
MONGO_URL=mongodb://localhost:27017/pizoo
JWT_SECRET=your_secret_key
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
CLOUDINARY_URL=cloudinary://key:secret@cloud_name
```

**Frontend (`frontend/.env`):**
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Run Development

```bash
# Start backend
cd backend
python server.py

# Start frontend (new terminal)
cd frontend
yarn start
```

Visit http://localhost:3000

---

## 📚 Documentation

- **[Complete Setup Guide](PIZOO_PROJECT_README.md)** - Full project documentation
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Production deployment
- **[Vercel Setup](VERCEL_SETUP.md)** - Frontend deployment
- **[API Documentation](AUTH_API_DOCUMENTATION.md)** - API reference

---

## 🛠️ Tech Stack

### Frontend
- React 18
- Tailwind CSS
- shadcn/ui
- React Router v6
- react-i18next
- LiveKit React

### Backend
- FastAPI (Python)
- MongoDB
- JWT Authentication
- LiveKit
- Cloudinary
- SendGrid/Mailjet

### DevOps
- Vercel (Frontend)
- Supervisor (Backend)
- GitHub Actions (CI/CD)

---

## 📁 Project Structure

```
/app/
├── frontend/           # React application
│   ├── public/        # Static assets
│   ├── src/           # Source code
│   └── package.json   # Dependencies
│
├── backend/           # FastAPI application
│   ├── server.py      # Main API
│   ├── auth_service.py
│   └── requirements.txt
│
├── docs/              # Documentation
└── vercel.json        # Deployment config
```

---

## 🚢 Deployment

### Frontend (Vercel)

```bash
# Using Vercel CLI
vercel --prod

# Or connect GitHub repo to Vercel
```

**Environment Variables:**
- `REACT_APP_BACKEND_URL`
- `REACT_APP_SENTRY_DSN`

### Backend (Emergent/Railway/Render)

```bash
# Using supervisor
sudo supervisorctl restart backend

# Or deploy to Railway/Render
```

**Environment Variables:**
- All backend `.env` variables

---

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
yarn test

# E2E tests
yarn test:e2e
```

---

## 📊 Database Schema

### Collections

- **users** - User profiles and authentication
- **matches** - Match relationships
- **messages** - Chat messages
- **images** - Uploaded media
- **notifications** - User notifications
- **subscriptions** - Premium plans
- **sessions** - Active sessions
- **call_logs** - Video/voice call history

Run database setup:
```bash
python backend/organize_mongodb.py
```

---

## 🔐 Security

- JWT token-based authentication
- Password hashing with bcrypt
- CORS protection
- Rate limiting
- CSRF protection
- XSS prevention
- SQL injection protection (MongoDB)

---

## 🌍 Internationalization

Supported languages:
- English (en)
- Arabic (ar) - RTL
- French (fr)
- German (de)
- Spanish (es)
- Italian (it)
- Turkish (tr)
- Portuguese (pt)
- Hindi (hi)

Translation files: `frontend/public/locales/`

---

## 📞 Support

- **Website:** https://pizoo.ch
- **Email:** support@pizoo.ch
- **GitHub Issues:** [Create an issue](https://github.com/Shatha-db/pizoo/issues)

---

## 📄 License

Private - All rights reserved © 2024 Pizoo

---

## 🙏 Acknowledgments

- Built with ❤️ by the Pizoo team
- Powered by Emergent AI Platform
- Icons by Lucide React
- UI components by shadcn/ui

---

**Version:** 2.0  
**Status:** ✅ Production Ready  
**Last Updated:** November 2024
