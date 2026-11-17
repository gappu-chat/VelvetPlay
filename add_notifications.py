with open('server.js', 'r') as f:
    code = f.read()

notification_routes = """
// ---------- NOTIFICATIONS API ----------
app.get('/api/notifications', auth, async (req, res) => {
  try {
    const notifications = await db.prepare('SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 20').all(req.user.id);
    res.json(notifications);
  } catch(e) { res.status(500).json({ error: 'Server error' }); }
});

app.get('/api/notifications/unread-count', auth, async (req, res) => {
  try {
    const result = await db.prepare('SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0').get(req.user.id);
    res.json({ count: result.count });
  } catch(e) { res.json({ count: 0 }); }
});

app.post('/api/notifications/read', auth, async (req, res) => {
  try {
    await db.prepare('UPDATE notifications SET is_read = 1 WHERE user_id = ?').run(req.user.id);
    res.json({ success: true });
  } catch(e) { res.status(500).json({ error: 'Server error' }); }
});

app.post('/api/auth/login'"""

if "/api/notifications" not in code:
    code = code.replace("app.post('/api/auth/login'", notification_routes)
    with open('server.js', 'w') as f:
        f.write(code)
    print("✅ Notification routes add ho gaye!")
else:
    print("⚠️ Notification routes pehle se hain.")
