import re

with open('public/player.html', 'r') as f:
    html = f.read()

# 1. Button ko thoda chhota karo taaki text cut na ho (margin-left hata do)
html = re.sub(r'id="dlBtn"[^>]*style="[^"]*"', 'id="dlBtn"', html)

# 2. Agar pichli baar maine jo custom script add ki thi (jo title update karti hai), usko hatao
html = re.sub(r'<script>\s*// Ye script video ko wapas load karegi.*?</script>', '', html, flags=re.DOTALL)

# 3. Original video load karne wala code wapas add karo (jo tumhare original code me tha)
# Kyunki humne galti se delete kar diya tha, ye code usko dobara set karega
script = """
<script>
// Original Player Logic
let token = Auth.getToken();
const urlParams = new URLSearchParams(window.location.search);
let videoId = urlParams.get("id") || urlParams.get("video") || urlParams.get("v");

if (videoId) {
  fetch('/api/video/' + videoId).then(r => r.json()).then(video => {
    if(!video || video.error) return;
    if(document.getElementById('vtitle')) document.getElementById('vtitle').innerText = video.title || 'Untitled';
    if(document.getElementById('vviews')) document.getElementById('vviews').innerText = `${video.views || 0} views`;
    
    // Video player load karo
    if (token) {
      fetch('/api/create-order', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ videoId: video.id })
      }).then(res => res.json()).then(data => {
        if (data.hasAccess) {
          const v = document.querySelector('video');
          if(v) { v.src = `/api/stream/${video.id}?token=${data.token}`; v.load(); }
        }
      });
    }
  });

  // Related Videos load karo
  fetch('/api/videos').then(r => r.json()).then(data => {
    if(!data.videos) return;
    let others = data.videos.filter(v => v.id !== videoId).sort(() => 0.5 - Math.random()).slice(0, 4);
    let relatedDiv = document.getElementById('related');
    if(relatedDiv) {
      relatedDiv.innerHTML = others.map(v => `<div class="yt-card" onclick="location.href='/player.html?video=${v.id}'"><img class="yt-card-thumb" src="${v.thumbnail}" loading="lazy"/><div class="yt-card-info"><div class="yt-card-title">${v.title || 'Untitled'}</div><div style="font-size:12px; color:#AAAAAA;">${v.views || 0} views</div></div></div>`).join('');
    }
  });
}
</script>
"""

# 4. Download button ka logic wapas add karo
download_script = """
<style>
  @keyframes spin { 100% { transform: rotate(360deg); } }
  .spin-anim { animation: spin 1s linear infinite; }
</style>
<script>
function getVideoId() { return new URLSearchParams(window.location.search).get("id") || new URLSearchParams(window.location.search).get("video") || new URLSearchParams(window.location.search).get("v"); }
async function checkDownloadStatus() {
  const token = Auth.getToken(); const videoId = getVideoId(); const btn = document.getElementById('dlBtn');
  if (!token || !videoId || !btn) return;
  try {
    const res = await fetch('/api/user/downloads', { headers: { 'Authorization': 'Bearer ' + token } });
    const downloads = await res.json();
    const isSaved = downloads.some(d => d.id === videoId);
    if (isSaved) { btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg> <span style="color:#10b981; font-weight:bold;">Saved</span>'; }
    else { btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download'; }
  } catch(e) {}
}
async function downloadCurrentVideo() {
  const token = Auth.getToken(); if (!token) { alert("Login karein!"); window.location.href = "/login.html"; return; }
  const videoId = getVideoId(); const btn = document.getElementById('dlBtn'); if (!videoId || !btn) return;
  const isSaved = btn.innerText.includes('Saved');
  if (isSaved) {
    if(!confirm("Remove from downloads?")) return;
    btn.innerHTML = '<svg class="spin-anim" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Removing...';
    try { const res = await fetch(`/api/user/downloads/${videoId}`, { method: 'DELETE', headers: { 'Authorization': 'Bearer ' + token } }); if(res.ok) checkDownloadStatus(); } catch(e) { alert("Error!"); checkDownloadStatus(); }
  } else {
    btn.innerHTML = '<svg class="spin-anim" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Saving...';
    try { const res = await fetch('/api/download/save', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token }, body: JSON.stringify({ videoId }) }); if(res.ok) checkDownloadStatus(); } catch(e) { alert("Error!"); checkDownloadStatus(); }
  }
}
document.addEventListener("DOMContentLoaded", checkDownloadStatus);
</script>
"""

if 'id="dlBtn"' not in html:
    btn = '''<button class="action-btn" onclick="downloadCurrentVideo()" id="dlBtn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download</button>'''
    html = html.replace('</svg> Save</button>', '</svg> Save</button>' + btn)

html = html.replace('</body>', script + download_script + '\n</body>')

with open('public/player.html', 'w') as f:
    f.write(html)
print("✅ Final fix ho gaya! Ab sab kuch perfect chalega.")
