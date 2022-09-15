import json
import os
from sys import argv
from urllib.request import urlopen
import requests
from datetime import datetime
import random
import string
import hashlib
import bcrypt

def usage():
    print("python githubToJson.py gh_Issues.json gh_Pulls.json finalOutFile.json")
    print("\tgh_Issues.json - the Issues json file")
    print("\tgh_Pulls.json - the Pulls json file")
    print("\tfinalOutFile.json - a json file that will contain all the Github data we find useful")
    exit(0)

# generates relational ID
def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# anonymizes entity ID
def salt_hash_id(issueUserId):
    githubId = str(issueUserId).encode()
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(githubId, salt)
    return hash[:16]

if __name__ == "__main__":
    if len(argv) != 4:
        usage()

    with open(argv[1], "rt") as issuesJson: # Issues
        issues = json.load(issuesJson)

    data = []
    
    for attribute in issues[:10]:
    # Issue Creation
        relationalalIds = []
        if attribute["created_at"]:
            issueTitle = attribute["title"] # Issue Title
            issueMessage = attribute["body"] # Issue Body
            issueContext = issueTitle+ ". "+issueMessage
            issueNumber = attribute["number"] # To match issue and pr
            issueCreatedAt = attribute["created_at"] # Timestamp
            issueUserId = attribute["user"]["id"] # Entity Ids []
            #issueUserId = salt_hash_id(issueUserId)
            entityIds = []
            entityIds.append(issueUserId)
            issueAssignees = attribute["assignees"]
            for attribute in issueAssignees:
                issueAssigneesId = attribute["id"]
                #issueAssigneesId = salt_hash_id(issueAssigneesId)
                entityIds.append(issueAssigneesId)
            eventName = "Issue Creation" # Symbol Name
            issueId = id_generator() # Issue Id
            sameIssueId = issueId # when we need id to be the same for multiple events
            relationalalIds.append(issueId)

            issueDict = {"Issue Number":issueNumber,"Timestamp":issueCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":issueContext}

            data.append(issueDict)

            with open(argv[2], "rt") as pullsJson: # Pulls
                pulls = json.load(pullsJson)

            for attribute in pulls:        
            # PR Creation
                pullNumber = attribute["number"]
                if pullNumber == issueNumber:
                    prTitle = attribute["title"] # PR Title
                    prMessage = attribute["body"] # PR Body
                    prContext = prTitle+ ". "+prMessage
                    pullCreatedAt = attribute["created_at"]
                    pullUserId = attribute["user"]["id"]
                    entityIds = []
                    entityIds.append(pullUserId)
                    pullAssignees = attribute["assignees"]
                    pullReviewers = attribute["requested_reviewers"] 
                    for attribute in pullAssignees:
                        pullAssigneesId = attribute["id"]
                        entityIds.append(pullAssigneesId)
                    for attribute in pullReviewers:
                        pullReviewersId = attribute["id"]
                        entityIds.append(pullReviewersId)
                    eventName = "Pull Request Creation" # Symbol Name
                    prId = id_generator() # Pull Request Id
                    samePrId = prId # when we need id to be the same for multiple events
                    relationalalIds = [sameIssueId, prId]

                    prDict = {"Pull Number": pullNumber,"Timestamp":pullCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational IDs":relationalalIds, "Context":prContext}

                    data.append(prDict)

    # Header info ___________________________________________________________________________________

    dataName = "Github Data for Tensorflow"
    dataDate = "2015-11-07T01:19:20Z"
    dataStart = issues[-1]["created_at"]
    dataEnd = issues[0]["created_at"]
    dataVersion = 1.0
    dataOrigin = "Utlizes data/gh_Issues.json, gh_Pulls.json and dynamic requests to the Github API"

    # Header info ___________________________________________________________________________________
    
    githubDataFormatted = {"Data Name":dataName, "Creation Date":dataDate, "Data Range Start":dataStart, "Data Range End":dataEnd, "Version Information":dataVersion, "Provenance Information":dataOrigin, "data":data}
    
    with open(argv[3], "wt") as outFile:
        json.dump(githubDataFormatted, outFile, indent=4)