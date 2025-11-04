# 👥 Demo Users Seeding Guide

**Last Updated:** 2025-11-04

---

## 📋 Overview

The demo user seeding script creates realistic user profiles for testing and demonstration purposes. It fetches real photos and names from randomuser.me API and creates complete User + Profile documents in MongoDB.

---

## ✨ Features

- **Realistic Data:** Names, photos, and locations from randomuser.me
- **European Focus:** CH, FR, IT, DE, AT, ES nationalities
- **Gender Distribution:** 70% female, 30% male (customizable)
- **Age Distribution:**
  - Female: 60% (20-30), 40% (40-54)
  - Male: Uniform (18-50)
- **Safety First:** Requires explicit `SEED_DEMO_USERS=true` flag
- **Dry Run Mode:** Test without database insertion
- **Batch Processing:** Inserts in batches of 50 for performance
- **UUID-based IDs:** No MongoDB ObjectId conflicts

---

## 🚀 Usage

### Prerequisites:
```bash
cd /app/scripts
npm install mongodb axios yargs
```

### Basic Usage:
```bash
# Dry run (test mode, no DB changes)
SEED_DEMO_USERS=true node seed_demo_users.js --dry-run

# Insert 500 users (350 female, 150 male)
SEED_DEMO_USERS=true MONGO_URL="mongodb://localhost:27017" DB_NAME="pizoo_database" \
  node seed_demo_users.js --count=500

# Custom distribution
SEED_DEMO_USERS=true node seed_demo_users.js --count=1000 --female-ratio=0.6
```

### Environment Variables:
```bash
MONGO_URL         # MongoDB connection string (required)
DB_NAME           # Database name (default: pizoo_database)
SEED_DEMO_USERS   # Must be "true" to enable (safety)
```

### Command Line Options:
```bash
--count=<number>           # Total users to create (default: 500)
--dry-run                  # Test mode, no DB insertion
--female-ratio=<0-1>       # Ratio of female users (default: 0.7)
```

---

## 📊 Data Structure

### User Document:
```javascript
{
  id: "uuid-v4",
  name: "Sofia Mueller",
  email: "sofia.mueller4523@demo.test",
  phone_number: "+41791234567",
  password_hash: "$2b$12$demo...",
  email_verified: true,
  created_at: ISODate,
  verified: true,
  verified_method: "demo_seeded",
  demo: true,  // ⚠️ Important flag
  // ... other fields
}
```

### Profile Document:
```javascript
{
  id: "uuid-v4",
  user_id: "uuid-v4",  // References User.id
  display_name: "Sofia",
  bio: "Hi, I'm Sofia from Switzerland...",
  age: 25,
  gender: "female",
  photos: ["https://randomuser.me/api/portraits/women/32.jpg"],
  location: "Zurich, Switzerland",
  latitude: 47.3769,
  longitude: 8.5417,
  interests: ["Travel", "Music", "Yoga"],
  demo: true,  // ⚠️ Important flag
  // ... other fields
}
```

---

## 🔐 Safety Features

### 1. **Explicit Enable Flag:**
Script requires `SEED_DEMO_USERS=true` to prevent accidental seeding in production.

### 2. **Demo Flag:**
All generated users have `demo: true` for easy filtering and deletion:
```javascript
// Query only demo users
db.users.find({ demo: true })

// Query only real users
db.users.find({ demo: { $ne: true } })
```

### 3. **Cleanup Command:**
```javascript
// Remove all demo users and profiles
db.users.deleteMany({ demo: true })
db.profiles.deleteMany({ demo: true })
```

---

## 📋 Examples

### Example 1: Quick Test (10 users)
```bash
SEED_DEMO_USERS=true node seed_demo_users.js --count=10 --dry-run
```

### Example 2: Staging Environment (500 users)
```bash
SEED_DEMO_USERS=true \
  MONGO_URL="mongodb://localhost:27017" \
  DB_NAME="pizoo_staging" \
  node seed_demo_users.js --count=500
```

