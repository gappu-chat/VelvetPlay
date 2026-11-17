with open('public/index.html', 'r') as f:
    html = f.read()

# Naya bell icon jo header me fit baithega
bell_ui = """
<div id="notifBellContainer" style="position: relative; display: inline-block; margin-left: 10px;">
  <button onclick="toggleNotifications()" style="background: transparent; border: none; color: white; font-size: 24px; cursor: pointer; position: relative; padding: 0;">
    🔔
    <span id="notifBadge" style="display: none; position: absolute; top: -2px; right: -5px; background: red; color: white; font-size: 10px; padding: 2px 5px; border-radius: 50%; font-weight: bold;">0</span>
  </button>
  <div id="notifDropdown" style="display: none; position: absolute; right: 0; top: 35px; width: 280px; background: #1e1e1e; border: 1px solid #333; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); overflow: hidden; color: white; z-index: 9999; text-align: left;">
    <div style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; display: flex; justify-content: space-between;">
      <span>Notifications</span>
      <span onclick="markAllRead()" style="font-size: 12px; color: #3b82f6; cursor: pointer;">Mark all read</span>
    </div>
    <div id="notifList" style="max-height: 300px; overflow-y: auto;">
      <div style="padding: 15px; text-align: center; color: #888;">Loading...</div>
    </div>
  </div>
</div>
"""

# Bell ko login button ya profile ke theek pehle daalo
if 'notifBellContainer' not in html:
    # Agar login button hai to uske pehle daalo
    if '<a href="/login.html"' in html:
        html = html.replace('<a href="/login.html"', bell_ui + '<a href="/login.html"')
    else:
        # Agar account ka icon hai to uske pehle
        html = html.replace('<div class="profile-icon"', bell_ui + '<div class="profile-icon"')

with open('public/index.html', 'w') as f:
    f.write(html)
print("✅ Bell icon sahi jagah lag gaya!")
