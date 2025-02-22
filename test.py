import asyncio
import httpx
logs =[[{'id':1, 'name':'john','data':'check it out'}]]

data = {
        "message": logs,  # Sending logs as the message
        "username": "Log Monitor",
        "event_name": "Log Report",
        "status": "success" if logs else "error"
    }
async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://ping.telex.im/v1/webhooks/01951279-015e-7baa-b755-dd631bdba9bf", json=data)
            if response.status_code < 400:
                print("sent to telex")
            else:
                print("not sent")
        except Exception as e:
            return str(e)
asyncio.run(test())
