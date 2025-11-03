/**
 * seed_demo_users.js
 *
 * Usage:
 *  node seed_demo_users.js --count=400 --dry-run=true
 *  node seed_demo_users.js --count=400 --dry-run=false
 *
 * Env:
 *  MONGO_URL (required)
 *  DB_NAME (default "pizoo_database")
 *
 * Dependencies:
 *   npm i mongodb faker@5.5.3 axios yargs
 *
 * This script:
 *  - generates demo users with Faker names (localized European variants)
 *  - creates both User and Profile documents (matching app schema)
 *  - uses AI-generated avatars from DiceBear API
 *  - inserts into collections `users` and `profiles`
 */

const { MongoClient } = require('mongodb');
const faker = require('faker');
const axios = require('axios');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .option('count', { type: 'number', default: 400 })
  .option('dry-run', { type: 'boolean', default: true })
  .argv;

const MONGO_URL = process.env.MONGO_URL;
const DB_NAME = process.env.DB_NAME || 'pizoo_database';
const TOTAL = argv.count;
const DRY_RUN = argv['dry-run'];

if (!MONGO_URL) {
  console.error('❌ MONGO_URL is required in env');
  process.exit(1);
}

// European cities for realistic Swiss/French/Italian/German locations
const EUROPEAN_CITIES = [
  { city: 'Basel', country: 'Switzerland', lat: 47.5596, lon: 7.5886 },
  { city: 'Zurich', country: 'Switzerland', lat: 47.3769, lon: 8.5417 },
  { city: 'Geneva', country: 'Switzerland', lat: 46.2044, lon: 6.1432 },
  { city: 'Bern', country: 'Switzerland', lat: 46.9480, lon: 7.4474 },
  { city: 'Lausanne', country: 'Switzerland', lat: 46.5197, lon: 6.6323 },
  { city: 'Paris', country: 'France', lat: 48.8566, lon: 2.3522 },
  { city: 'Lyon', country: 'France', lat: 45.7640, lon: 4.8357 },
  { city: 'Marseille', country: 'France', lat: 43.2965, lon: 5.3698 },
  { city: 'Nice', country: 'France', lat: 43.7102, lon: 7.2620 },
  { city: 'Rome', country: 'Italy', lat: 41.9028, lon: 12.4964 },
  { city: 'Milan', country: 'Italy', lat: 45.4642, lon: 9.1900 },
  { city: 'Florence', country: 'Italy', lat: 43.7696, lon: 11.2558 },
  { city: 'Venice', country: 'Italy', lat: 45.4408, lon: 12.3155 },
  { city: 'Berlin', country: 'Germany', lat: 52.5200, lon: 13.4050 },
  { city: 'Munich', country: 'Germany', lat: 48.1351, lon: 11.5820 },
  { city: 'Hamburg', country: 'Germany', lat: 53.5511, lon: 9.9937 },
  { city: 'Frankfurt', country: 'Germany', lat: 50.1109, lon: 8.6821 },
];

// Locales for European names
const LOCALES = ['de', 'fr', 'it', 'en'];

// Interests for profiles
const INTERESTS = [
  'Travel', 'Music', 'Sports', 'Cooking', 'Reading', 'Photography', 
  'Art', 'Dancing', 'Movies', 'Yoga', 'Hiking', 'Gaming', 'Wine', 'Coffee'
];

// Relationship goals
const RELATIONSHIP_GOALS = ['serious', 'casual', 'friendship'];

// Education levels
const EDUCATION_LEVELS = [
  'High School', 'Bachelor Degree', 'Master Degree', 'PhD', 'Vocational Training'
];

// Occupations
const OCCUPATIONS = [
  'Engineer', 'Teacher', 'Doctor', 'Designer', 'Marketing Manager', 
  'Entrepreneur', 'Architect', 'Consultant', 'Software Developer', 'Artist',
  'Nurse', 'Chef', 'Lawyer', 'Photographer', 'Musician'
];

