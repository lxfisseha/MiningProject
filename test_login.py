import urllib.request
import urllib.error
import http.cookiejar
import re

BASE = "https://miningproject-production-aaf6.up.railway.app"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

# Step 1: GET login page
resp = opener.open(f"{BASE}/login", timeout=20)
page = resp.read().decode()
m = re.search(r'<meta name="csrf-token" content="([^"]+)"', page)
csrf_token = m.group(1) if m else "NONE"

# Check cookies
print("Cookies after GET /login:")
for c in cj:
    print(f"  {c.name} = {c.value[:50]}...")

# Step 2: POST login
data = "email=admin%40gmail.com&password=password".encode()
req = urllib.request.Request(f"{BASE}/login", data=data, method="POST", headers={
    "Content-Type": "application/x-www-form-urlencoded",
    "X-CSRF-Token": csrf_token,
    "Origin": BASE,
    "Referer": f"{BASE}/login",
})
try:
    resp = opener.open(req, timeout=20)
    body = resp.read().decode()
    redirect = resp.headers.get("HX-Redirect", "NONE")
    print(f"\nPOST /login -> {resp.status}")
    print(f"HX-Redirect: {redirect}")
    print(f"Body ({len(body)} bytes): {body[:300]}")
    print(f"\nCookies after POST:")
    for c in cj:
        print(f"  {c.name} = {c.value[:50]}...")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"\nPOST /login -> ERROR {e.code}")
    print(f"Body: {body[:500]}")
    print(f"\nCookies:")
    for c in cj:
        print(f"  {c.name} = {c.value[:50]}...")
except Exception as e:
    print(f"\nPOST /login -> EXCEPTION: {e}")
