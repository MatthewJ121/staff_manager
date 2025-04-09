import os
import httpx
roblox_api = os.getenv('roblox_api')

from pymongo.mongo_client import MongoClient
uri = (os.getenv('URI'))
mongoclient = MongoClient(uri)

#returns profile information from username
async def get_robloxprofile(username):
    userid_request = httpx.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": True}).json()["data"]
    if len(userid_request) == 0:
        raise ValueError(f"The username **{username}** was not found.")
    else:
        profile = httpx.get("https://apis.roblox.com/cloud/v2/users/"+str(userid_request[0]["id"]), headers={"x-api-key":(roblox_api)}).json()
        return profile

# returns user profile picture
async def get_picture(userid):
    picture_request = httpx.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={str(userid)}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]
    if len(picture_request) == 0:
        raise ValueError("Unable to obtain picture")
    else:
        return picture_request

# pulls information from databases
async def get_db(userid,db):
    db_map = {       
        "rdb": mongoclient.SilverOaks.ResidentList,
        "bdb": mongoclient.SilverOaks.Blacklist,
        "sdb": mongoclient.SilverOaks.StaffTracker,
        "susdb": mongoclient.SilverOaks.StaffTracker
    }
    #remove this if statement once old bot is retired
    if db == "bdb":
        item = db_map.get(db).find({"ouid": int(userid)})
    else:
        item = db_map.get(db).find({"userid": int(userid)})
    return item

# returns role information of users
#   "so" - so ranks only
#   "full" - full rank check   
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

    