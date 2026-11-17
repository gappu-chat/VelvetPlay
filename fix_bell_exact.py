with open('public/index.html', 'r') as f:
    html = f.read()

# Naya Bell code, Search bar ke theek baad lagane ke liye
bell_code = '''
      <div id="notifBellContainer" style="position: relative; display: flex; align-items: center; margin-right: 10px;">
        <button onclick="toggleNotifications()" style="background: transparent; border: none; color: white; font-size: 22px; cursor: pointer; position: relative; padding: 5px;">
          🔔
          <span id="notifBadge" style="display: none; position: absolute; top: 0px; right: 0px; background: red; color: white; font-size: 10px; padding: 2px 5px; border-radius: 50%; font-weight: bold;">0</span>
        </button>
        <div id="notifDropdown" style="display: none; position: absolute; right: 0; top: 35px; width: 280px; background: #1e1e1e; border: 1px solid #333; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); z-index: 9999; color: white; text-align: left;">
          <div style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; display: flex; justify-content: space-between;">
            <span>Notifications</span>
            <span onclick="markAllRead()" style="font-size: 12px; color: #3b82f6; cursor: pointer;">Mark all read</span>
          </div>
          <div id="notifList" style="max-height: 300px; overflow-y: auto;">
            <div style="padding: 15px; text-align: center; color: #888;">Loading...</div>
          </div>
        </div>
      </div>'''

# Bell ko search bar aur Login button ke beech me daalo
if 'notifBellContainer' not in html:
    html = html.replace('<input class="search" id="search" placeholder="Search movies, tags..." />', 
                        '<input class="search" id="search" placeholder="Search movies, tags..." />\n' + bell_code)

with open('public/index.html', 'w') as f:
    f.write(html)
print("✅ Bell icon perfect jagah pe lag gaya!")
