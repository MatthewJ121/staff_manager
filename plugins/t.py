import httpx
import os
print(httpx.get("https://apis.roblox.com/cloud/v2/groups/32941073/roles",headers={"x-api-key":(os.getenv("roblox_api"))}))