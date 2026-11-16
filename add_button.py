import re

with open('public/player.html', 'r') as f:
    html = f.read()

# Jo naya button add karna hai
new_button = """
      <button class="action-btn" onclick="downloadCurrentVideo()" id="dlBtn">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download
      </button>"""

# 'Save' button ko dhoondho aur uske theek baad naya button daal do
if 'downloadCurrentVideo' not in html:
    html = html.replace('</svg> Save</button>', '</svg> Save</button>' + new_button)
    with open('public/player.html', 'w') as f:
        f.write(html)
    print("✅ Button successfully add ho gaya!")
else:
    print("⚠️ Button pehle se hi maujood hai.")
