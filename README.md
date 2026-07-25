# Forex & Crypto Auto-Blog (Daily Auto Posting System)

Ye system har din automatic ek naya educational post banata hai (Forex/Trading/Crypto)
aur usme aapka affiliate link daal deta hai. Bilkul free hai.

## Setup Steps (ek dafa karna hai)

### 1. GitHub par naya repository banayein
- github.com par login karein (account nahi hai to free bana lein)
- "New repository" par click karein
- Naam dein (e.g. `forex-auto-blog`) -> Public rakhein -> Create

### 2. Ye saari files us repo mein upload karein
- Repo khol kar "Add file" -> "Upload files" par click karein
- Ye poora folder (sari files aur folders) drag & drop kar dein
- "Commit changes" par click karein

### 3. FREE Gemini API Key banayein
- https://aistudio.google.com/apikey par jayein
- Google account se login karein
- "Create API Key" par click karein -> key copy kar lein
- (Bilkul FREE hai, credit card nahi chahiye)

### 4. GitHub mein Secrets add karein
Repo ke andar:
- Settings -> Secrets and variables -> Actions -> "New repository secret"
- Do secrets banayein:
  - Name: `GEMINI_API_KEY` -> Value: (jo key copy ki thi)
  - Name: `AFFILIATE_LINK` -> Value: (aapka affiliate link, e.g. https://...)

### 5. GitHub Pages enable karein (website live karne ke liye)
- Settings -> Pages
- Source: "Deploy from a branch" -> Branch: `main` -> folder: `/ (root)` -> Save
- Kuch minute baad aapki site is URL par live hogi:
  `https://<aapka-username>.github.io/<repo-naam>/`

### 6. Automation test karein
- Repo ke "Actions" tab mein jayein
- "Daily Auto Post" workflow select karein
- "Run workflow" button se manually ek baar chala kar test kar lein
- Agar successful hua to `posts/` folder mein naya HTML file aur `index.html` update ho jayega

## Uske baad kya hoga?
- Ye workflow **har din automatic** (schedule: roz UTC 04:00 = Pakistan ~9 AM) chalega
- Naya post generate hoga, affiliate link ke sath, aur khud commit+push ho jayega
- Aapki website khud-ba-khud update hoti rahegi, kuch karna nahi padega

## Customize karna ho to
- `scripts/generate_post.py` mein `TOPICS` list mein apne topics add/remove kar sakte hain
- Timing badalne ke liye `.github/workflows/daily-post.yml` mein cron time change karein
- Design badalne ke liye `style.css` edit karein
