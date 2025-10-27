"""
Script to generate dummy profiles for testing the dating app
"""
import asyncio
import random
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
import uuid
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'dating_app')

# Arabic names
MALE_NAMES = [
    "محمد", "أحمد", "علي", "حسن", "حسين", "عمر", "خالد", "يوسف", "كريم", "سعد",
    "عبدالله", "فيصل", "سلطان", "مشعل", "ماجد", "طارق", "وليد", "رامي", "زياد", "نواف"
]

FEMALE_NAMES = [
    "فاطمة", "عائشة", "خديجة", "مريم", "سارة", "نور", "ليلى", "زينب", "رنا", "هدى",
    "سلمى", "دانة", "لينا", "ريم", "نورة", "شهد", "غادة", "أسماء", "منى", "سمية"
]

LOCATIONS = [
    "دبي، الإمارات", "الرياض، السعودية", "جدة، السعودية", "الدوحة، قطر",
    "الكويت، الكويت", "المنامة، البحرين", "مسقط، عمان", "القاهرة، مصر",
    "بيروت، لبنان", "عمان، الأردن", "الدار البيضاء، المغرب", "تونس، تونس"
]

OCCUPATIONS = [
    "مهندس برمجيات", "طبيب", "مهندس مدني", "محاسب", "مصمم جرافيك",
    "مدير تسويق", "معلم", "محامي", "صيدلي", "مهندس ميكانيكي",
    "طبيب أسنان", "مدير مبيعات", "مصور فوتوغرافي", "كاتب", "رائد أعمال"
]

INTERESTS = [
    "السفر", "القراءة", "الرياضة", "الطبخ", "الموسيقى",
    "التصوير", "السباحة", "اليوغا", "التمارين الرياضية", "الأفلام",
    "التسلق", "الغوص", "الرسم", "البرمجة", "التصميم",
    "الكتابة", "الطبيعة", "المشي", "الدراجات", "المغامرات"
]

BIOS = [
    "أحب السفر واستكشاف أماكن جديدة 🌍✈️",
    "عاشق للقهوة والكتب الجيدة ☕📚",
    "مهووس باللياقة البدنية وحياة صحية 💪🥗",
    "مصور هاواي أبحث عن مغامرات جديدة 📸",
    "أحب الضحك والاستمتاع بالحياة 😄",
    "عشاق الطبيعة والمشي لمسافات طويلة 🏔️",
    "طباخ مبتدئ أبحث عن شريك في المطبخ 👨‍🍳",
    "محب للموسيقى الحية والحفلات الموسيقية 🎵",
    "باحث عن علاقة جادة وصادقة ❤️",
    "أستمتع بالأيام الهادئة في المنزل وأيضاً المغامرات 🏠⛰️"
]

# Unsplash photo URLs (random profile photos)
MALE_PHOTOS = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d",
    "https://images.unsplash.com/photo-1557862921-37829c790f19",
    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7",
]

FEMALE_PHOTOS = [
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80",
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1",
]


async def generate_dummy_profiles(count=50):
    """Generate dummy profiles"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client.dating_app
    
    print(f"Generating {count} dummy profiles...")
    
    profiles = []
    
    for i in range(count):
        # Random gender
        gender = random.choice(['male', 'female'])
        
        # Select name and photos based on gender
        if gender == 'male':
            name = random.choice(MALE_NAMES)
            photos = [random.choice(MALE_PHOTOS) + f"?w=800&h=1000&fit=crop&{i}"]
        else:
            name = random.choice(FEMALE_NAMES)
            photos = [random.choice(FEMALE_PHOTOS) + f"?w=800&h=1000&fit=crop&{i}"]
        
        # Random age between 20-45
        age = random.randint(20, 45)
        
        # Random interests (3-6 interests)
        selected_interests = random.sample(INTERESTS, random.randint(3, 6))
        
        # Random languages (1-3 languages)
        languages = random.sample(['العربية', 'English', 'Français', 'Español'], random.randint(1, 3))
        
        # Create profile
        profile = {
            "id": str(uuid.uuid4()),
            "user_id": f"dummy_user_{i}_{random.randint(1000, 9999)}",
            "display_name": name,
            "age": age,
            "gender": gender,
            "location": random.choice(LOCATIONS),
            "bio": random.choice(BIOS),
            "occupation": random.choice(OCCUPATIONS),
            "photos": photos,
            "interests": selected_interests,
            "languages": languages,
            "height": random.randint(155, 195),
            "relationship_goals": random.choice([
                'long-term-partner', 'long-term-open', 'short-term-open', 
                'new-friends', 'figuring-out'
            ]),
            "education": random.choice(['bachelors', 'masters', 'high-school']),
            "zodiac_sign": random.choice([
                'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
            ]),
            "pets": random.choice(['dog', 'cat', 'none', 'both']),
            "drinking": random.choice(['no', 'socially', 'occasionally']),
            "smoking": random.choice(['no', 'sometimes', 'socially']),
            "exercise": random.choice(['active', 'sometimes', 'rarely']),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        profiles.append(profile)
    
    # Insert all profiles
    if profiles:
        result = await db.profiles.insert_many(profiles)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} profiles")
    
    client.close()
    print("Done!")


if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    asyncio.run(generate_dummy_profiles(count))
