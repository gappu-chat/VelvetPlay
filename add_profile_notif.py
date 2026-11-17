with open('server.js', 'r') as f:
    code = f.read()

# Profile update route me notification add karo
old_code = """app.put('/api/auth/profile', auth, async (req, res) => {
  try {
    await db.prepare('UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?').run(req.body.name, req.body.email, req.body.phone, req.user.id);
    res.json({ success: true });
  } catch(e) { res.status(400).json({ error: 'Email already in use' }); }
});"""

new_code = """app.put('/api/auth/profile', auth, async (req, res) => {
  try {
    await db.prepare('UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?').run(req.body.name, req.body.email, req.body.phone, req.user.id);
    // Notification create karo
    await db.prepare('INSERT INTO notifications (user_id, title, message) VALUES (?, ?, ?)').run(req.user.id, 'Profile Updated', 'Your profile details have been updated successfully.');
    res.json({ success: true });
  } catch(e) { res.status(400).json({ error: 'Email already in use' }); }
});"""

if 'Profile Updated' not in code:
    code = code.replace(old_code, new_code)
    with open('server.js', 'w') as f:
        f.write(code)
    print("✅ Profile update notification added!")
else:
    print("⚠️ Already added.")
