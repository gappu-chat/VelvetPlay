import re

with open('public/player.html', 'r') as f:
    html = f.read()

# 1. Download Button Add Karo
if 'id="dlBtn"' not in html:
    btn = '''
      <button class="action-btn" onclick="downloadCurrentVideo()" id="dlBtn" style="margin-left: 8px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download
      </button>'''
    html = html.replace('</svg> Save</button>', '</svg> Save</button>' + btn)

# 2. Script Add Karo
if 'function downloadCurrentVideo' not in html:
    script = """
<script>
function getVideoId() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("id") || urlParams.get("video") || urlParams.get("v");
}

async function checkDownloadStatus() {
  const token = Auth.getToken();
  const videoId = getVideoId();
  const btn = document.getElementById("dlBtn");
  if (!token || !videoId || !btn) return;

  try {
    const res = await fetch("/api/user/downloads", { headers: { "Authorization": "Bearer " + token } });
    const downloads = await res.json();
    const isSaved = downloads.some(d => d.id === videoId);
    
    if (isSaved) {
      btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg> <span style="color:#10b981; font-weight:bold;">Saved</span>';
    } else {
      btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download';
    }
  } catch(e) {}
}

async function downloadCurrentVideo() {
  const token = Auth.getToken();
  if (!token) { alert("Login karein!"); window.location.href = "/login.html"; return; }
  const videoId = getVideoId();
  const btn = document.getElementById("dlBtn");
  if (!videoId || !btn) return;

  const isSaved = btn.innerText.includes("Saved");
  
  if (isSaved) {
    if(!confirm("Remove from downloads?")) return;
    btn.innerHTML = '<svg class="spin-anim" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Removing...';
    try {
      const res = await fetch("/api/user/downloads/" + videoId, { method: "DELETE", headers: { "Authorization": "Bearer " + token } });
      if(res.ok) checkDownloadStatus();
    } catch(e) { alert("Error!"); checkDownloadStatus(); }
  } else {
    btn.innerHTML = '<svg class="spin-anim" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"></path></svg> Saving...';
    try {
      const res = await fetch("/api/download/save", {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
        body: JSON.stringify({ videoId })
      });
      if(res.ok) checkDownloadStatus();
    } catch(e) { alert("Error!"); checkDownloadStatus(); }
  }
}

document.addEventListener("DOMContentLoaded", checkDownloadStatus);
</script>
"""
    html = html.replace('</body>', script + '\n</body>')

with open('public/player.html', 'w') as f:
    f.write(html)
print("✅ Button aur Script dono add ho gaye, aur purana code safe hai!")
