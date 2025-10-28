import React, { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function RegisterPhone({ onClose }){
  const [phone,setPhone] = useState("");
  const [code,setCode]   = useState("");
  const [sent, setSent]  = useState(false);
  const [loading,setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = async ()=>{
    if(!phone) return;
    setLoading(true);
    setError("");
    try{ 
      await axios.post(`${API}/api/auth/otp/send`,{ phone }); 
      setSent(true); 
    } catch(err) { 
      setError("تعذّر إرسال الرمز"); 
      console.error(err);
    } finally{ 
      setLoading(false); 
    }
  };

  const verify = async ()=>{
    if(!code) return;
    setLoading(true);
    setError("");
    try{ 
      await axios.post(`${API}/api/auth/otp/verify`,{ phone, code }); 
      alert("تم التوثيق ✨");
      onClose?.(); 
    } catch(err) { 
      setError("رمز غير صحيح"); 
      console.error(err);
    } finally{ 
      setLoading(false); 
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[999] p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-3 dark:text-white">توثيق الهاتف</h3>
        
        {!sent ? (
          <>
            <input 
              className="w-full rounded-xl border px-4 h-12 mb-3 dark:bg-gray-700 dark:text-white dark:border-gray-600" 
              placeholder="+966XXXXXXXXX" 
              value={phone} 
              onChange={(e)=>setPhone(e.target.value)} 
              dir="ltr"
            />
            <button 
              disabled={loading} 
              onClick={send} 
              className="w-full h-11 rounded-xl text-white bg-pink-500 hover:bg-pink-600 disabled:opacity-50 font-medium"
            >
              {loading? "..." : "إرسال رمز التحقق"}
            </button>
          </>
        ):(
          <>
            <input 
              className="w-full rounded-xl border px-4 h-12 mb-3 text-center dark:bg-gray-700 dark:text-white dark:border-gray-600" 
              placeholder="أدخل الرمز" 
              value={code} 
              onChange={(e)=>setCode(e.target.value)} 
              maxLength={6}
            />
            <button 
              disabled={loading} 
              onClick={verify} 
              className="w-full h-11 rounded-xl text-white bg-pink-500 hover:bg-pink-600 disabled:opacity-50 font-medium"
            >
              {loading? "..." : "تأكيد"}
            </button>
            <button 
              onClick={send} 
              className="mt-2 text-sm text-pink-600 dark:text-pink-400 underline"
            >
              إعادة إرسال الرمز
            </button>
          </>
        )}
        
        {error && (
          <div className="mt-3 text-red-600 dark:text-red-400 text-sm">{error}</div>
        )}
        
        <button 
          onClick={onClose} 
          className="mt-3 w-full h-11 rounded-xl border dark:border-gray-600 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700 font-medium"
        >
          إغلاق
        </button>
      </div>
    </div>
  );
}
