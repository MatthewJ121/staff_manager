import os
import httpx
roblox_api = os.getenv('roblox_api')

from pymongo.mongo_client import MongoClient
uri = (os.getenv('URI'))
mongoclient = MongoClient(uri)
rdb = mongoclient.SilverOaks.ResidentList
bdb = mongoclient.SilverOaks.Blacklist
sdb = mongoclient.SilverOaks.StaffTracker
susdb = mongoclient.SilverOaks.StaffTracker

async def get_robloxprofile(username):
    userid_request = httpx.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}).json()["data"]
    if len(userid_request) == 0:
        raise ValueError(f"The username **{username}** was not found.")
    else:
        profile = httpx.get("https://apis.roblox.com/cloud/v2/users/"+str(userid_request[0]["id"]), headers={"x-api-key":(roblox_api)}).json()
        return profile
    
async def get_picture(userid):
    picture_request = httpx.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={str(userid)}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]
    if len(picture_request) == 0:
        raise ValueError("Unable to obtain picture")
    else:
        return picture_request

async def get_db(userid,db):
    match db:
        case "rdb":
            item = rdb.find_one({"userid": int(userid)})
            return item
        
async def get_rank(userid,type):
    ranks = {}
    rogroups = httpx.get("https://groups.roblox.com/v2/users/"+str(userid)+"/groups/roles?includeLocked=false&includeNotificationPreferences=false").json()["data"]
    if len(rogroups) == 0:
        raise ValueError("Unable to obtain group information.")
    else:
        if type == "so":
            for e in rogroups:
                if e["group"]["id"] in [32941073,10021698,8294866,8294909]:
                    ranks[e["group"]["id"]] = e["role"]["name"]
                
            print(ranks)
            return ranks
        elif type == "full":
            for e in rogroups:
                if e["group"]["id"] in [32941073,10021698,8294866,8294909]:
                    ranks[e["group"]["id"]] = e["role"]["name"]
                
            print(ranks)
            return ranks

    