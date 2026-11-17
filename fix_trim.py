with open('server.js', 'r') as f:
    code = f.read()

# URL aur Token ko trim karne ka code
code = code.replace("url: process.env.TURSO_DATABASE_URL,", 'url: (process.env.TURSO_DATABASE_URL || "").trim(),')
code = code.replace("authToken: process.env.TURSO_AUTH_TOKEN,", 'authToken: (process.env.TURSO_AUTH_TOKEN || "").trim(),')

with open('server.js', 'w') as f:
    f.write(code)
print("✅ Trim code successfully add ho gaya!")
