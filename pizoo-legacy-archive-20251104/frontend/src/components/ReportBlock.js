import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Textarea } from './ui/textarea';
import { ArrowRight, Flag, Ban, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ReportUser = ({ userId, userName, onClose }) => {
  const { token } = useAuth();
  const [reason, setReason] = useState('');
  const [selectedReason, setSelectedReason] = useState('');
  const [loading, setLoading] = useState(false);

  const reportReasons = [
    'محتوى غير لائق',
    'سلوك مسيء',
    'انتحال شخصية',
    'محاولة احتيال',
    'صور غير لائقة',
    'رسائل مزعجة',
    'آخر (حدد في التفاصيل)'
  ];

  const handleReport = async () => {
    if (!selectedReason) {
      toast.error('الرجاء اختيار سبب الإبلاغ');
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${API}/report`,
        {
          reported_user_id: userId,
          reason: selectedReason,
          details: reason
        },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast.success('تم الإبلاغ بنجاح. شكراً لمساعدتنا في الحفاظ على أمان المجتمع');
      onClose();
    } catch (error) {
      console.error('Error reporting user:', error);
      toast.error('فشل الإبلاغ. حاول مرة أخرى');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" dir="rtl">
      <Card className="w-full max-w-md p-6 dark:bg-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <Flag className="w-6 h-6 text-red-500" />
          <h2 className="text-xl font-bold dark:text-gray-900">الإبلاغ عن {userName}</h2>
        </div>

        <div className="space-y-4">
          {/* Reason selection */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-gray-900">
              سبب الإبلاغ <span className="text-red-500">*</span>
            </label>
            <div className="space-y-2">
              {reportReasons.map((reasonOption) => (
                <label
                  key={reasonOption}
                  className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-pink-50 dark:hover:bg-pink-100 transition-colors"
                >
                  <input
                    type="radio"
                    name="reason"
                    value={reasonOption}
                    checked={selectedReason === reasonOption}
                    onChange={(e) => setSelectedReason(e.target.value)}
                    className="w-4 h-4 text-pink-600"
                  />
                  <span className="text-sm dark:text-gray-900">{reasonOption}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Additional details */}
          <div>
            <label className="block text-sm font-medium mb-2 dark:text-gray-900">
              تفاصيل إضافية (اختياري)
            </label>
            <Textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="أضف أي تفاصيل إضافية..."
              rows={4}
              className="w-full dark:bg-white dark:text-gray-900"
            />
          </div>

          {/* Warning message */}
          <div className="bg-yellow-50 dark:bg-yellow-100 border border-yellow-200 rounded-lg p-3 flex gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
            <p className="text-sm text-yellow-800">
              الإبلاغات الكاذبة قد تؤدي إلى تعليق حسابك. سنراجع الإبلاغ خلال 24 ساعة.
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3">
            <Button
              onClick={onClose}
              variant="outline"
              className="flex-1"
              disabled={loading}
            >
              إلغاء
            </Button>
            <Button
              onClick={handleReport}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white"
              disabled={loading || !selectedReason}
            >
              {loading ? 'جاري الإرسال...' : 'إرسال الإبلاغ'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

const BlockUser = ({ userId, userName, onBlock, onClose }) => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);

  const handleBlock = async () => {
    setLoading(true);
    try {
      await axios.post(
        `${API}/block`,
        { blocked_user_id: userId },
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      toast.success(`تم حظر ${userName} بنجاح`);
      if (onBlock) onBlock();
      onClose();
    } catch (error) {
      console.error('Error blocking user:', error);
      toast.error('فشل الحظر. حاول مرة أخرى');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" dir="rtl">
      <Card className="w-full max-w-md p-6 dark:bg-gray-200">
        <div className="flex items-center gap-3 mb-4">
          <Ban className="w-6 h-6 text-red-500" />
          <h2 className="text-xl font-bold dark:text-gray-900">حظر {userName}؟</h2>
        </div>

        <div className="space-y-4">
          <p className="text-gray-700 dark:text-gray-800">
            هل أنت متأكد أنك تريد حظر هذا المستخدم؟
          </p>

          <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-700">
            <li>• لن يتمكن من رؤية بروفايلك</li>
            <li>• لن تتمكنوا من التواصل مع بعض</li>
            <li>• سيتم إلغاء التطابق إن وجد</li>
            <li>• يمكنك إلغاء الحظر لاحقاً من الإعدادات</li>
          </ul>

          <div className="flex gap-3">
            <Button
              onClick={onClose}
              variant="outline"
              className="flex-1"
              disabled={loading}
            >
              إلغاء
            </Button>
            <Button
              onClick={handleBlock}
              className="flex-1 bg-red-500 hover:bg-red-600 text-white"
              disabled={loading}
            >
              {loading ? 'جاري الحظر...' : 'حظر المستخدم'}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export { ReportUser, BlockUser };
