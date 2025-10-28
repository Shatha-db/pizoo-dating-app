import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from 'react-i18next';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ArrowRight, Check, Zap, Star, Crown } from 'lucide-react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Premium = () => {
  const navigate = useNavigate();
  const { token } = useAuth();
  const { t } = useTranslation('premium');
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [selectedDuration, setSelectedDuration] = useState('1month');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${API}/premium/plans`);
      setPlans(response.data.plans);
      if (response.data.plans.length > 0) {
        setSelectedPlan(response.data.plans[0].tier);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSubscribe = async () => {
    if (!selectedPlan) return;
    
    setLoading(true);
    try {
      const response = await axios.post(
        `${API}/premium/subscribe?tier=${selectedPlan}&duration=${selectedDuration}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      alert('🎉 ' + response.data.message);
      navigate('/home');
    } catch (error) {
      console.error('Error:', error);
      alert('حدث خطأ أثناء الاشتراك');
    } finally {
      setLoading(false);
    }
  };

  const currentPlan = plans.find(p => p.tier === selectedPlan);
  const currentPricing = currentPlan?.pricing?.find(p => p.duration === selectedDuration);

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50 to-pink-50 pb-10" dir="rtl">
      {/* Header */}
      <header className="bg-gradient-to-r from-yellow-400 via-orange-400 to-pink-400 text-white p-6">
        <button onClick={() => navigate(-1)} className="mb-4">
          <ArrowRight className="w-6 h-6" />
        </button>
        <h1 className="text-3xl font-bold mb-2">Pizoo Premium 💎</h1>
        <p className="text-white/90">افتح جميع المميزات واحصل على تجربة مواعدة أفضل</p>
      </header>

      <main className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Free vs Premium Comparison */}
        <Card className="p-6 bg-gradient-to-br from-white to-gray-50">
          <h3 className="text-2xl font-bold mb-6 text-center">قارن الخطط</h3>
          <div className="grid md:grid-cols-3 gap-4">
            {/* Free */}
            <div className="text-center p-4 border-2 border-gray-200 rounded-lg">
              <div className="text-4xl mb-2">🆓</div>
              <h4 className="font-bold text-lg mb-3">مجاني</h4>
              <div className="space-y-2 text-sm text-gray-600">
                <p>✅ 12 إعجاب / أسبوع</p>
                <p>✅ 10 رسائل / أسبوع</p>
                <p>❌ مطابقات محدودة</p>
                <p>❌ لا يمكن معرفة من أعجب بك</p>
              </div>
            </div>

            {/* Gold */}
            <div className="text-center p-4 border-4 border-yellow-400 rounded-lg bg-gradient-to-br from-yellow-50 to-orange-50 relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-yellow-400 text-white text-xs px-3 py-1 rounded-full font-bold">
                {t('mostPopular')}
              </div>
              <div className="text-4xl mb-2">⭐</div>
              <h4 className="font-bold text-lg mb-3">Gold</h4>
              <div className="space-y-2 text-sm">
                <p>✅ إعجابات غير محدودة</p>
                <p>✅ رسائل غير محدودة</p>
                <p>✅ معرفة من أعجب بك</p>
                <p>✅ 5 سوبر لايك يومياً</p>
                <p>✅ تراجع غير محدود</p>
              </div>
            </div>

            {/* Platinum */}
            <div className="text-center p-4 border-4 border-purple-400 rounded-lg bg-gradient-to-br from-purple-50 to-pink-50">
              <div className="text-4xl mb-2">👑</div>
              <h4 className="font-bold text-lg mb-3">Platinum</h4>
              <div className="space-y-2 text-sm">
                <p>✅ كل مميزات Gold</p>
                <p>✅ رسائلك تُقرأ أولاً</p>
                <p>✅ معرفة من شاهد بروفايلك</p>
                <p>{t('freeBoost')}</p>
                <p>{t('hideAds')}</p>
                <p>✅ أولوية في الدعم</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Plan Selection */}
        <div className="grid md:grid-cols-2 gap-4">
          {plans.map((plan) => (
            <Card
              key={plan.tier}
              className={`p-6 cursor-pointer transition-all ${
                selectedPlan === plan.tier
                  ? 'ring-4 ring-yellow-400 bg-gradient-to-br from-yellow-50 to-orange-50'
                  : 'hover:shadow-lg'
              }`}
              onClick={() => setSelectedPlan(plan.tier)}
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {plan.tier === 'gold' ? (
                      <Zap className="w-6 h-6 text-yellow-500" />
                    ) : (
                      <Crown className="w-6 h-6 text-purple-500" />
                    )}
                    <h3 className="text-2xl font-bold">{plan.name}</h3>
                  </div>
                  <p className="text-gray-600">{plan.description}</p>
                </div>
                {selectedPlan === plan.tier && (
                  <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                    <Check className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>

              <div className="space-y-2">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center gap-2 text-sm">
                    <div className="w-5 h-5 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <Check className="w-3 h-3 text-white" />
                    </div>
                    <span>{feature}</span>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>

        {/* Duration Selection */}
        {currentPlan && (
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-4">اختر المدة</h3>
            <div className="space-y-3">
              {currentPlan.pricing.map((price) => {
                const durationLabels = {
                  '1week': t('monthDuration.1week'),
                  '1month': t('monthDuration.1month'),
                  '3months': t('monthDuration.3months'),
                  '6months': t('monthDuration.6months'),
                  '1year': t('monthDuration.1year')
                };

                const perMonth = price.duration === '1week'
                  ? (price.price * 4).toFixed(2)
                  : price.duration === '1month'
                  ? price.price
                  : price.duration === '3months'
                  ? (price.price / 3).toFixed(2)
                  : price.duration === '6months'
                  ? (price.price / 6).toFixed(2)
                  : (price.price / 12).toFixed(2);

                const savings = price.duration !== '1week' && price.duration !== '1month'
                  ? Math.round(((currentPlan.pricing.find(p => p.duration === '1month')?.price * (price.duration === '3months' ? 3 : price.duration === '6months' ? 6 : 12) - price.price) / currentPlan.pricing.find(p => p.duration === '1month')?.price * (price.duration === '3months' ? 3 : price.duration === '6months' ? 6 : 12)) * 100)
                  : 0;

                return (
                  <div
                    key={price.duration}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedDuration === price.duration
                        ? 'border-yellow-400 bg-yellow-50'
                        : 'border-gray-200 hover:border-yellow-300'
                    }`}
                    onClick={() => setSelectedDuration(price.duration)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-lg">{durationLabels[price.duration]}</span>
                          {savings > 0 && (
                            <span className="bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                              وفّر {savings}%
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">
                          {perMonth} {price.currency} {t('perMonth')}
                        </p>
                      </div>
                      <div className="text-left">
                        <div className="text-2xl font-bold">{price.price}</div>
                        <div className="text-sm text-gray-600">{price.currency}</div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        )}

        {/* Subscribe Button */}
        <Card className="p-6 bg-gradient-to-r from-yellow-400 to-orange-400">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-2">
              {currentPricing?.price} {currentPricing?.currency}
            </h3>
            <p className="text-white/90 text-sm mb-4">
              سيتم تجديد الاشتراك تلقائياً • يمكن الإلغاء في أي وقت
            </p>
            <Button
              onClick={handleSubscribe}
              disabled={loading}
              className="w-full bg-white text-black hover:bg-gray-100 font-bold text-lg py-6"
            >
              {loading ? 'جاري المعالجة...' : 'اشترك الآن'}
            </Button>
          </div>
        </Card>

        {/* Note */}
        <p className="text-center text-sm text-gray-600">
          💡 هذا نظام تجريبي - لا يوجد دفع حقيقي
        </p>
      </main>
    </div>
  );
};

export default Premium;
