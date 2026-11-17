import re
with open('server.js', 'r') as f:
    code = f.read()

# Saare routes mein jahan (req, res) hai, uske pehle 'async' add karo (agar pehle se nahi hai)
code = re.sub(r",\s*\(req,\s*res\)\s*=>", ", async (req, res) =>", code)

# Agar kisi jagah galti se 'async async' ho gaya ho toh usko theek karo
code = re.sub(r"async\s+async\s+\(req,\s*res\)\s*=>", "async (req, res) =>", code)

with open('server.js', 'w') as f:
    f.write(code)
print("✅ Sabhi routes perfectly async ho gaye!")
