"""
Daily Forex/Trading/Crypto Education Post Generator
-----------------------------------------------------
Ye script:
1. Google Gemini (FREE API) se ek naya educational post generate karta hai (emojis ke sath)
2. Us mein aapka affiliate link daalta hai
3. Hashtags aur keywords bhi generate karta hai
4. Ek modern-style HTML file banata hai posts/ folder mein
5. index.html (homepage) ko update karta hai naye post ke sath

Environment variables (GitHub Secrets se aate hain):
- GEMINI_API_KEY   -> Google AI Studio se free API key
- AFFILIATE_LINK   -> aapka affiliate link
"""

import os
import sys
import json
import random
import time
from datetime import datetime
from google import genai
import requests

# ---------- CONFIG ----------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
AFFILIATE_LINK = os.environ.get("AFFILIATE_LINK", "https://example.com/your-affiliate-link")
SITE_TITLE = "Forex & Crypto Trading Academy"
SITE_URL = "https://gulishop.github.io/forex-auto-blog/"

FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_ACCESS_TOKEN")

def _parse_fb_pages():
    """FB_PAGE_ID aur FB_PAGE_ACCESS_TOKEN dono comma-separated ho sakte hain
    (multiple pages ke liye), jaise: FB_PAGE_ID=111,222  FB_PAGE_ACCESS_TOKEN=tokA,tokB
    Dono lists same order/length mein honi chahiye."""
    if not FB_PAGE_ID or not FB_PAGE_ACCESS_TOKEN:
        return []
    ids = [p.strip() for p in FB_PAGE_ID.split(",") if p.strip()]
    tokens = [t.strip() for t in FB_PAGE_ACCESS_TOKEN.split(",") if t.strip()]
    if len(ids) != len(tokens):
        print(f"⚠️ FB_PAGE_ID ({len(ids)}) aur FB_PAGE_ACCESS_TOKEN ({len(tokens)}) ki count match nahi karti - Facebook post skip kiya.")
        return []
    return list(zip(ids, tokens))

TOPICS = [
    "Forex trading ke liye beginner ki 5 sabse zaroori tips",
    "Risk management kaise karein Forex trading mein",
    "Crypto trading vs Forex trading - konsa behtar hai",
    "Candlestick patterns jo har trader ko pata hone chahiye",
    "Leverage kya hai aur ise safely kaise use karein",
    "Trading psychology - emotions ko control karna kyun zaroori hai",
    "Support aur Resistance kaise identify karein",
    "Best time frames Forex trading ke liye",
    "Stop loss aur take profit ka sahi use",
    "Crypto market mein volatility ko kaise samjhein",
    "Trading plan kaise banayein - step by step guide",
    "Demo account se real account tak ka safar",
    "Fundamental analysis vs Technical analysis",
    "Common mistakes jo naye traders karte hain",
    "Moving averages kaise use karein trading mein",
]

DEFAULT_HASHTAGS = ["#Forex", "#ForexTrading", "#Crypto", "#CryptoTrading", "#Exness", "#TradingTips", "#FinancialFreedom"]

# ---------- SETUP GEMINI ----------
client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-flash-latest"


class QuotaExceededError(Exception):
    """Jab Gemini free-tier quota/rate-limit khatam ho jaye."""
    pass


def _is_quota_error(e):
    text = str(e).lower()
    return any(k in text for k in ["quota", "rate limit", "429", "resource_exhausted"])


