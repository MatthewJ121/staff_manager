import os
import httpx
import json
roblox_api = os.getenv('roblox_api')
admin_api = os.getenv('admin_key')
rel_api = os.getenv('relations_key')
sec_api = os.getenv('security_key')

egg_key = os.getenv("egg_key")

from pymongo.mongo_client import MongoClient
uri = (os.getenv('URI'))
mongoclient = MongoClient(uri)
rdb = mongoclient.SilverOaks.ResidentList
bdb = mongoclient.SilverOaks.Blacklist
sdb = mongoclient.SilverOaks.StaffTracker
susdb = mongoclient.SilverOaks.SuspensionTracker

db_map = {       
    "rdb": rdb,
    "bdb": bdb,
    "sdb": sdb,
    "susdb": susdb
}



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
def get_db(userid,db):
    #remove this if statement once old bot is retired
    if db == "bdb":
        item = db_map.get(db).find_one({"ouid": int(userid)})
    else:
        item = db_map.get(db).find_one({"userid": int(userid)})
    return item


# get membership id
# dont ask me how it works lol
async def get_memberid(groupid,userid):
    id = None
    page_token = ""
    while id == None:
        mrequest = httpx.get(f"https://apis.roblox.com/cloud/v2/groups/{groupid}/memberships?maxPageSize=100&pageToken={page_token}",headers={"x-api-key":(egg_key)}).json()
        page_token = mrequest["nextPageToken"]
        mlist = mrequest["groupMemberships"]
        for member_object in mlist:
            if member_object["user"] == f"users/{userid}":
                id = int(member_object["user"].split("/")[1])
                print(id)
        print("looping again")

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
                    ranks[e["group"]["id"]] = e["role"]
                
            print(ranks)
            return ranks
        elif type == "full":
            for e in rogroups:
                if e["group"]["id"] in [32941073,10021698,8294866,8294909]:
                    ranks[e["group"]["id"]] = e["role"]
                
            print(ranks)
            return ranks

#group_set = {"m": 32941073,"r": 10021698,"s": 8294866,"a": 8294909}
async def set_rank(userid, groupid, rankid):
    try:
        print(httpx.patch(f"https://apis.roblox.com/cloud/v2/groups/{groupid}/memberships/{userid}",headers={"Content-Type": "application/json","x-api-key":(egg_key)},data=json.dumps({"role":f"groups/{groupid}/roles/{rankid}"})))
    except Exception as e:
        print(e)