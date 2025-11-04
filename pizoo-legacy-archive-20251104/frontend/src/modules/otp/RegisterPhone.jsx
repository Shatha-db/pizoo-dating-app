import React, { useState } from "react";
import axios from "axios";
import { useTranslation } from "react-i18next";
import CountryCodeSelector from "../../components/CountryCodeSelector";
import { COUNTRY_CODES } from "../../utils/countryCodes";

const API = process.env.REACT_APP_BACKEND_URL || '';

export default function RegisterPhone({ onClose }){
  const { t } = useTranslation(['auth', 'common']);
  const [selectedCountry, setSelectedCountry] = useState(COUNTRY_CODES[0]); // Default Saudi Arabia
  const [phoneNumber, setPhoneNumber] = useState("");
  const [code,setCode]   = useState("");
  const [sent, setSent]  = useState(false);
  const [loading,setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = async ()=>{
    if(!phoneNumber) return;
    setLoading(true);
    setError("");
    
    // Combine country code with phone number
    const fullPhone = selectedCountry.dial + phoneNumber;
    
    try{ 
      await axios.post(`${API}/api/auth/phone/send-otp`,{ phone: fullPhone }); 
      setSent(true); 
    } catch(err) { 
      setError(t("Failed to send code", { ns: 'auth' })); 
      console.error(err);
    } finally{ 
      setLoading(false); 
    }
  };

  const verify = async ()=>{
    if(!code) return;
    setLoading(true);
    setError("");
    
    const fullPhone = selectedCountry.dial + phoneNumber;
    
    try{ 
      await axios.post(`${API}/api/auth/phone/verify-otp`,{ phone: fullPhone, code }); 
      alert(t("Phone verified successfully", { ns: 'auth' }));
      onClose?.(); 
    } catch(err) { 
      setError(t("Invalid code", { ns: 'auth' })); 
      console.error(err);
    } finally{ 
      setLoading(false); 
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[999] p-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-3 dark:text-white">{t("Phone Verification", { ns: 'auth' })}</h3>
        
        {!sent ? (
          <>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {t("Enter your phone number to receive verification code", { ns: 'auth' })}
            </p>
            
            {/* Phone Input with Country Selector */}
            <div className="flex gap-2 mb-3">
              <CountryCodeSelector 
                selectedCountry={selectedCountry}
                onChange={setSelectedCountry}
              />
              <input 
                className="flex-1 rounded-xl border px-4 h-12 dark:bg-gray-700 dark:text-white dark:border-gray-600" 
                placeholder="512345678" 
                value={phoneNumber} 
                onChange={(e)=>setPhoneNumber(e.target.value.replace(/\D/g, ''))} 
                type="tel"
                maxLength={15}
                dir="ltr"
              />
            </div>
            
            <button 
              disabled={loading || !phoneNumber} 
              onClick={send} 
              className="w-full h-11 rounded-xl text-white bg-pink-500 hover:bg-pink-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading? "..." : t("Send verification code", { ns: 'auth' })}
            </button>
          </>
        ):(
          <>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {t("Code sent to", { ns: 'auth' })} {selectedCountry.dial}{phoneNumber}
            </p>
            <input 
              className="w-full rounded-xl border px-4 h-12 mb-3 text-center dark:bg-gray-700 dark:text-white dark:border-gray-600 text-2xl tracking-widest" 
              placeholder="000000" 
              value={code} 
              onChange={(e)=>setCode(e.target.value.replace(/\D/g, ''))} 
              maxLength={6}
              type="tel"
            />
            <button 
              disabled={loading || code.length !== 6} 
              onClick={verify} 
              className="w-full h-11 rounded-xl text-white bg-pink-500 hover:bg-pink-600 disabled:opacity-50 disabled:cursor-not-allowed font-medium mb-2"
            >
              {loading? "..." : t("Verify", { ns: 'auth' })}
            </button>
            <button 
              onClick={send} 
              disabled={loading}
              className="w-full text-sm text-pink-600 dark:text-pink-400 underline hover:no-underline disabled:opacity-50"
            >
              {t("Resend code", { ns: 'auth' })}
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
          {t("Close", { ns: 'common' })}
        </button>
      </div>
    </div>
  );
}
