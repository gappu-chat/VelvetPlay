require('dotenv').config();
const express = require('express');
const jwt = require('jsonwebtoken');
const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const multer = require('multer');
const { exec } = require('child_process');
const speakeasy = require('speakeasy');
const QRCode = require('qrcode');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static('public'));

process.on('uncaughtException', (err) => console.error('\n⚠️ CAUGHT:', err.message));
process.on('unhandledRejection', (reason) => console.error('\n⚠️ REJECTION:', reason));

const db = new Database('videos.db');
db.exec(`
  CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password_hash TEXT, sub_expiry DATETIME);
  CREATE TABLE IF NOT EXISTS videos (id TEXT PRIMARY KEY, title TEXT, thumbnail TEXT, category TEXT, is_free INTEGER, views INTEGER DEFAULT 0, likes INTEGER DEFAULT 0, dislikes INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, video_id TEXT, user_id INTEGER, user_name TEXT, username TEXT, text TEXT, likes INTEGER DEFAULT 0, parent_id INTEGER, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
  CREATE TABLE IF NOT EXISTS payment_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, user_name TEXT, item_type TEXT, item_id TEXT, amount INTEGER, utr TEXT, status TEXT DEFAULT 'pending', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS user_library (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, video_id TEXT, folder_name TEXT DEFAULT 'Saved', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS user_folders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, folder_name TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS user_downloads (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, video_id TEXT, downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS watch_history (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, video_id TEXT, progress INTEGER DEFAULT 0, duration INTEGER DEFAULT 0, watched_at DATETIME DEFAULT CURRENT_TIMESTAMP);
  CREATE TABLE IF NOT EXISTS tv_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT, user_id INTEGER, video_id TEXT, token TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
`);

try { db.exec('ALTER TABLE users ADD COLUMN vault_pin TEXT'); } catch(e) {}
try { db.exec('ALTER TABLE users ADD COLUMN referral_code TEXT'); } catch(e) {}
try { db.exec('ALTER TABLE users ADD COLUMN referred_by INTEGER'); } catch(e) {}
try { db.exec('ALTER TABLE users ADD COLUMN username TEXT'); } catch(e) {}
try { db.exec('ALTER TABLE users ADD COLUMN twofa_secret TEXT'); } catch(e) {}
try { db.exec('ALTER TABLE users ADD COLUMN twofa_enabled INTEGER DEFAULT 0'); } catch(e) {}
try { db.exec('ALTER TABLE users ADD COLUMN phone TEXT'); } catch(e) {}
try { db.exec('ALTER TABLE videos ADD COLUMN tags TEXT'); } catch(e) {}
try { db.exec('ALTER TABLE videos ADD COLUMN dislikes INTEGER DEFAULT 0'); } catch(e) {}
try { db.exec('ALTER TABLE watch_history ADD COLUMN progress INTEGER DEFAULT 0'); } catch(e) {}
try { db.exec('ALTER TABLE watch_history ADD COLUMN duration INTEGER DEFAULT 0'); } catch(e) {}
try { db.exec('ALTER TABLE comments ADD COLUMN likes INTEGER DEFAULT 0'); } catch(e) {}
try { db.exec('ALTER TABLE comments ADD COLUMN parent_id INTEGER'); } catch(e) {}
try { db.exec('ALTER TABLE comments ADD COLUMN username TEXT'); } catch(e) {}

db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('upi_id', 'vp061038-2@okhdfcbank');
db.prepare('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)').run('upi_name', 'VelvetPlay');

const uploadDir = path.join(__dirname, 'temp_uploads');
const mediaDir = path.join(__dirname, 'media');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
if (!fs.existsSync(mediaDir)) fs.mkdirSync(mediaDir);

const upload = multer({ dest: uploadDir });
const JWT_SECRET = process.env.JWT_SECRET || 'super_secret_key_123';

function auth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Login required' });
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = db.prepare('SELECT * FROM users WHERE id = ?').get(payload.userId);
    if (!req.user) throw new Error();
    next();
  } catch { res.status(401).json({ error: 'Invalid Token' }); }
}

function adminAuth(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Admin login required' });
  try { if (!jwt.verify(token, JWT_SECRET).isAdmin) throw new Error(); next(); } 
  catch { res.status(401).json({ error: 'Unauthorized' }); }
}

