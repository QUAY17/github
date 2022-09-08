import json
import os
from sys import argv
from urllib.request import urlopen
import requests
from datetime import datetime
import random
import string
import hashlib

def usage():
    print("python githubToJson.py gh_Issues.json gh_Pulls.json finalOutFile.json")
    print("\tgh_Issues.json - the Issues json file")
    print("\tgh_Pulls.json - the Pulls json file")
    print("\tfinalOutFile.json - a json file that will contain all the Github data we find useful")
    exit(0)

# generation of relational ID
def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# anonymizing entity ID
def salt_hash_id(issueUserId):
    githubId = issueUserId
    salt = os.urandom(32)
    new_id = githubId+salt
    hashed = hashlib.md5(new_id.encode())
    return hashed

if __name__ == "__main__":
    if len(argv) != 4:
        usage()

    with open(argv[1], "rt") as issuesJson:
        issues = json.load(issuesJson)
   
    dataData = []

    for attribute in issues[:100]:
        issueCreatedAt = attribute["created_at"]
        issueUserId = attribute["user"]["id"]
        anonUserId = salt_hash_id(issueUserId)
        eventUrl = attribute["events_url"]
        issueId = id_generator()
        message= attribute["body"]

        gh_user="QUAY17"
        gh_token="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"

        gitHubAPI_URL_getEvents = f"{eventUrl}"
        response = requests.get(gitHubAPI_URL_getEvents, auth=(gh_user, gh_token))
        issueComment = response.json()


    
        dataDict = {"Timestamp":issueCreatedAt, "EntityId":anonUserId, "Symbol":eventName, "Relational IDs":issueId, "Context":message}


    # Header info ___________________________________________________________________________________

    dataName = "Github Data for Tensorflow"
    dataDate = "2015-11-07T01:19:20Z"
    dataStart = issueCreatedAt[0]
    dataEnd = issueCreatedAt[-1]
    dataVersion = 1.0
    dataOrigin = "Utlizes data/gh_Issues.json, gh_Pulls.json and dynamic requests to the Github API"

        
    githubDataFormatted = {"Data Name":dataName, "Creation Date":dataDate, "Data Range Start":dataStart, "Data Range End":dataEnd,
            "Version Information":dataVersion, "Provenance Information":dataOrigin, "data":dataData}
