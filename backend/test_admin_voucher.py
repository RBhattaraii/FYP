import requests

url = "http://localhost:8000/points/vouchers/admin/create"
headers = {"Content-Type": "application/json", "Authorization": "Bearer mock-token"}
payload = {
    "voucher_code": "SUMMER2026",
    "discount_type": "fixed_amount",
    "discount_amount": 500,
    "minimum_spend": 0,
    "usage_limit": 100,
    "expires_in_days": 30
}

response = requests.post(url, json=payload, headers=headers)
print(response.status_code)
print(response.json())
