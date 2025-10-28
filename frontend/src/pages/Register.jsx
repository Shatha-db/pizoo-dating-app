import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import i18n from "../i18n";

export default function Register(){
  const { t } = useTranslation(["auth","common"]);
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [emailPhone, setEmailPhone] = useState("");
  const [password, setPassword] = useState("");

  const onLangChange = (e) => i18n.changeLanguage(e.target.value);

  const handleRegister = async (e) => {
    e.preventDefault();
    // TODO: implement registration API call
    console.log('Register:', { name, emailPhone, password });
  };

  const openPhoneRegister = () => {
    window.dispatchEvent(new CustomEvent('otp:open'));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-100 to-rose-200">
      <div className="absolute top-4 right-4">
        <select 
          className="rounded-lg px-3 py-2 bg-white/90 border"
          value={i18n.resolvedLanguage || "en"}
          onChange={onLangChange}
        >
          <option value="en">English</option>
          <option value="ar">العربية</option>
          <option value="fr">Français</option>
          <option value="es">Español</option>
          <option value="de">Deutsch</option>
          <option value="tr">Türkçe</option>
          <option value="it">Italiano</option>
          <option value="pt-BR">Português</option>
          <option value="ru">Русский</option>
        </select>
      </div>

      <div className="w-full max-w-md bg-white/95 rounded-2xl shadow-xl p-6 mx-4">
        <h1 className="text-2xl font-bold mb-2">
          {t("auth:register_title") || "Create a new account"}
        </h1>
        <p className="text-sm text-gray-600 mb-5">
          {t("auth:register_subtitle") || "Join Pizoo and find your match"}
        </p>

        <form onSubmit={handleRegister}>
          <label className="block text-sm mb-1 font-medium">
            {t("auth:name")||"Name"}
          </label>
          <input 
            className="w-full rounded-xl border px-4 h-12 mb-3" 
            value={name} 
            onChange={(e)=>setName(e.target.value)} 
            placeholder={t("auth:placeholder_name")||"Your name"} 
          />

          <label className="block text-sm mb-1 font-medium">
            {t("auth:email_or_phone")||"Email or phone"}
          </label>
          <input 
            className="w-full rounded-xl border px-4 h-12 mb-3" 
            value={emailPhone} 
            onChange={(e)=>setEmailPhone(e.target.value)} 
            placeholder={t("auth:placeholder_email_phone")||"example@email.com or +966XXXXXXXX"} 
          />

          <label className="block text-sm mb-1 font-medium">
            {t("auth:password")||"Password"}
          </label>
          <input 
            className="w-full rounded-xl border px-4 h-12 mb-4" 
            type="password" 
            value={password} 
            onChange={(e)=>setPassword(e.target.value)} 
            placeholder={t("auth:placeholder_password")||"Choose a strong password"} 
          />

          <button 
            type="submit"
            className="w-full h-12 rounded-full text-white font-semibold bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600"
          >
            {t("auth:sign_up")||"Create account"}
          </button>
        </form>

        <div className="text-center mt-4 text-sm">
          {t("auth:have_account")||"Already have an account?"}{" "}
          <button 
            onClick={() => navigate('/login')}
            className="text-pink-600 underline font-medium"
          >
            {t("auth:sign_in")||"Sign in"}
          </button>
        </div>

        <div className="mt-6">
          <button 
            id="btn-phone-register" 
            onClick={openPhoneRegister}
            className="w-full h-11 rounded-xl border bg-white hover:bg-gray-50 font-medium"
          >
            {t("auth:register_with_phone")||"Register using phone"}
          </button>
        </div>
      </div>
    </div>
  );
}
