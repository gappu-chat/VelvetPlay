import re

# index.html ko theek karo
with open('public/index.html', 'r') as f:
    html = f.read()

# 1. "Notifications" wala bikhra hua box hatao (jo upar right me dikh raha hai)
html = re.sub(r'<div id="notifBellContainer".*?</div>\s*</div>\s*</div>', '', html, flags=re.DOTALL)

# 2. Neeche wala bikhra hua bell (Latest & Trending ke paas) hatao
html = re.sub(r'<div id="notifBellContainer".*?</div>', '', html, flags=re.DOTALL)

# 3. Purana notif script hatao
html = re.sub(r'<script>\s*async function fetchNotifications.*?</script>', '', html, flags=re.DOTALL)

# 4. Sirf Search bar aur Login button wapas theek karo (bina touch kiye)
# Agar galti se header ka structure bigda hai, use wapas set karo
header_fix = '''<div class="header-top">
      <div class="logo" onclick="location.href='/'">Velvet<span>Play</span></div>
      <input class="search" id="search" placeholder="Search movies, tags..." />
      <button class="user-btn login-state" id="userBtn" onclick="userClick()">Login</button>
    </div>'''

html = re.sub(r'<div class="header-top">.*?</div>', header_fix, html, flags=re.DOTALL)

with open('public/index.html', 'w') as f:
    f.write(html)
print("✅ Home page ka layout wapas perfect ho gaya!")

# account.html aur player.html se bhi bell hatao
for file in ['public/account.html', 'public/player.html']:
    try:
        with open(file, 'r') as f:
            h = f.read()
        h = re.sub(r'<div id="notifBellContainer".*?</div>\s*</div>\s*</div>', '', h, flags=re.DOTALL)
        h = re.sub(r'<div id="notifBellContainer".*?</div>', '', h, flags=re.DOTALL)
        with open(file, 'w') as f:
            f.write(h)
        print(f"✅ {file} saaf ho gaya!")
    except Exception as e:
        print(f"⚠️ {file} me error: {e}")
