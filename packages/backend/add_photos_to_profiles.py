"""
Script to add real photos to dummy profiles using randomuser.me API
"""
import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# NOTE: Dev-only script; runtime uses MONGO_URL from environment.
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "dating_app")

async def fetch_random_users(gender, count=50):
    """Fetch random user photos from randomuser.me"""
    url = f"https://randomuser.me/api/?results={count}&nat=us,gb,ca,au&gender={gender}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data.get('results', [])

async def update_profiles_with_photos():
    """Update dummy profiles with real photos"""
    # Connect to MongoDB - Use environment variable for database name
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔄 Fetching random user photos...")
    
    # Fetch photos for males and females
    male_users = await fetch_random_users('male', 60)
    female_users = await fetch_random_users('female', 60)
    
    print(f"✅ Fetched {len(male_users)} male photos and {len(female_users)} female photos")
    
    # Get all profiles without photos or with placeholder photos
    profiles = await db.profiles.find({}).to_list(length=None)
    
    print(f"📊 Found {len(profiles)} profiles to update")
    
    updated_count = 0
    male_index = 0
    female_index = 0
    
    for profile in profiles:
        # Determine gender
        gender = profile.get('gender', 'male')
        
        # Select photo source
        if gender == 'female' and female_index < len(female_users):
            user_data = female_users[female_index]
            female_index += 1
        elif gender == 'male' and male_index < len(male_users):
            user_data = male_users[male_index]
            male_index += 1
        else:
            continue
        
        # Extract photos (multiple sizes available)
        photos = [
            user_data['picture']['large'],
            user_data['picture']['medium'],
            user_data['picture']['thumbnail']
        ]
        
        # Update profile with photos
        await db.profiles.update_one(
            {"id": profile['id']},
            {"$set": {"photos": photos}}
        )
        
        updated_count += 1
        
        if updated_count % 10 == 0:
            print(f"⏳ Updated {updated_count} profiles...")
    
    print(f"✅ Successfully updated {updated_count} profiles with real photos!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_profiles_with_photos())
