with open('server.js', 'r') as f:
    code = f.read()

# Direct URL aur Token (No environment variables)
direct_code = '''const turso = createClient({
  url: "libsql://velvetplay-db-gappu-chat.aws-ap-south-1.turso.io",
  authToken: "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTQ5Mjg2MTgsImlkIjoiMDFhMWU5NzctN2QwMS03ZDgxLTllZmYtMGRmYWU2MWQwNDY0Iiwia2lkIjoiVk9sQ0pMemt3WkNVWmMtQ2E4LUc4ZlQwQnhNVlJQdDlOcUZ5elRzVjhKMCIsInJpZCI6ImU2ZjVhYjk3LWEyZjMtNGJkZi04ODk4LWZkYzk5NTliMWQ3NyJ9.8ky-wmzVPiNEQC-7dRU1Z9bbJrvPKkVsGTI_8kRJGHRhTYM4PyCEoZVaDO6FqTmwce1_F9tAhqae3ILsviZeBQ",
});'''

# Purane createClient block ko naye direct code se replace karo
import re
code = re.sub(r"const turso = createClient\(\{.*?\}\);", direct_code, code, flags=re.DOTALL)

with open('server.js', 'w') as f:
    f.write(code)
print("✅ URL aur Token direct code me daal diye gaye hain!")
