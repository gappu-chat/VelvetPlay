with open('server.js', 'r') as f:
    code = f.read()

signup_route = """
app.post('/api/auth/signup', async (req, res) => {
  try {
    const { name, email, password, referral } = req.body;
    if (!name || !email || !password) return res.status(400).json({ error: 'All fields required' });
    
    const existing = db.prepare('SELECT * FROM users WHERE email = ?').get(email.toLowerCase());
    if (existing) return res.status(400).json({ error: 'Email already exists' });

    const hashedPassword = await bcrypt.hash(password, 10);
    let baseUsername = name.toLowerCase().replace(/\\s+/g, '');
    let username = '@' + baseUsername + '_' + Math.floor(10 + Math.random() * 99);
    
    let referredBy = null;
    if (referral) {
      const referrer = db.prepare('SELECT id FROM users WHERE referral_code = ?').get(referral);
      if (referrer) referredBy = referrer.id;
    }
    
    const myReferralCode = 'ZAYN' + Math.floor(1000 + Math.random() * 9000);

    const result = db.prepare('INSERT INTO users (name, email, password_hash, username, referred_by, referral_code) VALUES (?, ?, ?, ?, ?, ?)').run(name, email.toLowerCase(), hashedPassword, username, referredBy, myReferralCode);
    
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(result.lastInsertRowid);
    const { password_hash, vault_pin, twofa_secret, ...safe } = user;
    
    res.json({ token: jwt.sign({ userId: safe.id }, JWT_SECRET), user: safe });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

app.post('/api/auth/login'"""

if "/api/auth/signup" not in code:
    code = code.replace("app.post('/api/auth/login'", signup_route)
    with open('server.js', 'w') as f:
        f.write(code)
    print("✅ Signup route successfully add ho gaya!")
else:
    print("⚠️ Signup route pehle se maujood hai.")
