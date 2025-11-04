# 🌐 DNS Configuration Guide for pizoo.ch

**URGENT ACTION REQUIRED:** Configure these DNS records at Hostpoint to activate your production domain.

---

## 📋 Quick Start - Copy These Records to Hostpoint

### Step 1: Login to Hostpoint
🔗 **URL:** https://admin.hostpoint.ch/  
**Navigate to:** Domains → pizoo.ch → DNS Settings / Zone Editor

---

## 🎯 DNS Records to Configure

### Record 1: Apex Domain (pizoo.ch)

```
┌─────────────────────────────────────────────────┐
│ TYPE:  A                                        │
│ NAME:  @ (or leave blank for root domain)      │
│ VALUE: 76.76.21.21                              │
│ TTL:   3600 (or Auto)                           │
└─────────────────────────────────────────────────┘
```

**Alternative Option (if A record doesn't work):**
```
┌─────────────────────────────────────────────────┐
│ TYPE:  CNAME                                    │
│ NAME:  @ (or leave blank)                       │
│ VALUE: 44589a4b7c4c7957.vercel-dns-017.com.     │
│ TTL:   3600                                     │
└─────────────────────────────────────────────────┘
```
> **Note:** Some providers don't allow CNAME on apex. Try A record first.

---

### Record 2: WWW Subdomain (www.pizoo.ch)

```
┌─────────────────────────────────────────────────┐
│ TYPE:  CNAME                                    │
│ NAME:  www                                      │
│ VALUE: 44589a4b7c4c7957.vercel-dns-017.com.     │
│ TTL:   3600 (or Auto)                           │
└─────────────────────────────────────────────────┘
```

**Alternative (Generic Vercel CNAME):**
```
┌─────────────────────────────────────────────────┐
│ TYPE:  CNAME                                    │
│ NAME:  www                                      │
│ VALUE: cname.vercel-dns.com.                    │
│ TTL:   3600                                     │
└─────────────────────────────────────────────────┘
```

---

## 📸 Hostpoint Configuration Screenshot Guide

### What Your Hostpoint DNS Panel Should Look Like:

```
┌────────────────────────────────────────────────────────────┐
│ DNS Records for pizoo.ch                                   │
├──────┬──────┬───────────────────────────────────┬─────────┤
│ Type │ Host │ Points To / Value                 │ TTL     │
├──────┼──────┼───────────────────────────────────┼─────────┤
│ A    │ @    │ 76.76.21.21                       │ 3600    │
│ CNAME│ www  │ 44589a4b7c4c7957.vercel-dns-017.com.│ 3600  │
└──────┴──────┴───────────────────────────────────┴─────────┘
```

---

## ⚡ Quick Copy-Paste Format

**For Hostpoint Form Fields:**

```
Record 1:
Type = A
Host = @
Value = 76.76.21.21
TTL = 3600

Record 2:
Type = CNAME
Host = www
Value = 44589a4b7c4c7957.vercel-dns-017.com.
TTL = 3600
```

---

## ⏱️ Propagation Timeline

| Time | Status |
|------|--------|
| **0-5 min** | DNS records saved at Hostpoint |
| **5-15 min** | Initial propagation begins |
| **15-30 min** | Most DNS servers updated ✅ |
| **1-2 hours** | Global propagation complete |
| **Up to 48 hours** | Maximum propagation time (rare) |

**Typical Wait Time:** 15-30 minutes ⏰

---

## 🔍 Verification Commands

### 1. Check DNS Propagation:
```bash
# Using dig (Mac/Linux)
dig pizoo.ch A +short
# Expected output: 76.76.21.21

dig www.pizoo.ch CNAME +short
# Expected output: 44589a4b7c4c7957.vercel-dns-017.com.

# Using nslookup (Windows/Mac/Linux)
nslookup pizoo.ch
nslookup www.pizoo.ch
```

### 2. Test Domain Accessibility:
```bash
# Test apex domain
curl -I https://pizoo.ch/

# Test www redirect
curl -I https://www.pizoo.ch/

# Test API health
curl https://pizoo.ch/health
```

### 3. Online DNS Checker:
🔗 **Check globally:** https://dnschecker.org/#A/pizoo.ch

---

## 🎯 Vercel Current Configuration

**Your Vercel domains are already configured:**

✅ **pizoo.ch**
- Status: Verified
- Type: Production (Primary)
- SSL: Auto-provisioned (after DNS)

✅ **www.pizoo.ch**
- Status: Verified
- Type: Redirect → pizoo.ch
- SSL: Auto-provisioned (after DNS)

**Nothing to do in Vercel dashboard - just configure DNS at Hostpoint!**

---

## 🔐 SSL Certificate

**Automatic SSL Configuration:**
- Provider: Let's Encrypt (via Vercel)
- Type: Free, Auto-Renewing
- Issuance: Automatic (within 5-10 minutes after DNS propagates)
- Renewal: Every 90 days (automatic)
- Protocols: TLS 1.2, TLS 1.3
- Status: **Will activate automatically once DNS propagates** ⏳

**No action required for SSL!**

---

## 📞 Hostpoint Support (if needed)

**Contact Hostpoint Support:**
- 📧 Email: support@hostpoint.ch
- 📞 Phone: +41 848 46 78 76
- 💬 Live Chat: https://www.hostpoint.ch/en/support

**What to tell them:**
> "I need to add DNS records for my domain pizoo.ch to point to Vercel. I need to add:
> - A record for @ pointing to 76.76.21.21
> - CNAME record for www pointing to 44589a4b7c4c7957.vercel-dns-017.com."

---

## ✅ Checklist

- [ ] Login to Hostpoint DNS management
- [ ] Add A record: @ → 76.76.21.21
- [ ] Add CNAME record: www → 44589a4b7c4c7957.vercel-dns-017.com.
- [ ] Save DNS changes
- [ ] Wait 15-30 minutes for propagation
- [ ] Test: https://pizoo.ch/ (should load)
- [ ] Test: https://www.pizoo.ch/ (should redirect to apex)
- [ ] Verify SSL certificate (green padlock in browser)
- [ ] Test API: https://pizoo.ch/health
- [ ] Check CORS headers work properly

---

## 🚨 Common Issues

### Issue: "Cannot add CNAME to apex domain"
**Solution:** Use A record (76.76.21.21) instead

### Issue: "DNS not updating after 1 hour"
**Solution:**
1. Double-check records are saved in Hostpoint
2. Ensure no typos in values
3. Clear your DNS cache locally
4. Wait up to 48 hours maximum

### Issue: "SSL certificate not showing"
**Solution:**
1. Verify DNS has propagated (use dnschecker.org)
2. Wait 5-10 minutes after DNS propagates
3. Check Vercel dashboard for certificate status

---

## 🎉 After DNS Propagation

Once DNS propagates, your app will be live at:

✅ **Primary:** https://pizoo.ch  
✅ **WWW:** https://www.pizoo.ch (redirects to primary)  
✅ **API:** https://pizoo.ch/api/...  
✅ **Health Check:** https://pizoo.ch/health  

**All with automatic SSL encryption!** 🔒

---

## 📊 Current Vercel Deployment

**Deployment ID:** dpl_7woMjdZB3ALauzKYCuKvi9ufsXcJ  
**Status:** READY ✅  
**Branch:** Main  
**Commit:** bbb17a074742d95772339aa4d466ee18d848bfb6  

🔗 **Monitor:** https://vercel.com/shatha-db/pizoo/dpl_7woMjdZB3ALauzKYCuKvi9ufsXcJ

---

**🎯 Next Step: Configure the DNS records at Hostpoint now!**

*Once configured, check back in 15-30 minutes to verify everything is working.*

---

*Last Updated: January 2025*
