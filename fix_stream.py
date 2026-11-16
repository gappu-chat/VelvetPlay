import re

with open('server.js', 'r') as f:
    code = f.read()

# Naya streaming code jo smooth chalega
new_stream_code = '''app.get('/api/stream/:videoId', (req, res) => {
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
        'Content-Range': `bytes ${start}-${end}/${stat.size}`,
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
});'''

# Purane stream route ko naye se replace karo
code = re.sub(r"app\.get\('/api/stream/:videoId'.*?\}\);", new_stream_code, code, flags=re.DOTALL)

with open('server.js', 'w') as f:
    f.write(code)
print("✅ Server streaming code update ho gaya!")