def call_gemini(prompt, retries=3, delay=20):
    """Gemini ko call karta hai, quota/rate-limit error pe thoda ruk ke retry karta hai."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return response.text.strip()
        except Exception as e:
            last_err = e
            if _is_quota_error(e):
                if attempt < retries:
                    print(f"⚠️ Quota/rate-limit hit (attempt {attempt}/{retries}), {delay}s baad retry karenge...")
                    time.sleep(delay)
                    continue
                raise QuotaExceededError(str(e)) from e
            raise
    raise QuotaExceededError(str(last_err)) from last_err


def generate_content(topic):
    prompt = f"""
    Tum ek professional Forex aur Crypto trading educator ho, jo social-media-style engaging
    content likhte ho.
    Topic: "{topic}"

    Ek chota, modern aur engaging blog post likho (Roman Urdu/Hindi + English mix, jaisa
    trading community mein likha jata hai). Requirements:
    - 250-350 words
    - 3-4 short paragraphs ya bullet points
    - Ek catchy heading do (pehli line mein, bina # ke), heading mein ek relevant emoji bhi shamil karo.
      Heading aisa likho jo curiosity jagaye AUR clearly bataye ke post ke andar kya milega
      (jaise "5 Galtiyan Jo Naye Traders Karte Hain (Aur Inse Kaise Bachein)" ya
      "Stop Loss Sahi Jagah Kaise Lagayein? Ye 3 Tarike Try Karein"), sirf vague ya
      clickbait-only heading mat do jisme content ka andaza na ho.
    - Har paragraph ya bullet point ke shuru mein ek relevant emoji use karo (jaise 📊 💡 ⚠️ 🚀 💰 📈 🎯)
    - Beginner-friendly tone, practical tips, modern aur energetic lehja
    - Ant mein ek short call-to-action line jo trading platform try karne ke liye encourage kare, usme bhi emoji ho
    - Kisi financial guarantee ya "sure profit" jaisa claim mat karo, disclaimer wala tone rakho
    - Emojis natural lagne chahiye, overuse mat karo (max 1-2 per line)
    """
    return call_gemini(prompt)

def generate_hashtags(topic):
    prompt = f"""
    Topic: "{topic}"
    Is Forex/Crypto trading topic ke liye 8 relevant English hashtags do (jaise #Forex #Trading).
    Sirf hashtags do, koi extra text nahi, ek line mein space se separate karke.
    """
    try:
        text = call_gemini(prompt, retries=1)
        tags = text.strip().split()
        tags = [t for t in tags if t.startswith("#")]
        if len(tags) >= 4:
            return tags
    except Exception:
        pass
    return DEFAULT_HASHTAGS

def build_html(title, body_text, date_str, slug, hashtags):
    paragraphs = "\n".join(f"<p>{line.strip()}</p>" for line in body_text.split("\n") if line.strip())
    hashtags_html = " ".join(f'<span class="hashtag">{h}</span>' for h in hashtags)
    hashtags_line = " ".join(hashtags)
    post_url = f"{SITE_URL.rstrip('/')}/posts/{slug}.html"

    # Share text jo WhatsApp/Facebook/Twitter pe jayega: poora post + links neeche (har link apne naam ke sath, alag line)
    share_text = (
        f"🎯 Free Demo Account banayein 👉 {AFFILIATE_LINK}\n\n"
        f"{title}\n\n"
        f"{body_text.strip()}\n\n"
        f"{hashtags_line}\n\n"
        f"🌐 Poori website: {SITE_URL}\n"
        f"📖 Ye post yahan padhein: {post_url}"
    )
    share_text_json = json.dumps(share_text)  # JS ke andar safely embed karne ke liye
    post_url_json = json.dumps(post_url)

    return f"""<!DOCTYPE html>
<html lang="ur">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {SITE_TITLE}</title>
<link rel="stylesheet" href="../style.css">
<style>
.share-box {{ margin: 24px 0; text-align: center; }}
.share-label {{ font-size: 0.95em; opacity: 0.85; margin-bottom: 10px; }}
.share-icons {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}}
.share-icon {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 999px;
  font-size: 0.9em;
  font-weight: 600;
  text-decoration: none;
  border: none;
  cursor: pointer;
  color: #fff;
  transition: transform 0.15s ease, opacity 0.15s ease;
}}
.share-icon:hover {{ transform: translateY(-2px); opacity: 0.92; }}
.share-whatsapp {{ background: #25D366; }}
.share-facebook {{ background: #1877F2; }}
.share-telegram {{ background: #29A9EA; }}
.share-instagram {{ background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); }}
.share-other {{ background: #555; font-family: inherit; }}
.share-copied {{
  display: none;
  margin-top: 10px;
  font-size: 0.85em;
  color: #2ecc71;
}}
.share-copied.visible {{ display: inline-block; }}
</style>
</head>
<body>
<div class="container">
  <a href="../index.html" class="back-link">&larr; Home</a>
  <div class="post-card">
    <h1>{title}</h1>
    <p class="date">📅 {date_str}</p>
    {paragraphs}
    <div class="cta-box">
      <p>🚀 Trading shuru karne ke liye trusted platform try karein:</p>
      <a href="{AFFILIATE_LINK}" target="_blank" rel="nofollow noopener" class="cta-button">💰 Abhi Account Banayein &rarr;</a>
    </div>
    <p class="site-link">🌐 Poori website dekhein: <a href="{SITE_URL}" target="_blank" rel="noopener">{SITE_URL}</a></p>
    <p class="hashtags">{hashtags_html}</p>
    <div class="share-box">
      <p class="share-label">📤 Is post ko share karein:</p>
      <div class="share-icons">
        <a href="#" class="share-icon share-whatsapp" onclick="shareWhatsapp(); return false;" aria-label="Share on WhatsApp">💬 WhatsApp</a>
        <a href="#" class="share-icon share-facebook" onclick="shareFacebook(); return false;" aria-label="Share on Facebook">📘 Facebook</a>
        <a href="#" class="share-icon share-telegram" onclick="shareTelegram(); return false;" aria-label="Share on Telegram">✈️ Telegram</a>
        <a href="#" class="share-icon share-instagram" onclick="shareInstagram(); return false;" aria-label="Share on Instagram">📸 Instagram</a>
        <button class="share-icon share-other" onclick="shareOther()" aria-label="Other share options">🔗 Other</button>
      </div>
      <span class="share-copied" id="shareCopied">Link copied! ✅</span>
    </div>
    <p class="disclaimer">⚠️ Disclaimer: Ye content sirf educational purpose ke liye hai. Trading mein risk hota hai, apni research zaroor karein.</p>
  </div>
</div>
<script>
const shareText = {share_text_json};
const postUrl = {post_url_json};

function copyAndNotify() {{
  navigator.clipboard.writeText(shareText).then(() => {{
    const el = document.getElementById("shareCopied");
    el.classList.add("visible");
    setTimeout(() => el.classList.remove("visible"), 2500);
  }});
}}

function shareWhatsapp() {{
  window.open("https://wa.me/?text=" + encodeURIComponent(shareText), "_blank");
}}

function shareFacebook() {{
  // FB sharer ignores prefilled text on most browsers, so copy full text + open sharer with the link
  copyAndNotify();
  window.open("https://www.facebook.com/sharer/sharer.php?u=" + encodeURIComponent(postUrl), "_blank");
}}

function shareTelegram() {{
  window.open("https://t.me/share/url?url=" + encodeURIComponent(postUrl) + "&text=" + encodeURIComponent(shareText), "_blank");
}}

function shareInstagram() {{
  // Instagram has no web share-intent, so copy text and open the app/site so user can paste it
  copyAndNotify();
  window.open("https://www.instagram.com/", "_blank");
}}

function shareOther() {{
  const shareData = {{ title: document.title, text: shareText }};
  if (navigator.share) {{
    navigator.share(shareData).catch(() => {{}});
  }} else {{
    copyAndNotify();
  }}
}}
</script>
</body>
</html>"""

def update_index(posts):
    items = "\n".join(
        f'<li><a href="posts/{p["slug"]}.html">📈 {p["title"]}</a><span class="date">{p["date"]}</span></li>'
        for p in reversed(posts)
    )
    html = f"""<!DOCTYPE html>
<html lang="ur">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{SITE_TITLE}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
  <h1>💹 {SITE_TITLE}</h1>
  <p class="subtitle">✨ Daily Forex, Trading &amp; Crypto Education</p>
  <ul class="post-list">
  {items}
  </ul>
</div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def post_to_facebook(title, body_text, hashtags, post_url):
    """Har configured Facebook Page pe naya post automatically publish karta hai."""
    pages = _parse_fb_pages()
    if not pages:
        print("⚠️ FB_PAGE_ID ya FB_PAGE_ACCESS_TOKEN missing hai - Facebook post skip kiya.")
        return

    hashtags_line = " ".join(hashtags)
    message = (
        f"🎯 Free Demo Account banayein 👉 {AFFILIATE_LINK}\n\n"
        f"{title}\n\n"
        f"{body_text.strip()}\n\n"
        f"{hashtags_line}\n\n"
        f"🌐 Poori website: {SITE_URL}"
    )

    for page_id, page_token in pages:
        url = f"https://graph.facebook.com/v25.0/{page_id}/feed"
        payload = {
            "message": message,
            "link": post_url,
            "access_token": page_token,
        }
        try:
            response = requests.post(url, data=payload, timeout=30)
            data = response.json()
            if "id" in data:
                print(f"✅ Facebook Page ({page_id}) pe post ho gaya: {data['id']}")
            else:
                print(f"⚠️ Facebook post failed (Page {page_id}): {data}")
        except Exception as e:
            print(f"⚠️ Facebook post error (Page {page_id}): {e}")

def main():
    topic = random.choice(TOPICS)
    try:
        content = generate_content(topic)
    except QuotaExceededError as e:
        print("⚠️ Gemini free-tier quota/rate-limit khatam ho gaya hai is waqt.")
        print(f"Details: {e}")
        print("ℹ️ Naya post skip kiya - agla scheduled run automatically retry karega.")
        print("ℹ️ Agar ye baar-baar ho raha hai, naya API key banao: https://aistudio.google.com/apikey")
        sys.exit(0)  # workflow ko "failed" na dikhayein, bas is run mein post skip

    hashtags = generate_hashtags(topic)

    lines = content.split("\n")
    title = lines[0].strip().lstrip("#").strip()
    body = "\n".join(lines[1:]).strip()

    today = datetime.now()
    date_str = today.strftime("%d-%m-%Y")
    slug = today.strftime("%Y-%m-%d") + "-" + str(random.randint(100, 999))

    post_html = build_html(title, body, date_str, slug, hashtags)
    os.makedirs("posts", exist_ok=True)
    with open(f"posts/{slug}.html", "w", encoding="utf-8") as f:
        f.write(post_html)

    posts_file = "posts.json"
    posts = []
    if os.path.exists(posts_file):
        with open(posts_file, "r", encoding="utf-8") as f:
            posts = json.load(f)
    posts.append({"title": title, "date": date_str, "slug": slug, "hashtags": hashtags})
    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    update_index(posts)

    post_url = f"{SITE_URL.rstrip('/')}/posts/{slug}.html"
    post_to_facebook(title, body, hashtags, post_url)

    print(f"Naya post ban gaya: {title}")
    print(f"Hashtags: {' '.join(hashtags)}")

if __name__ == "__main__":
    main()