function randomElement(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function randomElements(array, count) {
  const shuffled = [...array].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

function randomAgeForGender(gender) {
  // females: more in 20-30 (60%) and 40-54 (40%)
  if (gender === 'female') {
    return Math.random() < 0.6
      ? Math.floor(Math.random() * (30 - 20 + 1)) + 20
      : Math.floor(Math.random() * (54 - 40 + 1)) + 40;
  } else {
    // males: 18-50
    return Math.floor(Math.random() * (50 - 18 + 1)) + 18;
  }
}

function getAvatarUrl(index, gender) {
  const seed = `demo-${Date.now()}-${index}`;
  // Use appropriate DiceBear styles for male/female
  const style = gender === 'female' ? 'avataaars' : 'male';
  return `https://api.dicebear.com/8.x/${style}/svg?seed=${encodeURIComponent(seed)}`;
}

function generateUserId() {
  // Generate UUID v4-like ID (matches app schema)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

async function generateUserAndProfile(index, gender) {
  const userId = generateUserId();
  const profileId = generateUserId();
  
  // Set faker locale for European names
  const locale = randomElement(LOCALES);
  faker.locale = locale;
  
  const firstName = faker.name.firstName(gender === 'female' ? 1 : 0);
  const lastName = faker.name.lastName();
  const name = `${firstName} ${lastName}`;
  const age = randomAgeForGender(gender);
  const location = randomElement(EUROPEAN_CITIES);
  const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}${Math.floor(Math.random() * 9000 + 1000)}@demo.local`;
  const phone = `+${Math.floor(Math.random() * 90) + 10}${Math.floor(Math.random() * 900000000 + 100000000)}`;
  const bio = faker.lorem.sentence();
  const avatarUrl = getAvatarUrl(index, gender);
  
  // Calculate date of birth from age
  const currentYear = new Date().getFullYear();
  const birthYear = currentYear - age;
  const dateOfBirth = `${birthYear}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`;
  
  const now = new Date();
  const trialEndDate = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000); // 14 days trial
  
  // User document (matches User model in server.py)
  const userDoc = {
    id: userId,
    name: name,
    email: email,
    phone_number: phone,
    password_hash: '$2b$12$demopasswordhashfordemousersonly1234567890', // Demo hash
    email_verified: true,
    created_at: now,
    trial_end_date: trialEndDate,
    subscription_status: 'trial',
    terms_accepted: true,
    terms_accepted_at: now,
    profile_completed: true,
    verified: true,
    verified_method: 'demo_generated',
    verified_at: now,
    language: locale === 'de' ? 'de' : locale === 'fr' ? 'fr' : locale === 'it' ? 'it' : 'en',
    country: location.country === 'Switzerland' ? 'CH' : location.country === 'France' ? 'FR' : location.country === 'Italy' ? 'IT' : 'DE',
    premium_tier: 'free',
    likes_sent_this_week: 0,
    messages_sent_this_week: 0,
    week_start_date: now,
    demo: true, // 🏷️ Demo flag
  };
  
  // Profile document (matches Profile model in server.py)
  const profileDoc = {
    id: profileId,
    user_id: userId,
    display_name: firstName, // Use first name as display name
    bio: bio,
    date_of_birth: dateOfBirth,
    age: age,
    gender: gender,
    height: Math.floor(Math.random() * (190 - 155 + 1)) + 155, // 155-190 cm
    looking_for: gender === 'female' ? 'male' : 'female',
    interests: randomElements(INTERESTS, Math.floor(Math.random() * 5) + 3),
    photos: [avatarUrl], // At least one avatar
    location: `${location.city}, ${location.country}`,
    latitude: location.lat,
    longitude: location.lon,
    occupation: randomElement(OCCUPATIONS),
    education: randomElement(EDUCATION_LEVELS),
    relationship_goals: randomElement(RELATIONSHIP_GOALS),
    smoking: randomElement(['no', 'no', 'sometimes']), // Mostly non-smokers
    drinking: randomElement(['no', 'sometimes', 'yes']),
    has_children: Math.random() > 0.7, // 30% have children
    wants_children: Math.random() > 0.5,
    languages: locale === 'de' ? ['German', 'English'] : locale === 'fr' ? ['French', 'English'] : locale === 'it' ? ['Italian', 'English'] : ['English'],
    current_mood: randomElement(['fun', 'romantic', 'casual', 'serious']),
    created_at: now,
    updated_at: now,
    demo: true, // 🏷️ Demo flag
  };
  
  return { userDoc, profileDoc };
}

(async () => {
  console.log('🚀 Starting MongoDB Demo User Seeding Script');
  console.log('='.repeat(60));
  console.log(`📊 Configuration:`);
  console.log(`   MONGO_URL: ${MONGO_URL}`);
  console.log(`   DB_NAME: ${DB_NAME}`);
  console.log(`   TOTAL_USERS: ${TOTAL}`);
  console.log(`   DRY_RUN: ${DRY_RUN}`);
  console.log('='.repeat(60));
  
  const client = new MongoClient(MONGO_URL, { 
    useNewUrlParser: true, 
    useUnifiedTopology: true 
  });
  
  try {
    await client.connect();
    console.log('✅ Connected to MongoDB');
    
    const db = client.db(DB_NAME);
    const usersCollection = db.collection('users');
    const profilesCollection = db.collection('profiles');
    
    // Ensure indices
    console.log('\n📑 Ensuring database indices...');
    
    await usersCollection.createIndex({ email: 1 }, { unique: true, sparse: true });
    await usersCollection.createIndex({ phone_number: 1 }, { unique: true, sparse: true });
    await usersCollection.createIndex({ id: 1 }, { unique: true });
    await usersCollection.createIndex({ demo: 1 });
    await usersCollection.createIndex({ verified: 1 });
    console.log('   ✅ Users collection indices created');
    
    await profilesCollection.createIndex({ user_id: 1 }, { unique: true });
    await profilesCollection.createIndex({ id: 1 }, { unique: true });
    await profilesCollection.createIndex({ demo: 1 });
    await profilesCollection.createIndex({ gender: 1 });
    await profilesCollection.createIndex({ age: 1 });
    await profilesCollection.createIndex({ latitude: 1, longitude: 1 }); // Geo queries
    console.log('   ✅ Profiles collection indices created');
    
    // Generate users
    console.log('\n👥 Generating demo users...');
    const femaleCount = 350;
    const maleCount = TOTAL - femaleCount;
    
    const userDocs = [];
    const profileDocs = [];
    
    console.log(`   🚺 Generating ${femaleCount} female profiles...`);
    for (let i = 0; i < femaleCount; i++) {
      const { userDoc, profileDoc } = await generateUserAndProfile(i, 'female');
      userDocs.push(userDoc);
      profileDocs.push(profileDoc);
      if ((i + 1) % 50 === 0) {
        console.log(`      Progress: ${i + 1}/${femaleCount} female profiles`);
      }
    }
    
    console.log(`   🚹 Generating ${maleCount} male profiles...`);
    for (let j = 0; j < maleCount; j++) {
      const { userDoc, profileDoc } = await generateUserAndProfile(femaleCount + j, 'male');
      userDocs.push(userDoc);
      profileDocs.push(profileDoc);
      if ((j + 1) % 10 === 0) {
        console.log(`      Progress: ${j + 1}/${maleCount} male profiles`);
      }
    }
    
    console.log(`\n✅ Generated ${userDocs.length} user documents and ${profileDocs.length} profile documents`);
    
    if (DRY_RUN) {
      console.log('\n🔍 DRY RUN MODE - Sample 5 users:\n');
      console.log('='.repeat(60));
      for (let i = 0; i < Math.min(5, userDocs.length); i++) {
        console.log(`\n👤 User ${i + 1}:`);
        console.log(`   Name: ${userDocs[i].name}`);
        console.log(`   Email: ${userDocs[i].email}`);
        console.log(`   Gender: ${profileDocs[i].gender}`);
        console.log(`   Age: ${profileDocs[i].age}`);
        console.log(`   Location: ${profileDocs[i].location}`);
        console.log(`   Bio: ${profileDocs[i].bio}`);
        console.log(`   Interests: ${profileDocs[i].interests.join(', ')}`);
        console.log(`   Avatar: ${profileDocs[i].photos[0].substring(0, 80)}...`);
      }
      console.log('\n='.repeat(60));
      console.log('ℹ️  This was a DRY RUN. No data was inserted.');
      console.log('ℹ️  Run with --dry-run=false to insert data into MongoDB.');
    } else {
      console.log('\n💾 Inserting documents into MongoDB...');
      
      try {
        // Insert users in batches of 50
        const userBatches = [];
        for (let i = 0; i < userDocs.length; i += 50) {
          userBatches.push(userDocs.slice(i, i + 50));
        }
        
        let totalUsersInserted = 0;
        for (let i = 0; i < userBatches.length; i++) {
          const result = await usersCollection.insertMany(userBatches[i], { ordered: false });
          totalUsersInserted += result.insertedCount;
          console.log(`   Batch ${i + 1}/${userBatches.length}: Inserted ${result.insertedCount} users`);
        }
        
        console.log(`✅ Inserted ${totalUsersInserted} user documents`);
        
        // Insert profiles in batches of 50
        const profileBatches = [];
        for (let i = 0; i < profileDocs.length; i += 50) {
          profileBatches.push(profileDocs.slice(i, i + 50));
        }
        
        let totalProfilesInserted = 0;
        for (let i = 0; i < profileBatches.length; i++) {
          const result = await profilesCollection.insertMany(profileBatches[i], { ordered: false });
          totalProfilesInserted += result.insertedCount;
          console.log(`   Batch ${i + 1}/${profileBatches.length}: Inserted ${result.insertedCount} profiles`);
        }
        
        console.log(`✅ Inserted ${totalProfilesInserted} profile documents`);
        
        // Verify insertion
        console.log('\n🔍 Verification:');
        const demoUsersCount = await usersCollection.countDocuments({ demo: true });
        const demoProfilesCount = await profilesCollection.countDocuments({ demo: true });
        console.log(`   Demo users in DB: ${demoUsersCount}`);
        console.log(`   Demo profiles in DB: ${demoProfilesCount}`);
        
        // Show sample
        console.log('\n📋 Sample 10 demo users:');
        const samples = await usersCollection.find({ demo: true }).limit(10).toArray();
        for (const user of samples) {
          const profile = await profilesCollection.findOne({ user_id: user.id });
          console.log(`   - ${user.name} (${profile?.gender}, ${profile?.age}) from ${profile?.location}`);
        }
        
      } catch (err) {
        console.error('❌ Insert error (some duplicates may be ignored):', err.message);
        if (err.writeErrors) {
          console.error(`   Failed inserts: ${err.writeErrors.length}`);
        }
      }
    }
    
  } catch (error) {
    console.error('❌ Script failed:', error);
    process.exit(1);
  } finally {
    await client.close();
    console.log('\n✅ MongoDB connection closed');
    console.log('='.repeat(60));
    console.log('🎉 Script completed successfully!');
  }
})();
