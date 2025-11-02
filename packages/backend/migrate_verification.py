"""
Migration Script: Add verification fields to existing users
Sets verified=False for all existing users
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import asyncio

# Load environment
load_dotenv()

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

async def migrate_users():
    """Add verification fields to all existing users"""
    
    print("🔄 Starting user verification migration...")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Count existing users
        total_users = await db.users.count_documents({})
        print(f"📊 Found {total_users} users to migrate")
        
        if total_users == 0:
            print("✅ No users to migrate")
            return
        
        # Update all users to add verification fields
        result = await db.users.update_many(
            {
                # Only update users that don't have verification fields
                "verified": {"$exists": False}
            },
            {
                "$set": {
                    "verified": False,
                    "verified_method": None,
                    "verified_at": None
                }
            }
        )
        
        print(f"✅ Migration complete!")
        print(f"   • Updated: {result.modified_count} users")
        print(f"   • Matched: {result.matched_count} users")
        
        # Verify migration
        verified_count = await db.users.count_documents({"verified": True})
        unverified_count = await db.users.count_documents({"verified": False})
        
        print(f"\n📈 Current status:")
        print(f"   • Verified users: {verified_count}")
        print(f"   • Unverified users: {unverified_count}")
        print(f"   • Total users: {total_users}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        client.close()
        print("\n🔒 Database connection closed")


if __name__ == "__main__":
    asyncio.run(migrate_users())
