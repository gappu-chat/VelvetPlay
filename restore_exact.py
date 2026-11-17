import re

with open('public/index.html', 'r') as f:
    html = f.read()

# Naya exact header code (jo tumhare pehle screenshot me tha)
new_header = """
  <header>
    <div class="header-top">
      <div class="logo" onclick="location.href='/'">Velvet<span>Play</span></div>
      <input class="search" id="search" placeholder="Search movies, tags..." />
      <button class="user-btn login-state" id="userBtn" onclick="userClick()">Login</button>
    </div>
    <div class="categories" id="categories"></div>
  </header>
"""

# Purane poore header ko naye header se replace karo
html = re.sub(r'<header>.*?</header>', new_header, html, flags=re.DOTALL)

# Us bikhre hue "Notifications" aur "Loading" wale box ko hatao
html = re.sub(r'<div id="notifBellContainer".*?</div>\s*</div>\s*</div>', '', html, flags=re.DOTALL)
html = re.sub(r'<div id="notifBellContainer".*?</div>', '', html, flags=re.DOTALL)

# Neeche wala bikhra hua bell (Latest & Trending ke paas) hatao
html = html.replace('🔔', '')

# Bell ki purani script hatao
html = re.sub(r'<script>\s*async function fetchNotifications.*?</script>', '', html, flags=re.DOTALL)

with open('public/index.html', 'w') as f:
    f.write(html)

print("✅ Tumhara Home Page wapas pehle jaisa ho gaya!")
