curl --location 'https://telex-app.onrender.com/send-logs' --header 'Content-Type: application/json' --data '{
    "channel_id": "01951279-015e-7baa-b755-dd631bdba9bf",
    "return_url": "https://ping.telex.im/v1/return/01951279-015e-7baa-b755-dd631bdba9bf",
    "settings": [
        {
            "label": "site",
            "type": "text",
            "required": true,
            "default": "https://telex-app.onrender.com/logs"
        },
        {
            "label": "interval",
            "type": "text",
            "required": true,
            "default": "* * * * *"
        }
    ]
}'
