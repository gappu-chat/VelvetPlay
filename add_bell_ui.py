import re

html_files = ['public/index.html', 'public/account.html', 'public/player.html']

bell_html = """
<div id="notifBellContainer" style="position: fixed; top: 15px; right: 60px; z-index: 9999;">
  <button onclick="toggleNotifications()" style="background: transparent; border: none; color: white; font-size: 24px; cursor: pointer; position: relative;">
    🔔
    <span id="notifBadge" style="display: none; position: absolute; top: -5px; right: -5px; background: red; color: white; font-size: 10px; padding: 2px 5px; border-radius: 50%; font-weight: bold;">0</span>
  </button>
  <div id="notifDropdown" style="display: none; position: absolute; right: 0; top: 35px; width: 300px; background: #1e1e1e; border: 1px solid #333; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); overflow: hidden; color: white;">
    <div style="padding: 10px; border-bottom: 1px solid #333; font-weight: bold; display: flex; justify-content: space-between;">
      <span>Notifications</span>
      <span onclick="markAllRead()" style="font-size: 12px; color: #3b82f6; cursor: pointer;">Mark all read</span>
    </div>
    <div id="notifList" style="max-height: 300px; overflow-y: auto;">
      <div style="padding: 15px; text-align: center; color: #888;">Loading...</div>
    </div>
  </div>
</div>

<script>
async function fetchNotifications() {
  const token = Auth.getToken();
  if (!token) return;
  
  try {
    const res = await fetch('/api/notifications', { headers: { 'Authorization': 'Bearer ' + token } });
    if (!res.ok) return;
    const notifs = await res.json();
    
    const unreadRes = await fetch('/api/notifications/unread-count', { headers: { 'Authorization': 'Bearer ' + token } });
    const unreadData = await unreadRes.json();
    
    const badge = document.getElementById('notifBadge');
    if (unreadData.count > 0) {
      badge.style.display = 'block';
      badge.innerText = unreadData.count;
    } else {
      badge.style.display = 'none';
    }

    const list = document.getElementById('notifList');
    if (notifs.length === 0) {
      list.innerHTML = '<div style="padding: 15px; text-align: center; color: #888;">No notifications yet.</div>';
    } else {
      list.innerHTML = notifs.map(n => `
        <div style="padding: 10px; border-bottom: 1px solid #222; background: ${n.is_read ? 'transparent' : '#2a2a2a'};">
          <div style="font-weight: bold; font-size: 14px;">${n.title}</div>
          <div style="font-size: 12px; color: #aaa; margin-top: 3px;">${n.message}</div>
        </div>
      `).join('');
    }
  } catch(e) { console.log(e); }
}

function toggleNotifications() {
  const dropdown = document.getElementById('notifDropdown');
  if (dropdown.style.display === 'none') {
    dropdown.style.display = 'block';
    fetchNotifications();
  } else {
    dropdown.style.display = 'none';
  }
}

async function markAllRead() {
  const token = Auth.getToken();
  if (!token) return;
  await fetch('/api/notifications/read', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token } });
  fetchNotifications();
}

// Page load hone par check karo
document.addEventListener("DOMContentLoaded", () => {
    setTimeout(fetchNotifications, 1000);
});

// Har 30 second me check karo
setInterval(fetchNotifications, 30000);
</script>
</body>
"""

for file in html_files:
    try:
        with open(file, 'r') as f:
            html = f.read()
        
        if 'notifBellContainer' not in html:
            html = html.replace('</body>', bell_html)
            with open(file, 'w') as f:
                f.write(html)
            print(f"✅ Bell icon added to {file}")
        else:
            print(f"⚠️ Bell icon already exists in {file}")
    except Exception as e:
        print(f"❌ Error in {file}: {e}")
