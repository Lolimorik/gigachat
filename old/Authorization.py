import requests

url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

payload={
  'scope': 'GIGACHAT_API_PERS'
}

headers = {
  'Content-Type': 'application/x-www-form-urlencoded',
  'Accept': 'application/json',
  'RqUID': '7040164d-3e17-4127-a5c0-77bff34110ad',
  'Authorization': 'Basic MDE5ZjE5MjktODQ0Mi03OTNiLThlMWEtYmM0NTQ4YWM3ZjEzOjE1M2YzNDk3LTY2MmYtNDNjYi05OTU5LTUzZGIxYzRhNGUzOQ=='
}

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

print(response.text)