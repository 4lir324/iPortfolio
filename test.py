import requests

CMC_API_KEY = "69445e7c-3e87-4b37-a576-b6b3fc5dd0c3"

def test_get_current_price(contract_address):
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    params = {
        "symbol": contract_address,  # یا بررسی کنید شاید نیاز به تغییر پارامترها باشد.
        "convert": "USD"
    }
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": CMC_API_KEY
    }

    response = requests.get(url, headers=headers, params=params)
    print(response.status_code)
    print(response.json())

# به جای "BTC" یکی از مقادیر واقعی خود را وارد کنید.
test_get_current_price("BTC")