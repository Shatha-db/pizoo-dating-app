/**
 * seed_demo_users.js - Production-Ready Demo User Seeding
 * 
 * Usage:
 *   SEED_DEMO_USERS=true node scripts/seed_demo_users.js --count=500
 * 
 * ENV:
 *   MONGO_URL - MongoDB connection string
 *   DB_NAME - Database name (default: pizoo_database)
 *   SEED_DEMO_USERS - Enable seeding (default: false for safety)
 * 
 * Features:
 *   - Fetches realistic photos from randomuser.me API
 *   - 350 female, 150 male (customizable)
 *   - European regions: CH, FR, IT, DE, AT, ES
 *   - Age distribution: 20-30 (60%), 40-54 (40%)
 *   - Proper E.164 phone numbers
 *   - UUID-based IDs (no MongoDB ObjectId)
 */

const { MongoClient } = require('mongodb');
const axios = require('axios');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

// Parse arguments
const argv = yargs(hideBin(process.argv))
  .option('count', { type: 'number', default: 500, description: 'Total users to create' })
  .option('dry-run', { type: 'boolean', default: false, description: 'Test mode without DB insertion' })
  .option('female-ratio', { type: 'number', default: 0.7, description: 'Ratio of female users (0.7 = 70%)' })
  .argv;

// Configuration
const MONGO_URL = process.env.MONGO_URL;
const DB_NAME = process.env.DB_NAME || 'pizoo_database';
const SEED_ENABLED = process.env.SEED_DEMO_USERS === 'true';
const TOTAL_USERS = argv.count;
const DRY_RUN = argv['dry-run'];
const FEMALE_RATIO = argv['female-ratio'];

// Safety check
if (!SEED_ENABLED && !DRY_RUN) {
  console.error('❌ ERROR: SEED_DEMO_USERS must be set to "true" to run seeding.');
  console.error('   This is a safety measure to prevent accidental seeding in production.');
  console.error('   Use: SEED_DEMO_USERS=true node scripts/seed_demo_users.js');
  process.exit(1);
}

if (!MONGO_URL) {
  console.error('❌ ERROR: MONGO_URL environment variable is required.');
  process.exit(1);
}