// ---------- TV CASTING SYSTEM ----------
app.post('/api/tv/create', (req, res) => {
  const code = Math.floor(1000 + Math.random() * 9000).toString();
  db.prepare('DELETE FROM tv_sessions WHERE created_at < datetime("now", "-1 hour")').run();
  const result = db.prepare('INSERT INTO tv_sessions (code) VALUES (?)').run(code);
  res.json({ code });
});

app.get('/api/tv/poll/:code', (req, res) => {
  const session = db.prepare('SELECT * FROM tv_sessions WHERE code = ?').get(req.params.code);
  if (!session) return res.status(404).json({ error: 'Expired' });
  res.json({ video_id: session.video_id, token: session.token });
});

app.post('/api/tv/pair', auth, (req, res) => {
  const session = db.prepare('SELECT * FROM tv_sessions WHERE code = ?').get(req.body.code);
  if (!session) return res.status(404).json({ error: 'Invalid Code' });
  db.prepare('UPDATE tv_sessions SET user_id = ? WHERE id = ?').run(req.user.id, session.id);
  res.json({ success: true });
});

app.post('/api/tv/send', auth, (req, res) => {
  const session = db.prepare('SELECT * FROM tv_sessions WHERE user_id = ?').get(req.user.id);
  if (!session) return res.status(404).json({ error: 'No paired TV. Connect in Settings.' });
  const token = jwt.sign({ videoId: req.body.videoId }, JWT_SECRET, { expiresIn: '12h' });
  db.prepare('UPDATE tv_sessions SET video_id = ?, token = ? WHERE id = ?').run(req.body.videoId, token, session.id);
  res.json({ success: true });
});

// ---------- AUTH & 2FA ----------
app.post('/api/auth/login', async (req, res) => {
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(req.body.email.toLowerCase());
  if (!user || !(await bcrypt.compare(req.body.password, user.password_hash))) return res.status(400).json({ error: 'Invalid credentials' });
  
  if (user.twofa_enabled) {
    const tempToken = jwt.sign({ userId: user.id, temp: true }, JWT_SECRET, { expiresIn: '5m' });
    return res.json({ requires2FA: true, tempToken });
  }
  
  if (!user.username) {
    let baseUsername = (user.name || 'user').toLowerCase().replace(/\s+/g, '');
    let username = '@' + baseUsername + '_' + Math.floor(10 + Math.random() * 99);
    db.prepare('UPDATE users SET username = ? WHERE id = ?').run(username, user.id);
    user.username = username;
  }
  const { password_hash, vault_pin, twofa_secret, ...safe } = user;
  res.json({ token: jwt.sign({ userId: safe.id }, JWT_SECRET), user: safe });
});

app.post('/api/auth/login-2fa', (req, res) => {
  try {
    const payload = jwt.verify(req.body.tempToken, JWT_SECRET);
    if (!payload.temp) throw new Error();
    const user = db.prepare('SELECT * FROM users WHERE id = ?').get(payload.userId);
    const verified = speakeasy.totp.verify({ secret: user.twofa_secret, encoding: 'base32', token: req.body.code });
    if (!verified) return res.status(400).json({ error: 'Invalid 2FA Code' });
    const { password_hash, vault_pin, twofa_secret, ...safe } = user;
    res.json({ token: jwt.sign({ userId: safe.id }, JWT_SECRET), user: safe });
  } catch { res.status(401).json({ error: 'Session Expired' }); }
});

app.get('/api/auth/me', auth, (req, res) => {
  res.json({ id: req.user.id, name: req.user.name, email: req.user.email, username: req.user.username, phone: req.user.phone, sub_expiry: req.user.sub_expiry, vault_enabled: !!req.user.vault_pin, twofa_enabled: !!req.user.twofa_enabled });
});

app.put('/api/auth/profile', auth, (req, res) => {
  try {
    db.prepare('UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?').run(req.body.name, req.body.email, req.body.phone, req.user.id);
    res.json({ success: true });
  } catch(e) { res.status(400).json({ error: 'Email already in use' }); }
});

