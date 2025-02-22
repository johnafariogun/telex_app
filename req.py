import requests

url = "https://ping.telex.im/v1/webhooks/01951279-015e-7baa-b755-dd631bdba9bf"
payload = {
    "event_name": "string",
    "message": "python post",
    "status": "success",
    "username": "collins"
}

response = requests.post(
    url,
    json=payload,
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
)
print(response.json())