// Nationalities for European countries
const NATIONALITIES = [
  { nat: 'CH', country: 'Switzerland', cities: ['Zurich', 'Geneva', 'Basel', 'Bern', 'Lausanne'], dial: '+41' },
  { nat: 'FR', country: 'France', cities: ['Paris', 'Lyon', 'Marseille', 'Nice', 'Toulouse'], dial: '+33' },
  { nat: 'IT', country: 'Italy', cities: ['Rome', 'Milan', 'Florence', 'Venice', 'Naples'], dial: '+39' },
  { nat: 'DE', country: 'Germany', cities: ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'], dial: '+49' },
  { nat: 'AT', country: 'Austria', cities: ['Vienna', 'Salzburg', 'Innsbruck', 'Graz', 'Linz'], dial: '+43' },
  { nat: 'ES', country: 'Spain', cities: ['Madrid', 'Barcelona', 'Valencia', 'Seville', 'Bilbao'], dial: '+34' }
];

const INTERESTS = [
  'Travel', 'Music', 'Sports', 'Cooking', 'Reading', 'Photography', 
  'Art', 'Dancing', 'Movies', 'Yoga', 'Hiking', 'Gaming', 'Wine', 'Coffee',
  'Fashion', 'Fitness', 'Theater', 'Concerts', 'Volunteering', 'Languages'
];

const RELATIONSHIP_GOALS = ['serious', 'casual', 'friendship', 'not_sure'];
const EDUCATION_LEVELS = ['High School', 'Bachelor', 'Master', 'PhD', 'Vocational'];

/**
 * Generate UUID v4
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Random element from array
 */
function randomElement(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Random N elements from array
 */
function randomElements(arr, count) {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, Math.min(count, arr.length));
}

/**
 * Generate age based on distribution
 * Female: 60% (20-30), 40% (40-54)
 * Male: uniform (18-50)
 */
function generateAge(gender) {
  if (gender === 'female') {
    return Math.random() < 0.6
      ? Math.floor(Math.random() * 11) + 20  // 20-30
      : Math.floor(Math.random() * 15) + 40; // 40-54
  } else {
    return Math.floor(Math.random() * 33) + 18; // 18-50
  }
}

/**
 * Fetch users from randomuser.me API
 */
async function fetchRandomUsers(count, gender) {
  const nat = NATIONALITIES.map(n => n.nat).join(',');
  const url = `https://randomuser.me/api/?results=${count}&gender=${gender}&nat=${nat}&inc=name,email,phone,picture,location,dob,nat`;
  
  try {
    const response = await axios.get(url, { timeout: 10000 });
    return response.data.results;
  } catch (error) {
    console.error(`❌ Error fetching random users: ${error.message}`);
    return [];
  }
}

/**
 * Convert randomuser.me data to our User + Profile schema
 */
function convertToUserProfile(randomUser) {
  const userId = generateUUID();
  const profileId = generateUUID();
  const gender = randomUser.gender;
  const age = generateAge(gender);
  const nationality = NATIONALITIES.find(n => n.nat === randomUser.nat) || NATIONALITIES[0];
  
  // Calculate date of birth from age
  const currentYear = new Date().getFullYear();
  const birthYear = currentYear - age;
  const birthMonth = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
  const birthDay = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
  const dateOfBirth = `${birthYear}-${birthMonth}-${birthDay}`;
  
  const now = new Date();
  const trialEndDate = new Date(now.getTime() + 14 * 24 * 60 * 60 * 1000);
  
  // User document
  const user = {
    id: userId,
    name: `${randomUser.name.first} ${randomUser.name.last}`,
    email: `${randomUser.name.first.toLowerCase()}.${randomUser.name.last.toLowerCase()}${Math.floor(Math.random() * 9000 + 1000)}@demo.test`,
    phone_number: `${nationality.dial}${randomUser.phone.replace(/\D/g, '').slice(-9)}`,
    password_hash: '$2b$12$demopasswordhash.placeholder.for.demo.users.only',
    email_verified: true,
    created_at: now,
    trial_end_date: trialEndDate,
    subscription_status: 'trial',
    terms_accepted: true,
    terms_accepted_at: now,
    profile_completed: true,
    verified: true,
    verified_method: 'demo_seeded',
    verified_at: now,
    language: nationality.nat === 'CH' ? 'de' : nationality.nat === 'FR' ? 'fr' : nationality.nat === 'IT' ? 'it' : 'en',
    country: nationality.nat,
    premium_tier: 'free',
    likes_sent_this_week: 0,
    messages_sent_this_week: 0,
    week_start_date: now,
    demo: true
  };
  
  // Profile document
  const profile = {
    id: profileId,
    user_id: userId,
    display_name: randomUser.name.first,
    bio: `Hi, I'm ${randomUser.name.first} from ${nationality.country}! Looking to meet new people and have great conversations.`,
    date_of_birth: dateOfBirth,
    age: age,
    gender: gender,
    height: Math.floor(Math.random() * 35) + 155, // 155-190 cm
    looking_for: gender === 'female' ? 'male' : 'female',
    interests: randomElements(INTERESTS, Math.floor(Math.random() * 5) + 3),
    photos: [randomUser.picture.large], // Use large photo from randomuser.me
    location: `${randomElement(nationality.cities)}, ${nationality.country}`,
    latitude: parseFloat(randomUser.location.coordinates.latitude),
    longitude: parseFloat(randomUser.location.coordinates.longitude),
    occupation: randomElement(['Engineer', 'Teacher', 'Designer', 'Manager', 'Consultant', 'Entrepreneur']),
    education: randomElement(EDUCATION_LEVELS),
    relationship_goals: randomElement(RELATIONSHIP_GOALS),
    smoking: randomElement(['no', 'no', 'sometimes']),
    drinking: randomElement(['no', 'sometimes', 'yes']),
    has_children: Math.random() > 0.75,
    wants_children: Math.random() > 0.5,
    languages: [nationality.country === 'Switzerland' ? 'German' : nationality.country === 'France' ? 'French' : nationality.country === 'Italy' ? 'Italian' : 'English', 'English'],
    current_mood: randomElement(['fun', 'romantic', 'casual', 'serious']),
    created_at: now,
    updated_at: now,
    demo: true
  };
  
  return { user, profile };
}

/**
 * Main seeding function
 */
async function seedDemoUsers() {
  console.log('🌱 Starting Demo User Seeding...');
  console.log('='.repeat(60));
  console.log(`Configuration:`);
  console.log(`  MONGO_URL: ${MONGO_URL.replace(/\/\/(.+):(.+)@/, '//***:***@')}`);
  console.log(`  DB_NAME: ${DB_NAME}`);
  console.log(`  TOTAL_USERS: ${TOTAL_USERS}`);
  console.log(`  FEMALE_RATIO: ${FEMALE_RATIO * 100}%`);
  console.log(`  DRY_RUN: ${DRY_RUN}`);
  console.log(`  SEED_ENABLED: ${SEED_ENABLED}`);
  console.log('='.repeat(60));
  
  const femaleCount = Math.floor(TOTAL_USERS * FEMALE_RATIO);
  const maleCount = TOTAL_USERS - femaleCount;
  
  console.log(`\n📊 Distribution:`);
  console.log(`  Female: ${femaleCount}`);
  console.log(`  Male: ${maleCount}`);
  
  // Fetch random users
  console.log(`\n🌐 Fetching data from randomuser.me...`);
  const femaleUsers = await fetchRandomUsers(femaleCount, 'female');
  const maleUsers = await fetchRandomUsers(maleCount, 'male');
  
  if (femaleUsers.length === 0 || maleUsers.length === 0) {
    console.error('❌ Failed to fetch random users. Exiting.');
    process.exit(1);
  }
  
  console.log(`✅ Fetched ${femaleUsers.length} female and ${maleUsers.length} male profiles`);
  
  // Convert to our schema
  console.log(`\n🔄 Converting to database schema...`);
  const userDocs = [];
  const profileDocs = [];
  
  for (const randomUser of [...femaleUsers, ...maleUsers]) {
    const { user, profile } = convertToUserProfile(randomUser);
    userDocs.push(user);
    profileDocs.push(profile);
  }
  
  console.log(`✅ Generated ${userDocs.length} user and profile documents`);
  
  if (DRY_RUN) {
    console.log(`\n🔍 DRY RUN - Sample 3 users:\n`);
    for (let i = 0; i < Math.min(3, userDocs.length); i++) {
      console.log(`${i + 1}. ${userDocs[i].name} (${profileDocs[i].gender}, ${profileDocs[i].age})`);
      console.log(`   ${profileDocs[i].location}`);
      console.log(`   Interests: ${profileDocs[i].interests.join(', ')}`);
      console.log(`   Photo: ${profileDocs[i].photos[0].substring(0, 60)}...`);
      console.log('');
    }
    console.log('✅ DRY RUN complete. Use --dry-run=false to insert into database.');
    return;
  }
  
  // Connect to MongoDB
  console.log(`\n📦 Connecting to MongoDB...`);
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
    
    // Create indexes
    console.log(`\n📑 Ensuring indexes...`);
    await usersCollection.createIndex({ email: 1 }, { unique: true, sparse: true });
    await usersCollection.createIndex({ id: 1 }, { unique: true });
    await usersCollection.createIndex({ demo: 1 });
    await profilesCollection.createIndex({ user_id: 1 }, { unique: true });
    await profilesCollection.createIndex({ id: 1 }, { unique: true });
    await profilesCollection.createIndex({ demo: 1 });
    await profilesCollection.createIndex({ gender: 1 });
    await profilesCollection.createIndex({ age: 1 });
    console.log('✅ Indexes created');
    
    // Insert in batches
    console.log(`\n💾 Inserting users (batches of 50)...`);
    const userBatchSize = 50;
    let totalUsersInserted = 0;
    
    for (let i = 0; i < userDocs.length; i += userBatchSize) {
      const batch = userDocs.slice(i, i + userBatchSize);
      try {
        const result = await usersCollection.insertMany(batch, { ordered: false });
        totalUsersInserted += result.insertedCount;
        console.log(`  Batch ${Math.floor(i / userBatchSize) + 1}: ${result.insertedCount} users`);
      } catch (err) {
        console.warn(`  ⚠️  Batch had some errors (likely duplicates): ${err.message}`);
      }
    }
    
    console.log(`✅ Inserted ${totalUsersInserted} users`);
    
    console.log(`\n💾 Inserting profiles (batches of 50)...`);
    let totalProfilesInserted = 0;
    
    for (let i = 0; i < profileDocs.length; i += userBatchSize) {
      const batch = profileDocs.slice(i, i + userBatchSize);
      try {
        const result = await profilesCollection.insertMany(batch, { ordered: false });
        totalProfilesInserted += result.insertedCount;
        console.log(`  Batch ${Math.floor(i / userBatchSize) + 1}: ${result.insertedCount} profiles`);
      } catch (err) {
        console.warn(`  ⚠️  Batch had some errors: ${err.message}`);
      }
    }
    
    console.log(`✅ Inserted ${totalProfilesInserted} profiles`);
    
    // Verification
    console.log(`\n🔍 Verification:`);
    const demoUsers = await usersCollection.countDocuments({ demo: true });
    const demoProfiles = await profilesCollection.countDocuments({ demo: true });
    const femaleProfiles = await profilesCollection.countDocuments({ demo: true, gender: 'female' });
    const maleProfiles = await profilesCollection.countDocuments({ demo: true, gender: 'male' });
    
    console.log(`  Demo users in DB: ${demoUsers}`);
    console.log(`  Demo profiles in DB: ${demoProfiles}`);
    console.log(`    - Female: ${femaleProfiles}`);
    console.log(`    - Male: ${maleProfiles}`);
    
    console.log(`\n📋 Sample 5 demo users:`);
    const samples = await usersCollection.find({ demo: true }).limit(5).toArray();
    for (const user of samples) {
      const profile = await profilesCollection.findOne({ user_id: user.id });
      console.log(`  - ${user.name} (${profile?.gender}, ${profile?.age}) from ${profile?.location}`);
    }
    
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  } finally {
    await client.close();
    console.log(`\n✅ MongoDB connection closed`);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('🎉 Demo user seeding complete!');
  console.log('='.repeat(60));
}

// Run
seedDemoUsers().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
