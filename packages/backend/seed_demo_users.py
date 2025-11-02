import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

DEMO_USERS = [
    {
        "id": "demo-user-1",
        "email": "sarah@demo.com",
        "password": hash_password("demo123"),
        "name": "سارة",
        "age": 25,
        "gender": "female",
        "location": "دبي، الإمارات",
        "bio": "أحب السفر والتصوير الفوتوغرافي. أبحث عن شخص يشاركني شغفي بالمغامرات.",
        "photos": [
            "https://images.unsplash.com/photo-1697551458746-b86ccf5049d4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwxfHxkaXZlcnNlJTIwcGVvcGxlJTIwcG9ydHJhaXRzfGVufDB8fHx8MTc2MDg2MDYwOXww&ixlib=rb-4.1.0&q=85",
            "https://images.pexels.com/photos/3419650/pexels-photo-3419650.jpeg"
        ],
        "interests": ["السفر", "التصوير", "القراءة"],
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "demo-user-2",
        "email": "ahmed@demo.com",
        "password": hash_password("demo123"),
        "name": "أحمد",
        "age": 28,
        "gender": "male",
        "location": "الرياض، السعودية",
        "bio": "مهندس برمجيات، أحب الرياضة والموسيقى. أبحث عن علاقة جادة.",
        "photos": [
            "https://images.unsplash.com/photo-1749003659356-1d1a4451a49d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwyfHxkaXZlcnNlJTIwcGVvcGxlJTIwcG9ydHJhaXRzfGVufDB8fHx8MTc2MDg2MDYwOXww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1653129305118-3c5b26df576c?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwzfHxwb3J0cmFpdCUyMGhlYWRzaG90fGVufDB8fHx8MTc2MDg2MDYyMXww&ixlib=rb-4.1.0&q=85"
        ],
        "interests": ["البرمجة", "الرياضة", "الموسيقى"],
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "demo-user-3",
        "email": "layla@demo.com",
        "password": hash_password("demo123"),
        "name": "ليلى",
        "age": 23,
        "gender": "female",
        "location": "القاهرة، مصر",
        "bio": "فنانة وكاتبة، أحب الفن والثقافة. أبحث عن روح إبداعية.",
        "photos": [
            "https://images.unsplash.com/photo-1679466061812-211a6b737175?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzR8MHwxfHNlYXJjaHwzfHxkaXZlcnNlJTIwcGVvcGxlJTIwcG9ydHJhaXRzfGVufDB8fHx8MTc2MDg2MDYwOXww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1721411395539-152e35906fc6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHwyfHxwb3J0cmFpdCUyMGhlYWRzaG90fGVufDB8fHx8MTc2MDg2MDYyMXww&ixlib=rb-4.1.0&q=85"
        ],
        "interests": ["الفن", "الكتابة", "السينما"],
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "demo-user-4",
        "email": "omar@demo.com",
        "password": hash_password("demo123"),
        "name": "عمر",
        "age": 30,
        "gender": "male",
        "location": "بيروت، لبنان",
        "bio": "طبيب، أحب مساعدة الآخرين والقراءة. أبحث عن شريكة حياة.",
        "photos": [
            "https://images.unsplash.com/photo-1624395213043-fa2e123b2656?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NjZ8MHwxfHNlYXJjaHw0fHxwb3J0cmFpdCUyMGhlYWRzaG90fGVufDB8fHx8MTc2MDg2MDYyMXww&ixlib=rb-4.1.0&q=85",
            "https://images.unsplash.com/photo-1593944828451-643371360971?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHw0fHxkYXRpbmclMjBwcm9maWxlJTIwcGhvdG9zfGVufDB8fHx8MTc2MDg2MDYxNXww&ixlib=rb-4.1.0&q=85"
        ],
        "interests": ["الطب", "القراءة", "السباحة"],
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "demo-user-5",
        "email": "mira@demo.com",
        "password": hash_password("demo123"),
        "name": "ميرا",
        "age": 26,
        "gender": "female",
        "location": "عمّان، الأردن",
        "bio": "مصممة جرافيك، أحب الألوان والإبداع. أبحث عن شخص مميز.",
        "photos": [
            "https://images.pexels.com/photos/1438461/pexels-photo-1438461.jpeg",
            "https://images.pexels.com/photos/3419650/pexels-photo-3419650.jpeg"
        ],
        "interests": ["التصميم", "الفن", "الموضة"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

async def seed_users():
    print("🌱 بدء إضافة المستخدمين التجريبيين...")
    
    # Clear existing demo users
    await db.users.delete_many({"id": {"$regex": "^demo-user-"}})
    
    # Insert demo users
    await db.users.insert_many(DEMO_USERS)
    
    print(f"✅ تم إضافة {len(DEMO_USERS)} مستخدمين تجريبيين بنجاح!")
    print("\n📝 يمكنك تسجيل الدخول باستخدام:")
    for user in DEMO_USERS:
        print(f"   - {user['email']} / demo123")

if __name__ == "__main__":
    asyncio.run(seed_users())