import requests
res = requests.get("https://www.cgdigital.com.np/api/get/categories")
if res.status_code == 200:
    print(res.json().get('data'))
