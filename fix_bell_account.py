with open('public/account.html', 'r') as f:
    html = f.read()

bell_code = '''
      <div id="notifBellContainer" style="position: relative; display: inline-block; margin-right: 15px; vertical-align: middle;">
        <button onclick="toggleNotifications()" style="background: transparent; border: none; color: white; font-size: 22px; cursor: pointer; padding: 0; margin: 0;">
          🔔
          <span id="notifBadge" style="display: none; position: absolute; top: 0; right: -5px; background: red; color: white; font-size: 10px; padding: 2px 5px; border-radius: 50%; font-weight: bold;">0</span>
        </button>
        <div id="notifDropdown" style="display: none; position: absolute; right: 0; top: 30px; width: 280px; background: #1e1e1e; border: 1px solid #333; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); z-index: 9999; text-align: left;">
          <div style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; display: flex; justify-content: space-between;">
            <span>Notifications</span>
            <span onclick="markAllRead()" style="font-size: 12px; color: #3b82f6; cursor: pointer;">Mark all read</span>
          </div>
          <div id="notifList" style="max-height: 300px; overflow-y: auto;">
            <div style="padding: 15px; text-align: center; color: #888;">Loading...</div>
          </div>
        </div>
      </div>
'''

# Settings icon ke theek pehle bell lagao
if 'notifBellContainer' not in html:
    if 'onclick="location.href=\'/settings.html\'"' in html:
        html = html.replace('onclick="location.href=\'/settings.html\'"', bell_code + '\n<a onclick="location.href=\'/settings.html\'"')
    elif '<a href="/settings.html"' in html:
        html = html.replace('<a href="/settings.html"', bell_code + '\n<a href="/settings.html"')
        
    with open('public/account.html', 'w') as f:
        f.write(html)
    print("✅ Account page pe bell sahi jagah lag gaya!")
else:
    print("⚠️ Bell pehle se hai.")
