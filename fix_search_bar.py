import re

with open('public/index.html', 'r') as f:
    html = f.read()

# Search bar (input type="text" placeholder="Search...") ko form me wrap karo
# Aur usme id="mainSearch" add karo taaki JS se pakad sake
if 'id="mainSearch"' not in html:
    # Purane search input ko dhoondh kar naya form daal do
    html = re.sub(
        r'<input[^>]*type="text"[^>]*placeholder="Search movies, tags..."[^>]*>', 
        '<input type="text" id="mainSearch" placeholder="Search movies, tags..." style="flex:1; padding:10px 15px; border-radius:20px; border:none; background:#1f1f1f; color:white; outline:none;">', 
        html
    )

# JavaScript add karo jo Enter dabane par search page par bhejega
js_code = """
<script>
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("mainSearch");
    if (searchInput) {
        searchInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                const q = searchInput.value.trim();
                if (q) window.location.href = "/search.html?q=" + encodeURIComponent(q);
            }
        });
    }
});
</script>
</body>
"""

html = html.replace('</body>', js_code)

with open('public/index.html', 'w') as f:
    f.write(html)
print("✅ Home page ka search bar set ho gaya!")
