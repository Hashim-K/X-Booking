# localStorage Authentication Analysis

## 🎯 KEY FINDING: `delcom_auth`

The X booking system stores the complete authentication state in `localStorage` under the key `delcom_auth`.

### Authentication Token (JWT)

**Access Token** (stored in `delcom_auth.tokenResponse.accessToken`):
```
eyJraWQiOiJrZXlfMjAyNV8xMV8wMV8wMF8wMF8wMF83NTEiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...
```

**Token Type:** Bearer  
**Expires In:** 86400 seconds (24 hours)  
**Issued At:** 1763153495 (Unix timestamp)

### Token Structure
```json
{
  "member": { ... user details ... },
  "tokenResponse": {
    "accessToken": "eyJ...",
    "tokenType": "Bearer",
    "expiresIn": 86400,
    "idToken": "eyJ...",
    "issuedAt": 1763153495
  },
  "isOidc": true,
  "isLoggedIn": true
}
```

## 🚀 THIS MEANS WE CAN USE REQUESTS!

### Strategy

1. **Login once with Selenium** to get the auth token
2. **Extract `delcom_auth` from localStorage**
3. **Use the `accessToken` with requests** for API calls
4. **Set `Authorization: Bearer <token>` header**

### Implementation Plan

```python
import requests
import json
from selenium import webdriver

# Step 1: Login with Selenium
driver = webdriver.Chrome()
driver.get('https://x.tudelft.nl/')
# ... login flow ...

# Step 2: Extract token
auth_data = driver.execute_script("return window.localStorage.getItem('delcom_auth');")
auth_json = json.loads(auth_data)
access_token = auth_json['tokenResponse']['accessToken']

# Step 3: Use with requests
session = requests.Session()
session.headers.update({
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
})

# Step 4: Make API calls
response = session.get('https://x.tudelft.nl/api/bookings')
```

## 🔍 Next Steps

1. Find the actual API endpoints (they likely exist!)
2. Test if Bearer token works for API calls
3. Rewrite BookingClient to use requests instead of Selenium clicks

## 💡 Benefits

- **Much faster** - no browser automation for each action
- **Lower resource usage** - just HTTP calls
- **Easier to parallelize** - can make multiple requests
- **Better for automation** - pure Python, no Selenium complexity

## 🎉 Conclusion

**YES, we can use `requests` for most operations!**

We only need Selenium for the initial OIDC login to get the token.  
After that, everything can be pure HTTP requests with the Bearer token!
