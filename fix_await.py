with open('server.js', 'r') as f:
    code = f.read()

# Un 2 lines se 'await' hatao jo function ke bahar hain
code = code.replace("await db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('upi_id', 'vp061038-2@okhdfcbank');", "db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('upi_id', 'vp061038-2@okhdfcbank').catch(console.error);")
code = code.replace("await db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('upi_name', 'VelvetPlay');", "db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('upi_name', 'VelvetPlay').catch(console.error);")

with open('server.js', 'w') as f:
    f.write(code)
print("✅ Top-level await fix ho gaya!")
