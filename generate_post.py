"""
Daily Forex/Trading/Crypto Education Post Generator
-----------------------------------------------------
Ye script:
1. Google Gemini (FREE API) se ek naya educational post generate karta hai
2. Us mein aapka affiliate link daalta hai
3. Ek HTML file banata hai posts/ folder mein
4. index.html (homepage) ko update karta hai naye post ke sath

Environment variables (GitHub Secrets se aate hain):
- GEMINI_API_KEY   -> Google AI Studio se free API key
- AFFILIATE_LINK   -> aapka affiliate link
"""

import os
import json
import random
from datetime import datetime
import google.generativeai as genai

# ---------- CONFIG ----------
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
AFFILIATE_LINK = os.environ.get("AFFILIATE_LINK", "https://example.com/your-affiliate-link")
SITE_TITLE = "Forex & Crypto Trading Academy"

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

# ---------- SETUP GEMINI ----------
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def generate_content(topic):
    prompt = f"""
    Tum ek professional Forex aur Crypto trading educator ho.
    Topic: "{topic}"

    Ek chota, informative aur engaging blog post likho (Roman Urdu/Hindi + English mix, jaisa
    trading community mein likha jata hai). Requirements:
    - 250-350 words
    - 3-4 short paragraphs ya bullet points
    - Ek catchy heading do (pehli line mein, bina # ke)
    - Beginner-friendly tone, practical tips
    - Ant mein ek short call-to-action line jo trading platform try karne ke liye encourage kare
    - Kisi financial guarantee ya "sure profit" jaisa claim mat karo, disclaimer wala tone rakho
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def build_html(title, body_text, date_str, slug):
    paragraphs = "\n".join(f"<p>{line.strip()}</p>" for line in body_text.split("\n") if line.strip())
    return f"""<!DOCTYPE html>
<html lang="ur">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | {SITE_TITLE}</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<div class="container">
  <a href="../index.html" class="back-link">&larr; Home</a>
  <h1>{title}</h1>
  <p class="date">{date_str}</p>
  {paragraphs}
  <div class="cta-box">
    <p>Trading shuru karne ke liye trusted platform try karein:</p>
    <a href="{AFFILIATE_LINK}" target="_blank" rel="nofollow noopener" class="cta-button">Abhi Account Banayein &rarr;</a>
  </div>
  <p class="disclaimer">Disclaimer: Ye content sirf educational purpose ke liye hai. Trading mein risk hota hai, apni research zaroor karein.</p>
</div>
</body>
</html>"""

def update_index(posts):
    items = "\n".join(
        f'<li><a href="posts/{p["slug"]}.html">{p["title"]}</a><span class="date">{p["date"]}</span></li>'
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
  <h1>{SITE_TITLE}</h1>
  <p class="subtitle">Daily Forex, Trading &amp; Crypto Education</p>
  <ul class="post-list">
  {items}
  </ul>
</div>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    topic = random.choice(TOPICS)
    content = generate_content(topic)

    lines = content.split("\n")
    title = lines[0].strip().lstrip("#").strip()
    body = "\n".join(lines[1:]).strip()

    today = datetime.now()
    date_str = today.strftime("%d-%m-%Y")
    slug = today.strftime("%Y-%m-%d") + "-" + str(random.randint(100, 999))

    post_html = build_html(title, body, date_str, slug)
    with open(f"posts/{slug}.html", "w", encoding="utf-8") as f:
        f.write(post_html)

    posts_file = "posts.json"
    posts = []
    if os.path.exists(posts_file):
        with open(posts_file, "r", encoding="utf-8") as f:
            posts = json.load(f)
    posts.append({"title": title, "date": date_str, "slug": slug})
    with open(posts_file, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    update_index(posts)
    print(f"Naya post ban gaya: {title}")

if __name__ == "__main__":
    main()
