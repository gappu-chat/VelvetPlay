import re

with open('server.js', 'r') as f:
    code = f.read()

# 1. Database package change karo
code = code.replace("const Database = require('better-sqlite3');", "const { createClient } = require('@libsql/client');")

# 2. Purane Database connection ko hata kar Turso connect karo
turso_init = """
const turso = createClient({
  url: process.env.TURSO_DATABASE_URL,
  authToken: process.env.TURSO_AUTH_TOKEN,
});

const db = {
  prepare: (sql) => ({
    get: async (...args) => (await turso.execute({ sql, args })).rows[0],
    all: async (...args) => (await turso.execute({ sql, args })).rows,
    run: async (...args) => {
      const res = await turso.execute({ sql, args });
      return { lastInsertRowid: res.lastInsertRowid, changes: res.rowsAffected };
    }
  }),
  exec: (sql) => turso.execute(sql).catch(console.error)
};
"""
code = re.sub(r"const db = new Database\('videos.db'\);", turso_init, code)

# 3. Auth functions ko async karo (kyunki cloud DB me time lagta hai)
code = code.replace("function auth(req, res, next) {", "async function auth(req, res, next) {")
code = code.replace("function adminAuth(req, res, next) {", "async function adminAuth(req, res, next) {")

# 4. Saare database queries ke aage 'await' lagao
code = re.sub(r"(?<!await )db\.prepare\(", "await db.prepare(", code)

# 5. Saare routes ko async karo
code = re.sub(r"app\.(get|post|put|delete)\(([^,]+), \((req, res)\) =>", r"app.\1(\2, async (req, res) =>", code)
code = re.sub(r"app\.(get|post|put|delete)\(([^,]+), function\((req, res)\)", r"app.\1(\2, async function(req, res)", code)

with open('server.js', 'w') as f:
    f.write(code)
print("✅ Code successfully Turso Cloud Database ke liye update ho gaya!")
