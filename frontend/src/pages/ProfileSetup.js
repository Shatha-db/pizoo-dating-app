import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { X, Plus, Camera } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProfileSetup = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    display_name: '',
    bio: '',
    date_of_birth: '',
    gender: '',
    height: '',
    looking_for: '',
    location: '',
    latitude: null,
    longitude: null,
    occupation: '',
    education: '',
    relationship_goals: '',
    smoking: '',
    drinking: '',
    has_children: null,
    wants_children: null
  });
  const [interests, setInterests] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [newInterest, setNewInterest] = useState('');
  const [newLanguage, setNewLanguage] = useState('');
  const [photos, setPhotos] = useState([]);
  const [photoUploading, setPhotoUploading] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);

  // طلب الموقع تلقائياً عند تحميل الصفحة
  useEffect(() => {
    getLocation();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const addInterest = () => {
    if (newInterest.trim() && !interests.includes(newInterest.trim())) {
      setInterests([...interests, newInterest.trim()]);
      setNewInterest('');
    }
  };

  const removeInterest = (interest) => {
    setInterests(interests.filter(i => i !== interest));
  };

  const addLanguage = () => {
    if (newLanguage.trim() && !languages.includes(newLanguage.trim())) {
      setLanguages([...languages, newLanguage.trim()]);
      setNewLanguage('');
    }
  };

  const removeLanguage = (language) => {
    setLanguages(languages.filter(l => l !== language));
  };

  const getLocation = () => {
    setLocationLoading(true);
    setError('');
    
    if (!navigator.geolocation) {
      setError('المتصفح لا يدعم تحديد الموقع');
      setLocationLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          // Use Nominatim (OpenStreetMap) for reverse geocoding - Free!
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&accept-language=ar`
          );
          const data = await response.json();
          
          // Get city and country
          const city = data.address.city || data.address.town || data.address.village || data.address.state;
          const country = data.address.country;
          const locationStr = `${city}, ${country}`;
          
          setFormData(prev => ({ ...prev, location: locationStr }));
        } catch (error) {
          console.error('Error getting location name:', error);
          // Fallback to coordinates
          setFormData(prev => ({ ...prev, location: `${latitude.toFixed(2)}, ${longitude.toFixed(2)}` }));
        } finally {
          setLocationLoading(false);
        }
      },
      (error) => {
        console.error('Error getting location:', error);
        setError('لم نتمكن من الحصول على موقعك. يرجى السماح بالوصول للموقع.');
        setLocationLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  const handleSubmit = async () => {
    setError('');

    if (!formData.display_name) {
      setError('يرجى إدخال اسم العرض');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/profile/create`, {
        ...formData,
        height: formData.height ? parseInt(formData.height) : null,
        interests,
        languages,
        photos
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      navigate('/home');
    } catch (error) {
      setError(error.response?.data?.detail || 'حدث خطأ أثناء إنشاء الملف');
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('حجم الصورة يجب أن يكون أقل من 10MB');
      return;
    }

    setPhotoUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('is_primary', photos.length === 0 ? 'true' : 'false');

      const response = await axios.post(`${API}/profile/photo/upload`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setPhotos([...photos, response.data.photo.url]);
      
      // Clear file input
      e.target.value = null;
    } catch (error) {
      console.error('Error uploading photo:', error);
      setError(error.response?.data?.detail || 'فشل رفع الصورة. حاول مرة أخرى');
    } finally {
      setPhotoUploading(false);
    }
  };

  const removePhoto = (index) => {
    setPhotos(photos.filter((_, i) => i !== index));
  };

  const nextStep = () => {
    if (step === 1 && !formData.display_name) {
      setError('يرجى إدخال اسم العرض');
      return;
    }
    setError('');
    setStep(step + 1);
  };

  const prevStep = () => {
    setError('');
    setStep(step - 1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-purple-50 flex items-center justify-center p-4" dir="rtl">
      <Card className="w-full max-w-2xl" data-testid="profile-setup-card">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl">أكمل ملفك الشخصي</CardTitle>
          <CardDescription>
            خطوة {step} من 4 - أخبرنا عن نفسك لنساعدك في إيجاد التطابق المثالي
          </CardDescription>
          <div className="flex gap-2 mt-4">
            <div className={`h-2 flex-1 rounded-full ${step >= 1 ? 'bg-pink-500' : 'bg-gray-200'}`} />
            <div className={`h-2 flex-1 rounded-full ${step >= 2 ? 'bg-pink-500' : 'bg-gray-200'}`} />
            <div className={`h-2 flex-1 rounded-full ${step >= 3 ? 'bg-pink-500' : 'bg-gray-200'}`} />
          </div>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Step 1: المعلومات الأساسية */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="display_name">اسمك أو اسمك المستعار *</Label>
                <Input
                  id="display_name"
                  name="display_name"
                  value={formData.display_name}
                  onChange={handleChange}
                  placeholder="ما الاسم الذي تريد أن يظهر للآخرين؟"
                  data-testid="display-name-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="bio">نبذة عنك</Label>
                <Textarea
                  id="bio"
                  name="bio"
                  value={formData.bio}
                  onChange={handleChange}
                  placeholder="أخبر الآخرين قليلاً عن نفسك..."
                  rows={4}
                  data-testid="bio-input"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date_of_birth">تاريخ الميلاد</Label>
                  <Input
                    id="date_of_birth"
                    name="date_of_birth"
                    type="date"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                    data-testid="dob-input"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="gender">الجنس</Label>
                  <Select value={formData.gender} onValueChange={(value) => handleSelectChange('gender', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">ذكر</SelectItem>
                      <SelectItem value="female">أنثى</SelectItem>
                      <SelectItem value="other">آخر</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="height">الطول (سم)</Label>
                <Input
                  id="height"
                  name="height"
                  type="number"
                  value={formData.height}
                  onChange={handleChange}
                  placeholder="170"
                  data-testid="height-input"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">الموقع</Label>
                <Input
                  id="location"
                  name="location"
                  value={formData.location || (locationLoading ? 'جاري تحديد موقعك...' : 'لم يتم تحديد الموقع')}
                  readOnly
                  data-testid="location-input"
                  className="bg-gray-50"
                />
                <p className="text-xs text-gray-500">
                  📍 يتم تحديد موقعك تلقائياً لإيجاد أشخاص قريبين منك
                </p>
              </div>
            </div>
          )}

          {/* Step 2: المعلومات الشخصية */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="occupation">المهنة</Label>
                <Input
                  id="occupation"
                  name="occupation"
                  value={formData.occupation}
                  onChange={handleChange}
                  placeholder="ماذا تعمل؟"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="education">التعليم</Label>
                <Input
                  id="education"
                  name="education"
                  value={formData.education}
                  onChange={handleChange}
                  placeholder="أعلى شهادة حصلت عليها"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="relationship_goals">ماذا تبحث عنه؟</Label>
                <Select value={formData.relationship_goals} onValueChange={(value) => handleSelectChange('relationship_goals', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="اختر..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="serious">علاقة جدية</SelectItem>
                    <SelectItem value="casual">علاقة عابرة</SelectItem>
                    <SelectItem value="friendship">صداقة</SelectItem>
                    <SelectItem value="not_sure">لست متأكد</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="smoking">التدخين</Label>
                  <Select value={formData.smoking} onValueChange={(value) => handleSelectChange('smoking', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="yes">نعم</SelectItem>
                      <SelectItem value="no">لا</SelectItem>
                      <SelectItem value="sometimes">أحياناً</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="drinking">الكحول</Label>
                  <Select value={formData.drinking} onValueChange={(value) => handleSelectChange('drinking', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="yes">نعم</SelectItem>
                      <SelectItem value="no">لا</SelectItem>
                      <SelectItem value="sometimes">أحياناً</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="has_children">لديك أطفال؟</Label>
                  <Select value={formData.has_children === null ? '' : formData.has_children.toString()} onValueChange={(value) => handleSelectChange('has_children', value === 'true')}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">نعم</SelectItem>
                      <SelectItem value="false">لا</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="wants_children">تريد أطفالاً؟</Label>
                  <Select value={formData.wants_children === null ? '' : formData.wants_children.toString()} onValueChange={(value) => handleSelectChange('wants_children', value === 'true')}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">نعم</SelectItem>
                      <SelectItem value="false">لا</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: الهوايات واللغات */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>الهوايات والاهتمامات</Label>
                <div className="flex gap-2">
                  <Input
                    value={newInterest}
                    onChange={(e) => setNewInterest(e.target.value)}
                    placeholder="أضف هواية (مثل: السفر، القراءة، الرياضة)"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addInterest())}
                  />
                  <Button type="button" onClick={addInterest} size="icon">
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {interests.map((interest, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {interest}
                      <X className="w-3 h-3 cursor-pointer" onClick={() => removeInterest(interest)} />
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>اللغات التي تتحدثها</Label>
                <div className="flex gap-2">
                  <Input
                    value={newLanguage}
                    onChange={(e) => setNewLanguage(e.target.value)}
                    placeholder="أضف لغة (مثل: العربية، الإنجليزية)"
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLanguage())}
                  />
                  <Button type="button" onClick={addLanguage} size="icon">
                    <Plus className="w-4 h-4" />
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {languages.map((language, index) => (
                    <Badge key={index} variant="secondary" className="gap-1">
                      {language}
                      <X className="w-3 h-3 cursor-pointer" onClick={() => removeLanguage(language)} />
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Step 4: الصور - الجميع هنا ليروك */}
          {step === 4 && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <h3 className="text-2xl font-bold mb-2">الجميع هنا ليروك 📸</h3>
                <p className="text-gray-600">أضف صورك لجذب التطابقات المثالية</p>
              </div>

              <div className="space-y-2">
                <Label>صورك الشخصية</Label>
                <div className="border-2 border-dashed border-pink-300 rounded-lg p-8 text-center bg-pink-50 hover:bg-pink-100 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoUpload}
                    className="hidden"
                    id="photo-upload"
                    disabled={photoUploading}
                  />
                  <label
                    htmlFor="photo-upload"
                    className="cursor-pointer flex flex-col items-center gap-3"
                  >
                    <Camera className="w-12 h-12 text-pink-500" />
                    <span className="text-lg font-medium text-gray-900">
                      {photoUploading ? 'جاري رفع الصورة...' : 'اضغط لإضافة صورة'}
                    </span>
                    <span className="text-sm text-gray-600">
                      الحد الأقصى: 5MB • يمكنك إضافة حتى 6 صور
                    </span>
                  </label>
                </div>
                
                {photos.length > 0 && (
                  <div className="grid grid-cols-3 gap-3 mt-6">
                    {photos.map((photo, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={photo}
                          alt={`صورة ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg shadow-md"
                        />
                        <button
                          type="button"
                          onClick={() => removePhoto(index)}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-8 h-8 flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-4 h-4" />
                        </button>
                        {index === 0 && (
                          <div className="absolute bottom-2 left-2 bg-pink-500 text-white text-xs px-2 py-1 rounded-full">
                            الصورة الرئيسية
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                  <p className="text-sm text-blue-900">
                    💡 <strong>نصيحة:</strong> الملفات الشخصية التي تحتوي على 3+ صور تحصل على تطابقات أكثر بنسبة 70%!
                  </p>
                </div>
                
                {photos.length === 0 && (
                  <p className="text-sm text-red-500 text-center mt-2">
                    ⚠️ يرجى إضافة صورة واحدة على الأقل للمتابعة
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex gap-4 mt-6">
            {step > 1 && (
              <Button type="button" variant="outline" onClick={prevStep} className="flex-1">
                السابق
              </Button>
            )}
            {step < 4 ? (
              <Button type="button" onClick={nextStep} className="flex-1">
                التالي
              </Button>
            ) : (
              <Button 
                type="button" 
                onClick={handleSubmit} 
                disabled={loading || photos.length === 0} 
                className="flex-1"
              >
                {loading ? 'جاري الحفظ...' : 'إنهاء وابدأ الاكتشاف'}
              </Button>
            )}
          </div>

          <p className="text-xs text-center text-gray-500 mt-4">
            يمكنك تعديل ملفك الشخصي في أي وقت لاحقاً
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfileSetup;
