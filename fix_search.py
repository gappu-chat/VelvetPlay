with open('public/index.html', 'r') as f:
    html = f.read()

# Search bar ko form me wrap karo aur Enter event lagao
js_code = """
<script>
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("search");
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
print("✅ Search bar sahi se connect ho gaya!")