### Example 3: Custom Distribution (1000 users, 50% female)
```bash
SEED_DEMO_USERS=true \
  MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net" \
  DB_NAME="pizoo_database" \
  node seed_demo_users.js --count=1000 --female-ratio=0.5
```

---

## 🧪 Testing

### Dry Run Output:
```
🌱 Starting Demo User Seeding...
============================================================
Configuration:
  MONGO_URL: mongodb://***:***@localhost:27017
  DB_NAME: pizoo_database
  TOTAL_USERS: 500
  FEMALE_RATIO: 70%
  DRY_RUN: true
============================================================

📊 Distribution:
  Female: 350
  Male: 150

🌐 Fetching data from randomuser.me...
✅ Fetched 350 female and 150 male profiles

🔄 Converting to database schema...
✅ Generated 500 user and profile documents

🔍 DRY RUN - Sample 3 users:

1. Emma Dubois (female, 25)
   Paris, France
   Interests: Travel, Music, Photography
   Photo: https://randomuser.me/api/portraits/women/44.jpg...

2. Sofia Romano (female, 42)
   Rome, Italy
   Interests: Cooking, Wine, Art
   Photo: https://randomuser.me/api/portraits/women/65.jpg...

3. Luca Schmidt (male, 28)
   Berlin, Germany
   Interests: Sports, Gaming, Movies
   Photo: https://randomuser.me/api/portraits/men/32.jpg...

✅ DRY RUN complete. Use --dry-run=false to insert into database.
```

---

## 🗂️ Database Indexes

Script automatically creates these indexes:

**Users:**
- `email` (unique, sparse)
- `id` (unique)
- `demo`

**Profiles:**
- `user_id` (unique)
- `id` (unique)
- `demo`
- `gender`
- `age`

---

## ⚠️ Important Notes

### 1. **Network Dependency:**
Script requires internet access to fetch data from randomuser.me API.

### 2. **Rate Limits:**
randomuser.me has rate limits. For large seeding (>5000 users), run in batches:
```bash
# Batch 1
SEED_DEMO_USERS=true node seed_demo_users.js --count=500
# Wait 1 minute
# Batch 2
SEED_DEMO_USERS=true node seed_demo_users.js --count=500
```

### 3. **Photo URLs:**
Photos are hosted on randomuser.me. Consider downloading and uploading to Cloudinary for production use.

### 4. **Email Addresses:**
Uses `@demo.test` domain to avoid conflicts with real emails. Filter out in production login.

### 5. **Password Hashes:**
All demo users have placeholder password hashes. They cannot actually log in (by design).

---

## 🔍 Verification

### Check Seeded Data:
```javascript
// MongoDB Shell
use pizoo_database

// Count demo users
db.users.countDocuments({ demo: true })

// Count by gender
db.profiles.aggregate([
  { $match: { demo: true } },
  { $group: { _id: "$gender", count: { $sum: 1 } } }
])

// Sample demo profiles
db.profiles.find({ demo: true }).limit(5).pretty()
```

### Filter in Application:
```javascript
// Backend API - exclude demo users
const realUsers = await db.collection('users').find({ 
  demo: { $ne: true } 
}).toArray();

// Frontend - show demo badge
{profile.demo && <Badge>DEMO</Badge>}
```

---

## 🚀 Production Deployment

### DO NOT run on production without:
1. Setting `SEED_DEMO_USERS=true` explicitly
2. Using a non-production database
3. Testing with `--dry-run` first
4. Having a backup ready
5. Planning cleanup strategy

### Recommended Approach:
```bash
# 1. Test on staging
SEED_DEMO_USERS=true \
  MONGO_URL="mongodb://staging-db" \
  DB_NAME="pizoo_staging" \
  node seed_demo_users.js --count=100 --dry-run

# 2. Verify
# 3. Run actual seeding
# 4. Test application
# 5. Cleanup if needed
```

---

## 📞 Support

For issues or questions:
1. Check script logs for error messages
2. Verify MongoDB connection
3. Test randomuser.me API: `curl https://randomuser.me/api/`
4. Review this guide

---

**Script Location:** `/app/scripts/seed_demo_users.js`  
**Version:** 1.0.0  
**Last Updated:** 2025-11-04