app.post('/api/auth/2fa/setup', auth, async (req, res) => {
  const secret = speakeasy.generateSecret({ name: `VelvetPlay (${req.user.email})` });
  db.prepare('UPDATE users SET twofa_secret = ? WHERE id = ?').run(secret.base32, req.user.id);
  const qrUrl = await QRCode.toDataURL(secret.otpauth_url);
  res.json({ qrUrl, secret: secret.base32 });
});

app.post('/api/auth/2fa/enable', auth, (req, res) => {
  const user = db.prepare('SELECT twofa_secret FROM users WHERE id = ?').get(req.user.id);
  if (!speakeasy.totp.verify({ secret: user.twofa_secret, encoding: 'base32', token: req.body.code })) return res.status(400).json({ error: 'Galat code' });
  db.prepare('UPDATE users SET twofa_enabled = 1 WHERE id = ?').run(req.user.id);
  res.json({ success: true });
});

// ---------- REST OF THE ROUTES ----------
app.get('/api/referral/info', auth, (req, res) => { const u = db.prepare('SELECT referral_code FROM users WHERE id = ?').get(req.user.id); const c = db.prepare('SELECT COUNT(*) as count FROM users WHERE referred_by = ?').get(req.user.id).count; res.json({ code: u.referral_code, totalReferred: c }); });
app.post('/api/history/save', auth, (req, res) => { const { videoId, progress, duration } = req.body; db.prepare('DELETE FROM watch_history WHERE user_id = ? AND video_id = ?').run(req.user.id, videoId); db.prepare('INSERT INTO watch_history (user_id, video_id, progress, duration) VALUES (?, ?, ?, ?)').run(req.user.id, videoId, progress, duration); res.json({ success: true }); });
app.get('/api/history/continue', auth, (req, res) => { res.json(db.prepare(`SELECT w.progress, w.duration, v.* FROM watch_history w JOIN videos v ON v.id = w.video_id WHERE w.user_id = ? AND w.progress > 10 AND w.progress < (w.duration - 30) ORDER BY w.watched_at DESC LIMIT 5`).all(req.user.id)); });
app.get('/api/history/all', auth, (req, res) => { res.json(db.prepare(`SELECT w.watched_at, w.progress, v.* FROM watch_history w JOIN videos v ON v.id = w.video_id WHERE w.user_id = ? ORDER BY w.watched_at DESC LIMIT 20`).all(req.user.id)); });
app.get('/api/video/:id/comments', (req, res) => { const comments = db.prepare('SELECT * FROM comments WHERE video_id = ? ORDER BY likes DESC, created_at DESC').all(req.params.id); res.json(comments); });
app.post('/api/video/:id/comments', auth, (req, res) => { const { text, parent_id } = req.body; if (!text) return res.status(400).json({ error: 'Empty' }); const result = db.prepare('INSERT INTO comments (video_id, user_id, user_name, username, text, parent_id) VALUES (?, ?, ?, ?, ?, ?)').run(req.params.id, req.user.id, req.user.name, req.user.username, text, parent_id || null); res.json({ success: true, id: result.lastInsertRowid }); });
app.post('/api/comment/:id/like', auth, (req, res) => { db.prepare('UPDATE comments SET likes = likes + 1 WHERE id = ?').run(req.params.id); res.json({ success: true }); });
app.post('/api/video/:id/react', (req, res) => { const { type, action } = req.body; if (type === 'like') { if(action === 'add') db.prepare('UPDATE videos SET likes = likes + 1 WHERE id = ?').run(req.params.id); else db.prepare('UPDATE videos SET likes = likes - 1 WHERE id = ?').run(req.params.id); } else if (type === 'dislike') { if(action === 'add') db.prepare('UPDATE videos SET dislikes = dislikes + 1 WHERE id = ?').run(req.params.id); else db.prepare('UPDATE videos SET dislikes = dislikes - 1 WHERE id = ?').run(req.params.id); } res.json({ success: true }); });
app.put('/api/user/vault-pin', auth, async (req, res) => { const hash = req.body.pin ? await bcrypt.hash(req.body.pin, 10) : null; db.prepare('UPDATE users SET vault_pin = ? WHERE id = ?').run(hash, req.user.id); res.json({ success: true }); });
app.post('/api/user/verify-pin', auth, async (req, res) => { if (!req.user.vault_pin) return res.json({ success: true }); res.json({ success: await bcrypt.compare(req.body.pin, req.user.vault_pin) }); });
app.get('/api/user/folders', auth, (req, res) => { const custom = db.prepare('SELECT folder_name FROM user_folders WHERE user_id = ?').all(req.user.id); res.json([...new Set(['Saved', 'Favorites', 'Vault', ...custom.map(f => f.folder_name)])]); });
app.post('/api/user/folders', auth, (req, res) => { db.prepare('INSERT INTO user_folders (user_id, folder_name) VALUES (?, ?)').run(req.user.id, req.body.folder_name); res.json({ success: true }); });
app.get('/api/library', auth, (req, res) => { res.json(db.prepare(`SELECT ul.id as saved_id, ul.folder_name, v.* FROM user_library ul JOIN videos v ON v.id = ul.video_id WHERE ul.user_id = ? ORDER BY ul.created_at DESC`).all(req.user.id)); });
app.post('/api/library/add', auth, (req, res) => { db.prepare('INSERT INTO user_library (user_id, video_id, folder_name) VALUES (?, ?, ?)').run(req.user.id, req.body.videoId, req.body.folderName || 'Saved'); res.json({ success: true }); });
app.delete('/api/library/:id', auth, (req, res) => { db.prepare('DELETE FROM user_library WHERE id = ? AND user_id = ?').run(req.params.id, req.user.id); res.json({ success: true }); });
app.get('/api/videos', (req, res) => { const { q, category } = req.query; let sql = 'SELECT * FROM videos'; const params = []; const where = []; if (q) { where.push('(title LIKE ? OR tags LIKE ? OR category LIKE ?)'); params.push(`%${q}%`, `%${q}%`, `%${q}%`); } if (category && category !== 'All') { where.push('category = ?'); params.push(category); } if (where.length) sql += ' WHERE ' + where.join(' AND '); sql += ' ORDER BY created_at DESC'; res.json({ videos: db.prepare(sql).all(...params) }); });
app.get('/api/video/:id', (req, res) => res.json(db.prepare('SELECT * FROM videos WHERE id = ?').get(req.params.id)));
app.post('/api/video/:id/view', (req, res) => { db.prepare('UPDATE videos SET views = views + 1 WHERE id = ?').run(req.params.id); res.json({ success: true }); });
app.get('/api/settings', (req, res) => { const rows = db.prepare('SELECT key, value FROM settings').all(); res.json(rows.reduce((acc, r) => ({ ...acc, [r.key]: r.value }), {})); });
app.post('/api/payment/request', auth, (req, res) => { db.prepare('INSERT INTO payment_requests (user_id, user_name, item_type, item_id, amount, utr) VALUES (?, ?, ?, ?, ?, ?)').run(req.user.id, req.user.name, req.body.itemType, req.body.itemId, req.body.amount, req.body.utr || ''); res.json({ success: true }); });
app.post('/api/create-order', auth, (req, res) => { try { const video = db.prepare('SELECT * FROM videos WHERE id = ?').get(req.body.videoId); if(!video) return res.status(404).json({ error: 'Video not found' }); const isSubscribed = req.user.sub_expiry && new Date(req.user.sub_expiry) > new Date(); if (video.is_free || isSubscribed) return res.json({ hasAccess: true, token: jwt.sign({ videoId: video.id }, JWT_SECRET) }); return res.json({ requiresPayment: true, amount: 29900 }); } catch { res.status(500).json({ error: 'Server Error' }); } });
app.post('/api/admin/login', (req, res) => { if (req.body.password === (process.env.ADMIN_PASSWORD || 'admin123')) res.json({ token: jwt.sign({ isAdmin: true }, JWT_SECRET) }); else res.status(401).json({ error: 'Wrong password' }); });
app.get('/api/admin/analytics', adminAuth, (req, res) => { const totalUsers = db.prepare('SELECT COUNT(*) as c FROM users').get().c; const premiumUsers = db.prepare('SELECT COUNT(*) as c FROM users WHERE sub_expiry > ?').get(new Date().toISOString()).c; const revenue = db.prepare("SELECT SUM(amount) as total FROM payment_requests WHERE status = 'approved'").get().total || 0; const totalVideos = db.prepare('SELECT COUNT(*) as c FROM videos').get().c; res.json({ totalUsers, premiumUsers, revenue: revenue/100, totalVideos }); });
app.get('/api/admin/videos', adminAuth, (req, res) => res.json(db.prepare('SELECT * FROM videos ORDER BY created_at DESC').all()));
app.delete('/api/admin/video/:id', adminAuth, (req, res) => { db.prepare('DELETE FROM videos WHERE id = ?').run(req.params.id); const p = path.join(mediaDir, req.params.id + '.mp4'); if(fs.existsSync(p)) fs.unlinkSync(p); res.json({ success: true }); });
app.get('/api/admin/settings', adminAuth, (req, res) => { const rows = db.prepare('SELECT key, value FROM settings').all(); res.json(rows.reduce((acc, r) => ({ ...acc, [r.key]: r.value }), {})); });
app.post('/api/admin/settings', adminAuth, (req, res) => { const update = db.prepare('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)'); ['upi_id', 'upi_name', 'banner_title', 'banner_desc', 'banner_image', 'banner_video_id'].forEach(k => { if(req.body[k] !== undefined) update.run(k, req.body[k]); }); res.json({ success: true }); });
app.get('/api/admin/payments', adminAuth, (req, res) => res.json(db.prepare("SELECT * FROM payment_requests ORDER BY created_at DESC").all()));
app.post('/api/admin/payments/approve', adminAuth, (req, res) => { const reqRow = db.prepare('SELECT * FROM payment_requests WHERE id = ?').get(req.body.requestId); db.prepare("UPDATE payment_requests SET status = 'approved' WHERE id = ?").run(req.body.requestId); if (reqRow.item_type === 'subscription') { const expiry = new Date(); expiry.setDate(expiry.getDate() + 30); db.prepare('UPDATE users SET sub_expiry = ? WHERE id = ?').run(expiry.toISOString(), reqRow.user_id); } res.json({ success: true }); });
app.post('/api/admin/payments/reject', adminAuth, (req, res) => { db.prepare("UPDATE payment_requests SET status = 'rejected' WHERE id = ?").run(req.body.requestId); res.json({ success: true }); });
app.post('/api/admin/upload', adminAuth, upload.fields([{ name: 'video' }, { name: 'thumbnail' }]), (req, res) => { const videoId = 'vid_' + Date.now(); const outPath = path.join(mediaDir, videoId + '.mp4'); let thumbUrl = 'https://picsum.photos/seed/' + videoId + '/800/450'; if (req.files.thumbnail) { fs.renameSync(req.files.thumbnail[0].path, path.join(__dirname, 'public', videoId + '.jpg')); thumbUrl = '/' + videoId + '.jpg'; } db.prepare(`INSERT INTO videos (id, title, thumbnail, category, is_free, tags) VALUES (?, ?, ?, ?, ?, ?)`).run(videoId, req.body.title, thumbUrl, req.body.category, req.body.isFree === 'true' ? 1 : 0, req.body.tags || ''); exec(`ffmpeg -i "${req.files.video[0].path}" -c:v libx264 -preset veryfast -crf 28 -c:a aac -movflags +faststart "${outPath}"`, () => {}); res.json({ success: true }); });
app.get('/api/stream/:videoId', (req, res) => {
  try {
    jwt.verify(req.query.token, JWT_SECRET);
    const filePath = path.join(mediaDir, req.params.videoId + '.mp4');
    if (!fs.existsSync(filePath)) return res.status(404).send('Processing...');
    const stat = fs.statSync(filePath);
    const range = req.headers.range;

    if (range) {
      const parts = range.replace(/bytes=/, "").split("-");
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : stat.size - 1;
      const chunksize = (end - start) + 1;
      
      res.writeHead(206, {
        'Content-Range': 'bytes ' + start + '-' + end + '/' + stat.size,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunksize,
        'Content-Type': 'video/mp4',
        'Cache-Control': 'public, max-age=31536000'
      });
      
      const stream = fs.createReadStream(filePath, { start, end });
      stream.pipe(res);
    } else {
      res.writeHead(200, {
        'Content-Length': stat.size,
        'Content-Type': 'video/mp4',
        'Cache-Control': 'public, max-age=31536000'
      });
      fs.createReadStream(filePath).pipe(res);
    }
  } catch (err) {
    res.status(403).send('Unauthorized');
  }
});
app.listen(process.env.PORT || 3000, () => console.log(`✅ Server: http://localhost:3000`));
