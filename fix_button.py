with open('public/player.html', 'r') as f:
    html = f.read()

# Share button ke baad naya download button add karne ka code
target = 'onclick="openSaveModal()"'
new_btn = '''<button class="action-btn" onclick="downloadCurrentVideo()" id="dlBtn" style="margin-left: 8px;">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg> Download
      </button>'''

# Agar pehle se nahi hai, toh add karo
if 'id="dlBtn"' not in html and target in html:
    # Save button ka pura tag dhoondh kar uske theek baad naya button lagao
    import re
    html = re.sub(r'(<button[^>]*openSaveModal[^>]*>.*?</button>)', r'\1\n      ' + new_btn, html, flags=re.DOTALL)
    with open('public/player.html', 'w') as f:
        f.write(html)
    print("✅ Button perfectly add ho gaya!")
else:
    print("⚠️ Button add nahi hua (shayad pehle se hai).")
