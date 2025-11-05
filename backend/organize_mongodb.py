#!/usr/bin/env python3
"""
MongoDB Organization Script for Pizoo
Creates indexes, organizes collections, and ensures optimal structure
"""

import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, TEXT, GEOSPHERE
import asyncio
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/pizoo')

async def organize_mongodb():
    """Organize MongoDB collections and create indexes"""
    
    print("🗄️ MongoDB Organization Script")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URL)
        db = client.get_database()
        
        print(f"✅ Connected to MongoDB: {db.name}")
        print()
        
        # Get existing collections
        existing_collections = await db.list_collection_names()
        print(f"📂 Existing Collections: {len(existing_collections)}")
        for coll in existing_collections:
            count = await db[coll].count_documents({})
            print(f"   - {coll}: {count} documents")
        print()
        
        # =========================================
        # 1. USERS COLLECTION
        # =========================================
        print("👥 Organizing 'users' collection...")
        
        # Create indexes
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.users.create_index([("user_id", ASCENDING)], unique=True)
        await db.users.create_index([("phone", ASCENDING)], sparse=True)
        await db.users.create_index([("verified", ASCENDING)])
        await db.users.create_index([("created_at", DESCENDING)])
        await db.users.create_index([("last_active", DESCENDING)])
        
        # Geospatial index for location-based matching
        await db.users.create_index([("location", GEOSPHERE)])
        
        # Text search index for bio and interests
        await db.users.create_index([
            ("name", TEXT),
            ("bio", TEXT),
            ("interests", TEXT)
        ])
        
        print("   ✅ Indexes created for users collection")
        
        # =========================================
        # 2. MATCHES COLLECTION
        # =========================================
        print("💕 Organizing 'matches' collection...")
        
        if "matches" not in existing_collections:
            await db.create_collection("matches")
        
        await db.matches.create_index([("match_id", ASCENDING)], unique=True)
        await db.matches.create_index([("user1_id", ASCENDING)])
        await db.matches.create_index([("user2_id", ASCENDING)])
        await db.matches.create_index([("created_at", DESCENDING)])
        await db.matches.create_index([("status", ASCENDING)])
        
        # Compound index for finding matches between two users
        await db.matches.create_index([
            ("user1_id", ASCENDING),
            ("user2_id", ASCENDING)
        ])
        
        print("   ✅ Indexes created for matches collection")
        
        # =========================================
        # 3. MESSAGES COLLECTION
        # =========================================
        print("💬 Organizing 'messages' collection...")
        
        if "messages" not in existing_collections:
            await db.create_collection("messages")
        
        await db.messages.create_index([("message_id", ASCENDING)], unique=True)
        await db.messages.create_index([("match_id", ASCENDING)])
        await db.messages.create_index([("sender_id", ASCENDING)])
        await db.messages.create_index([("created_at", DESCENDING)])
        await db.messages.create_index([("read", ASCENDING)])
        
        # Compound index for chat history
        await db.messages.create_index([
            ("match_id", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        print("   ✅ Indexes created for messages collection")
        
        # =========================================
        # 4. IMAGES COLLECTION
        # =========================================
        print("🖼️ Organizing 'images' collection...")
        
        if "images" not in existing_collections:
            await db.create_collection("images")
        
        await db.images.create_index([("image_id", ASCENDING)], unique=True)
        await db.images.create_index([("user_id", ASCENDING)])
        await db.images.create_index([("type", ASCENDING)])  # profile, gallery, message
        await db.images.create_index([("created_at", DESCENDING)])
        
        # Compound index for user's images
        await db.images.create_index([
            ("user_id", ASCENDING),
            ("type", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        print("   ✅ Indexes created for images collection")
        
        # =========================================
        # 5. NOTIFICATIONS COLLECTION
        # =========================================
        print("🔔 Organizing 'notifications' collection...")
        
        if "notifications" not in existing_collections:
            await db.create_collection("notifications")
        
        await db.notifications.create_index([("notification_id", ASCENDING)], unique=True)
        await db.notifications.create_index([("user_id", ASCENDING)])
        await db.notifications.create_index([("read", ASCENDING)])
        await db.notifications.create_index([("created_at", DESCENDING)])
        
        # Compound index for user's unread notifications
        await db.notifications.create_index([
            ("user_id", ASCENDING),
            ("read", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        print("   ✅ Indexes created for notifications collection")
        
        # =========================================
        # 6. SUBSCRIPTIONS COLLECTION
        # =========================================
        print("💳 Organizing 'subscriptions' collection...")
        
        if "subscriptions" not in existing_collections:
            await db.create_collection("subscriptions")
        
        await db.subscriptions.create_index([("subscription_id", ASCENDING)], unique=True)
        await db.subscriptions.create_index([("user_id", ASCENDING)])
        await db.subscriptions.create_index([("plan", ASCENDING)])
        await db.subscriptions.create_index([("status", ASCENDING)])
        await db.subscriptions.create_index([("expires_at", ASCENDING)])
        
        # Compound index for active subscriptions
        await db.subscriptions.create_index([
            ("user_id", ASCENDING),
            ("status", ASCENDING),
            ("expires_at", DESCENDING)
        ])
        
        print("   ✅ Indexes created for subscriptions collection")
        
        # =========================================
        # 7. SESSIONS COLLECTION (Optional)
        # =========================================
        print("🔑 Organizing 'sessions' collection...")
        
        if "sessions" not in existing_collections:
            await db.create_collection("sessions")
        
        await db.sessions.create_index([("session_id", ASCENDING)], unique=True)
        await db.sessions.create_index([("user_id", ASCENDING)])
        await db.sessions.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)  # TTL index
        
        print("   ✅ Indexes created for sessions collection")
        
        # =========================================
        # 8. CALL_LOGS COLLECTION
        # =========================================
        print("📞 Organizing 'call_logs' collection...")
        
        if "call_logs" not in existing_collections:
            await db.create_collection("call_logs")
        
        await db.call_logs.create_index([("call_id", ASCENDING)], unique=True)
        await db.call_logs.create_index([("room_name", ASCENDING)])
        await db.call_logs.create_index([("caller_id", ASCENDING)])
        await db.call_logs.create_index([("callee_id", ASCENDING)])
        await db.call_logs.create_index([("started_at", DESCENDING)])
        
        # Compound index for user's call history
        await db.call_logs.create_index([
            ("caller_id", ASCENDING),
            ("started_at", DESCENDING)
        ])
        
        print("   ✅ Indexes created for call_logs collection")
        
        # =========================================
        # STATISTICS
        # =========================================
        print()
        print("=" * 60)
        print("📊 ORGANIZATION COMPLETE")
        print("=" * 60)
        
        # Get updated statistics
        all_collections = await db.list_collection_names()
        print(f"\n📂 Total Collections: {len(all_collections)}")
        
        for coll_name in sorted(all_collections):
            count = await db[coll_name].count_documents({})
            indexes = await db[coll_name.list_indexes().to_list(length=None)
            print(f"\n   {coll_name}:")
            print(f"      Documents: {count}")
            print(f"      Indexes: {len(indexes)}")
            for idx in indexes:
                if idx['name'] != '_id_':
                    keys = ', '.join([f"{k[0]}({k[1]})" for k in idx.get('key', {}).items()])
                    unique = " [UNIQUE]" if idx.get('unique') else ""
                    print(f"         - {idx['name']}: {keys}{unique}")
        
        print()
        print("=" * 60)
        print("✅ MongoDB organization completed successfully!")
        print("=" * 60)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(organize_mongodb())
