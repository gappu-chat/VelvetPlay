import re

with open('public/player.html', 'r') as f:
    html = f.read()

# 1. Download button aur script ko hatao
html = re.sub(r'<button[^>]*id="dlBtn"[^>]*>.*?</button>', '', html, flags=re.DOTALL)
html = re.sub(r'<script>\s*function downloadCurrentVideo.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<script>\s*function getVideoId.*?</script>', '', html, flags=re.DOTALL)

# 2. Agar extra div add ho gaya tha, use hatao
html = re.sub(r'<div style="text-align:center; margin: 20px;">.*?</div>', '', html, flags=re.DOTALL)

# 3. Khali tags saaf karo
html = re.sub(r'<script>\s*</script>', '', html)

with open('public/player.html', 'w') as f:
    f.write(html)
print("✅ File purani haalat mein wapas aa gayi!")
