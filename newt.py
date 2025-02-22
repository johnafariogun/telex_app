import asyncio
import httpx
logs =[[{'id':1, 'name':'john','data':'chehsjjsck it out'}]]

data = {
        "message": str(logs),  # Sending logs as the message
        "username": "Log Monitor",
        "event_name": "Log Report",
        "status": "success" if logs else "error"
    }
async def test():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://ping.telex.im/v1/return/01951279-015e-7baa-b755-dd631bdba9bf", json=data)
            print(response.json())
        except Exception as e:
            return str(e)
asyncio.run(test())
