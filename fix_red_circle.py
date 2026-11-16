with open('server.js', 'r') as f:
    lines = f.readlines()

# Line 196 (index 195) se stream ka code replace karna hai
new_stream = '''app.get('/api/stream/:videoId', (req, res) => {
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
'''

# Line 196 se aage ka purana code hatao jab tak app.listen na aaye
start_index = 195
end_index = len(lines)
for i in range(start_index, len(lines)):
    if 'app.listen' in lines[i]:
        end_index = i
        break

# Naya code daalo
lines = lines[:start_index] + [new_stream] + lines[end_index:]

with open('server.js', 'w') as f:
    f.writelines(lines)
print("✅ Red circle wala code fix ho gaya!")
