import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select } from '../components/ui/select';
import { ArrowRight, Camera, X, Plus, Check, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { uploadImageToCloudinary, compressImage } from '../utils/cloudinaryUpload';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EditProfile = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploadingPhotos, setUploadingPhotos] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [activeTab, setActiveTab] = useState('edit'); // 'edit' or 'preview'
  const [toast, setToast] = useState(null);
  
  // Profile data
  const [photos, setPhotos] = useState(Array(9).fill(null));
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [gender, setGender] = useState('');
  const [height, setHeight] = useState('');
  const [occupation, setOccupation] = useState('');
  const [education, setEducation] = useState('');
  const [location, setLocation] = useState('');
  
  // Additional fields like Tinder
  const [zodiacSign, setZodiacSign] = useState('');
  const [languages, setLanguages] = useState([]);
  const [newLanguage, setNewLanguage] = useState('');
  const [relationshipGoals, setRelationshipGoals] = useState('');
  const [familyPlans, setFamilyPlans] = useState('');
  const [hasChildren, setHasChildren] = useState('');
  const [wantsChildren, setWantsChildren] = useState('');
  const [personalityType, setPersonalityType] = useState('');
  const [communicationStyle, setCommunicationStyle] = useState('');
  const [loveStyle, setLoveStyle] = useState('');
  const [pets, setPets] = useState('');
  const [drinking, setDrinking] = useState('');
  const [smoking, setSmoking] = useState('');
  const [exercise, setExercise] = useState('');
  const [dietaryPreference, setDietaryPreference] = useState('');
  const [interests, setInterests] = useState([]);
  const [newInterest, setNewInterest] = useState('');
  
  // New Tinder-like fields
  const [school, setSchool] = useState('');
  const [company, setCompany] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [livingIn, setLivingIn] = useState('');
  const [hometown, setHometown] = useState('');
  const [genderIdentity, setGenderIdentity] = useState('');
  const [showGender, setShowGender] = useState(true);
  const [sexualOrientation, setSexualOrientation] = useState('');
  const [showOrientation, setShowOrientation] = useState(true);
  const [sleepingHabits, setSleepingHabits] = useState('');
  const [socialMedia, setSocialMedia] = useState('');
  const [vaccinated, setVaccinated] = useState('');
  const [religion, setReligion] = useState('');
  const [politicalViews, setPoliticalViews] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/profile/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const profile = response.data;
      if (profile) {
        setPhotos([...(profile.photos || []), ...Array(9 - (profile.photos?.length || 0)).fill(null)]);
        setDisplayName(profile.display_name || '');
        setBio(profile.bio || '');
        setDateOfBirth(profile.date_of_birth || '');
        setGender(profile.gender || '');
        setHeight(profile.height || '');
        setOccupation(profile.occupation || '');
        setEducation(profile.education || '');
        setLocation(profile.location || '');
        setZodiacSign(profile.zodiac_sign || '');
        setLanguages(profile.languages || []);
        setRelationshipGoals(profile.relationship_goals || '');
        setFamilyPlans(profile.family_plans || '');
        setHasChildren(profile.has_children ? 'yes' : 'no');
        setWantsChildren(profile.wants_children ? 'yes' : 'no');
        setPersonalityType(profile.personality_type || '');
        setCommunicationStyle(profile.communication_style || '');
        setLoveStyle(profile.love_style || '');
        setPets(profile.pets || '');
        setDrinking(profile.drinking || '');
        setSmoking(profile.smoking || '');
        setExercise(profile.exercise || '');
        setDietaryPreference(profile.dietary_preference || '');
        setInterests(profile.interests || []);
        
        // New fields
        setSchool(profile.school || '');
        setCompany(profile.company || '');
        setJobTitle(profile.job_title || '');
        setLivingIn(profile.living_in || location || '');
        setHometown(profile.hometown || '');
        setGenderIdentity(profile.gender_identity || '');
        setShowGender(profile.show_gender !== false);
        setSexualOrientation(profile.sexual_orientation || '');
        setShowOrientation(profile.show_orientation !== false);
        setSleepingHabits(profile.sleeping_habits || '');
        setSocialMedia(profile.social_media || '');
        setVaccinated(profile.vaccinated || '');
        setReligion(profile.religion || '');
        setPoliticalViews(profile.political_views || '');
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = (index, event) => {
    const file = event.target.files[0];
    if (file) {
      // In production, upload to server/cloud
      // For now, use FileReader for preview
      const reader = new FileReader();
      reader.onloadend = () => {
        const newPhotos = [...photos];
        newPhotos[index] = reader.result;
        setPhotos(newPhotos);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemovePhoto = (index) => {
    const newPhotos = [...photos];
    newPhotos[index] = null;
    // Shift photos to fill gap
    const filteredPhotos = newPhotos.filter(p => p !== null);
    setPhotos([...filteredPhotos, ...Array(9 - filteredPhotos.length).fill(null)]);
  };

  const handleAddLanguage = () => {
    if (newLanguage.trim() && !languages.includes(newLanguage.trim())) {
      setLanguages([...languages, newLanguage.trim()]);
      setNewLanguage('');
    }
  };

  const handleRemoveLanguage = (lang) => {
    setLanguages(languages.filter(l => l !== lang));
  };

  const handleAddInterest = () => {
    if (newInterest.trim() && !interests.includes(newInterest.trim())) {
      setInterests([...interests, newInterest.trim()]);
      setNewInterest('');
    }
  };

  const handleRemoveInterest = (interest) => {
    setInterests(interests.filter(i => i !== interest));
  };

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const profileData = {
        display_name: displayName,
        bio: bio,
        date_of_birth: dateOfBirth,
        gender: gender,
        height: parseInt(height) || null,
        occupation: occupation,
        education: education,
        location: location,
        photos: photos.filter(p => p !== null),
        zodiac_sign: zodiacSign,
        languages: languages,
        relationship_goals: relationshipGoals,
        family_plans: familyPlans,
        has_children: hasChildren === 'yes',
        wants_children: wantsChildren === 'yes',
        personality_type: personalityType,
        communication_style: communicationStyle,
        love_style: loveStyle,
        pets: pets,
        drinking: drinking,
        smoking: smoking,
        exercise: exercise,
        dietary_preference: dietaryPreference,
        interests: interests,
        
        // New fields
        school: school,
        company: company,
        job_title: jobTitle,
        living_in: livingIn,
        hometown: hometown,
        gender_identity: genderIdentity,
        show_gender: showGender,
        sexual_orientation: sexualOrientation,
        show_orientation: showOrientation,
        sleeping_habits: sleepingHabits,
        social_media: socialMedia,
        vaccinated: vaccinated,
        religion: religion,
        political_views: politicalViews
      };

      await axios.put(`${API}/profile/update`, profileData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      showToast('تم حفظ التغييرات بنجاح! ✅');
      setTimeout(() => navigate('/profile'), 1500);
    } catch (error) {
      console.error('Error saving profile:', error);
      showToast('حدث خطأ أثناء الحفظ', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-pink-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 ${
          toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'
        } text-white px-6 py-3 rounded-full z-50 shadow-lg flex items-center gap-2`}>
          {toast.type === 'error' ? <AlertCircle className="w-5 h-5" /> : <Check className="w-5 h-5" />}
          {toast.message}
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm p-4 sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="p-2 hover:bg-gray-100 rounded-full"
          >
            <ArrowRight className="w-6 h-6" />
          </button>
          <h1 className="text-xl font-bold">تعديل معلومات</h1>
          <Button
            onClick={handleSave}
            disabled={saving}
            className="bg-pink-500 hover:bg-pink-600 text-white"
            size="sm"
          >
            {saving ? 'جاري الحفظ...' : 'حفظ'}
          </Button>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 sticky top-16 z-10">
        <div className="max-w-2xl mx-auto flex">
          <button
            onClick={() => setActiveTab('edit')}
            className={`flex-1 py-3 text-center font-medium border-b-2 transition-colors ${
              activeTab === 'edit'
                ? 'border-pink-500 text-pink-500'
                : 'border-transparent text-gray-500'
            }`}
          >
            تعديل
          </button>
          <button
            onClick={() => setActiveTab('preview')}
            className={`flex-1 py-3 text-center font-medium border-b-2 transition-colors ${
              activeTab === 'preview'
                ? 'border-pink-500 text-pink-500'
                : 'border-transparent text-gray-500'
            }`}
          >
            معاينة
          </button>
        </div>
      </div>

      <main className="max-w-2xl mx-auto p-4 pb-20">
        {activeTab === 'edit' ? (
          <div className="space-y-6">
            {/* Media Section */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-bold text-lg">الوسائط</h2>
                <span className="text-sm text-gray-600">
                  {photos.filter(p => p !== null).length}/9
                </span>
              </div>
              
              <div className="grid grid-cols-3 gap-3">
                {photos.map((photo, index) => (
                  <div key={index} className="relative aspect-square">
                    {photo ? (
                      <>
                        <img
                          src={photo}
                          alt={`صورة ${index + 1}`}
                          className="w-full h-full object-cover rounded-lg"
                        />
                        <button
                          onClick={() => handleRemovePhoto(index)}
                          className="absolute top-1 left-1 bg-red-500 text-white p-1 rounded-full hover:bg-red-600"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </>
                    ) : (
                      <label className="w-full h-full border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center cursor-pointer hover:border-pink-400 hover:bg-pink-50 transition-colors">
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handlePhotoUpload(index, e)}
                        />
                        <Plus className="w-8 h-8 text-gray-400" />
                      </label>
                    )}
                  </div>
                ))}
              </div>

              <p className="text-sm text-gray-600 mt-4 text-center">
                أضف ما يصل إلى 9 صور. استمتع بتذوات عند تشاركك لشخصيتك.
              </p>
            </Card>

            {/* Basic Info */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">المعلومات الأساسية</h2>
              
              <div>
                <label className="block text-sm font-medium mb-2">الاسم</label>
                <Input
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="اسمك"
                  maxLength={50}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">نبذة عني</label>
                <Textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  placeholder="اكتب نبذة قصيرة عنك..."
                  rows={4}
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 mt-1">{bio.length}/500</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">تاريخ الميلاد</label>
                <Input
                  type="date"
                  value={dateOfBirth}
                  onChange={(e) => setDateOfBirth(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">الجنس</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="male">ذكر</option>
                  <option value="female">أنثى</option>
                  <option value="other">آخر</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">الطول (سم)</label>
                <Input
                  type="number"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  placeholder="مثال: 175"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">الوظيفة</label>
                <Input
                  value={occupation}
                  onChange={(e) => setOccupation(e.target.value)}
                  placeholder="مثال: مهندس برمجيات"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">الموقع</label>
                <Input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="مثال: دبي، الإمارات"
                />
              </div>
            </Card>

            {/* About Me Section - like Tinder */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">عني</h2>
              
              <div>
                <label className="block text-sm font-medium mb-2">🏫 المدرسة</label>
                <Input
                  value={school}
                  onChange={(e) => setSchool(e.target.value)}
                  placeholder="أضف مدرسة"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🏢 الشركة</label>
                <Input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="أضف شركة"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">💼 المسمى الوظيفي</label>
                <Input
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="أضف مسمى وظيفي"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🏙️ اعيش في</label>
                <Input
                  value={livingIn}
                  onChange={(e) => setLivingIn(e.target.value)}
                  placeholder="أضف مدينة"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🏡 مسقط الرأس</label>
                <Input
                  value={hometown}
                  onChange={(e) => setHometown(e.target.value)}
                  placeholder="أضف مسقط رأس"
                />
              </div>
            </Card>

            {/* Gender & Orientation */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">الهوية الجنسية والتوجه</h2>

              <div>
                <label className="block text-sm font-medium mb-2">الهوية الجنسية</label>
                <select
                  value={genderIdentity}
                  onChange={(e) => setGenderIdentity(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2 mb-2"
                >
                  <option value="">اختر...</option>
                  <option value="woman">امرأة</option>
                  <option value="man">رجل</option>
                  <option value="non-binary">غير ثنائي</option>
                  <option value="trans-woman">امرأة متحولة</option>
                  <option value="trans-man">رجل متحول</option>
                  <option value="prefer-not-to-say">أفضل عدم الإفصاح</option>
                </select>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={showGender}
                    onChange={(e) => setShowGender(e.target.checked)}
                    className="rounded"
                  />
                  <span>إظهار الهوية الجنسية في ملفي الشخصي</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">التوجه الجنسي</label>
                <select
                  value={sexualOrientation}
                  onChange={(e) => setSexualOrientation(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2 mb-2"
                >
                  <option value="">اختر...</option>
                  <option value="straight">مغاير</option>
                  <option value="gay">مثلي</option>
                  <option value="lesbian">مثلية</option>
                  <option value="bisexual">ثنائي الجنس</option>
                  <option value="asexual">لاجنسي</option>
                  <option value="pansexual">كلي الجنس</option>
                  <option value="queer">كوير</option>
                  <option value="questioning">مستكشف</option>
                </select>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={showOrientation}
                    onChange={(e) => setShowOrientation(e.target.checked)}
                    className="rounded"
                  />
                  <span>إظهار التوجه الجنسي في ملفي الشخصي</span>
                </label>
              </div>
            </Card>

            {/* Interests */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">الاهتمامات</h2>
              
              <div className="flex gap-2">
                <Input
                  value={newInterest}
                  onChange={(e) => setNewInterest(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddInterest()}
                  placeholder="أضف اهتمام..."
                />
                <Button onClick={handleAddInterest} size="sm">
                  إضافة
                </Button>
              </div>

              <div className="flex flex-wrap gap-2">
                {interests.map((interest, index) => (
                  <span
                    key={index}
                    className="bg-pink-100 text-pink-700 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                  >
                    {interest}
                    <button onClick={() => handleRemoveInterest(interest)}>
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </Card>

            {/* Languages */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">اللغات التي اعرفها</h2>
              
              <div className="flex gap-2">
                <Input
                  value={newLanguage}
                  onChange={(e) => setNewLanguage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddLanguage()}
                  placeholder="أضف لغة..."
                />
                <Button onClick={handleAddLanguage} size="sm">
                  إضافة
                </Button>
              </div>

              <div className="flex flex-wrap gap-2">
                {languages.map((lang, index) => (
                  <span
                    key={index}
                    className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm flex items-center gap-2"
                  >
                    {lang}
                    <button onClick={() => handleRemoveLanguage(lang)}>
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            </Card>

            {/* Lifestyle */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">أسلوب الحياة</h2>

              <div>
                <label className="block text-sm font-medium mb-2">🐾 الحيوانات الأليفة</label>
                <select
                  value={pets}
                  onChange={(e) => setPets(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="dog">كلب</option>
                  <option value="cat">قطة</option>
                  <option value="both">كلاهما</option>
                  <option value="other">حيوان آخر</option>
                  <option value="none">لا يوجد</option>
                  <option value="want">أريد حيوان أليف</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🍷 أشرب</label>
                <select
                  value={drinking}
                  onChange={(e) => setDrinking(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="yes">نعم</option>
                  <option value="no">لا</option>
                  <option value="socially">اجتماعياً</option>
                  <option value="occasionally">أحياناً</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🚬 كم مرة تُدخن عادةً؟</label>
                <select
                  value={smoking}
                  onChange={(e) => setSmoking(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="yes">نعم</option>
                  <option value="no">لا</option>
                  <option value="sometimes">أحياناً</option>
                  <option value="socially">اجتماعياً</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">💪 التمرين</label>
                <select
                  value={exercise}
                  onChange={(e) => setExercise(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="active">نشيط</option>
                  <option value="sometimes">أحياناً</option>
                  <option value="rarely">نادراً</option>
                  <option value="never">أبداً</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🥗 التفضيل الغذائي</label>
                <select
                  value={dietaryPreference}
                  onChange={(e) => setDietaryPreference(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="vegan">نباتي صرف</option>
                  <option value="vegetarian">نباتي</option>
                  <option value="pescatarian">يتناول السمك</option>
                  <option value="halal">حلال</option>
                  <option value="kosher">كوشير</option>
                  <option value="omnivore">يأكل كل شيء</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">😴 عادات النوم</label>
                <select
                  value={sleepingHabits}
                  onChange={(e) => setSleepingHabits(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="early-bird">صحوة مبكرة</option>
                  <option value="night-owl">بومة ليلية</option>
                  <option value="in-between">بينهما</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">📱 التواصل الاجتماعي</label>
                <select
                  value={socialMedia}
                  onChange={(e) => setSocialMedia(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="influencer">مؤثر</option>
                  <option value="active">نشيط</option>
                  <option value="passive">سلبي</option>
                  <option value="off-the-grid">بعيد عن الشبكات</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">💉 حالة اللقاح</label>
                <select
                  value={vaccinated}
                  onChange={(e) => setVaccinated(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="vaccinated">ملقح</option>
                  <option value="not-vaccinated">غير ملقح</option>
                  <option value="prefer-not-to-say">أفضل عدم الإفصاح</option>
                </select>
              </div>
            </Card>

            {/* Beliefs */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">المعتقدات</h2>

              <div>
                <label className="block text-sm font-medium mb-2">🙏 الدين</label>
                <select
                  value={religion}
                  onChange={(e) => setReligion(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="muslim">مسلم</option>
                  <option value="christian">مسيحي</option>
                  <option value="jewish">يهودي</option>
                  <option value="hindu">هندوسي</option>
                  <option value="buddhist">بوذي</option>
                  <option value="atheist">ملحد</option>
                  <option value="agnostic">لا أدري</option>
                  <option value="spiritual">روحاني</option>
                  <option value="other">آخر</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🗳️ الآراء السياسية</label>
                <select
                  value={politicalViews}
                  onChange={(e) => setPoliticalViews(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="liberal">ليبرالي</option>
                  <option value="moderate">معتدل</option>
                  <option value="conservative">محافظ</option>
                  <option value="not-political">غير مهتم بالسياسة</option>
                  <option value="prefer-not-to-say">أفضل عدم الإفصاح</option>
                </select>
              </div>
            </Card>

            {/* Relationship Goals */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">أهداف العلاقة</h2>

              <div>
                <label className="block text-sm font-medium mb-2">👫 أبحث عن</label>
                <select
                  value={relationshipGoals}
                  onChange={(e) => setRelationshipGoals(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="long-term-partner">شريك لفترة طويلة</option>
                  <option value="long-term-open">علاقة طويلة، منفتح على قصيرة</option>
                  <option value="short-term-open">قصيرة، منفتح على طويلة</option>
                  <option value="short-term">علاقة قصيرة الأمد</option>
                  <option value="new-friends">أصدقاء جدد</option>
                  <option value="figuring-out">ما زلت أفكر</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">👶 هل لديك أطفال؟</label>
                <select
                  value={hasChildren}
                  onChange={(e) => setHasChildren(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="yes">نعم لدي</option>
                  <option value="no">لا ليس لدي</option>
                  <option value="prefer-not-to-say">أفضل عدم الإفصاح</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🍼 هل تريد أطفال؟</label>
                <select
                  value={wantsChildren}
                  onChange={(e) => setWantsChildren(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="yes">نعم أريد</option>
                  <option value="no">لا أريد</option>
                  <option value="maybe">ربما</option>
                  <option value="open-to-children">منفتح على الأطفال</option>
                  <option value="not-sure">غير متأكد</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">👪 خطط العائلة</label>
                <select
                  value={familyPlans}
                  onChange={(e) => setFamilyPlans(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="want-children">أريد أطفال</option>
                  <option value="dont-want-children">لا أريد أطفال</option>
                  <option value="open-to-children">منفتح على الأطفال</option>
                  <option value="not-sure">غير متأكد بعد</option>
                </select>
              </div>
            </Card>

            {/* Additional Details */}
            <Card className="p-6 space-y-4">
              <h2 className="font-bold text-lg">المزيد عني</h2>

              <div>
                <label className="block text-sm font-medium mb-2">⭐ البرج</label>
                <select
                  value={zodiacSign}
                  onChange={(e) => setZodiacSign(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="aries">الحمل</option>
                  <option value="taurus">الثور</option>
                  <option value="gemini">الجوزاء</option>
                  <option value="cancer">السرطان</option>
                  <option value="leo">الأسد</option>
                  <option value="virgo">العذراء</option>
                  <option value="libra">الميزان</option>
                  <option value="scorpio">العقرب</option>
                  <option value="sagittarius">القوس</option>
                  <option value="capricorn">الجدي</option>
                  <option value="aquarius">الدلو</option>
                  <option value="pisces">الحوت</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🎓 المستوى الدراسي</label>
                <select
                  value={education}
                  onChange={(e) => setEducation(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="high-school">ثانوية عامة</option>
                  <option value="bachelors">بكالوريوس</option>
                  <option value="masters">ماجستير</option>
                  <option value="phd">دكتوراه</option>
                  <option value="trade">مهني</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">🧩 نوع الشخصية</label>
                <Input
                  value={personalityType}
                  onChange={(e) => setPersonalityType(e.target.value)}
                  placeholder="مثال: INTJ, ENFP..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">💬 وسيلة التواصل</label>
                <select
                  value={communicationStyle}
                  onChange={(e) => setCommunicationStyle(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="frequent">متكرر</option>
                  <option value="moderate">معتدل</option>
                  <option value="minimal">قليل</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">❤️ أسلوب الحب</label>
                <select
                  value={loveStyle}
                  onChange={(e) => setLoveStyle(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                >
                  <option value="">اختر...</option>
                  <option value="thoughtful">متأمل</option>
                  <option value="romantic">رومانسي</option>
                  <option value="playful">مرح</option>
                  <option value="practical">عملي</option>
                </select>
              </div>
            </Card>

            {/* Save Button */}
            <Button
              onClick={handleSave}
              disabled={saving}
              className="w-full bg-gradient-to-r from-pink-500 to-purple-500 text-white py-6 text-lg"
            >
              {saving ? 'جاري الحفظ...' : 'حفظ التغييرات'}
            </Button>
          </div>
        ) : (
          /* Preview Tab */
          <div className="space-y-6">
            <Card className="overflow-hidden">
              <div className="aspect-[3/4] relative bg-gradient-to-br from-pink-300 to-purple-300">
                {photos[0] ? (
                  <img
                    src={photos[0]}
                    alt={displayName}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-8xl">
                    ❤️
                  </div>
                )}
              </div>

              <div className="p-6">
                <h2 className="text-2xl font-bold mb-2">
                  {displayName || 'اسمك'}
                  {dateOfBirth && `, ${new Date().getFullYear() - new Date(dateOfBirth).getFullYear()}`}
                </h2>
                
                {location && <p className="text-gray-600 mb-2">📍 {location}</p>}
                {occupation && <p className="text-gray-600 mb-4">💼 {occupation}</p>}
                {bio && <p className="text-gray-700 mb-4">{bio}</p>}

                {interests.length > 0 && (
                  <div className="mb-4">
                    <h3 className="font-bold mb-2">الاهتمامات</h3>
                    <div className="flex flex-wrap gap-2">
                      {interests.map((interest, i) => (
                        <span key={i} className="bg-pink-100 text-pink-700 px-3 py-1 rounded-full text-sm">
                          {interest}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {languages.length > 0 && (
                  <div>
                    <h3 className="font-bold mb-2">اللغات</h3>
                    <div className="flex flex-wrap gap-2">
                      {languages.map((lang, i) => (
                        <span key={i} className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm">
                          {lang}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
};

export default EditProfile;
