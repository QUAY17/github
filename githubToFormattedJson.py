from html import entities
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

gh_user="QUAY17"
gh_token="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"
gh_repo="tensorflow/tensorflow"

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

# get all user Commits dynamically
def commit_type(login, gh_user, gh_token):
    # Get all Commits dynamically
    commitCountUrl = f"https://api.github.com/search/commits?q=author:{login}&sort=author-date&order=desc&page=1%27"
    gitHubAPI_URL_getCommitCount = f"{commitCountUrl}"
    response = requests.get(gitHubAPI_URL_getCommitCount, auth=(gh_user, gh_token))
    userCommits = response.json()
    if userCommits["total_count"]:
        commits = userCommits["total_count"]
        if commits < 10000:
            commit_type = "light committer"
        else:
            commit_type = "heavy committer"
    else:
        commit_type = None
    return commit_type

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
            issueContext = issueTitle+ ". "+issueMessage # Issue title + body
            issueNumber = attribute["number"] # To match issue and pr
            issueCreatedAt = attribute["created_at"] # Timestamp
            issueUserLogin = attribute["user"]["login"] 
            login = issueUserLogin # Login to follow url for number of commits
            committerType = commit_type(login, gh_user, gh_token)
            issueUserId = attribute["user"]["id"] # Entity Ids []
            entityId = issueUserId
            type = "Issue Creator"
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

            issueDict = {"Timestamp":issueCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":issueContext}

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
                    pullUserLogin = attribute["user"]["login"] 
                    login = pullUserLogin # Login to follow url for number of commits
                    committerType = commit_type(login, gh_user, gh_token)
                    entityId = pullUserId
                    type = "Pull Requestor"
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

                    prDict = {"Timestamp":pullCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational IDs":relationalalIds, "Context":prContext}

                    data.append(prDict)
    

    # Header info ___________________________________________________________________________________

    dataName = "Github Data for Tensorflow"
    dataCreation = "2015-11-07T01:19:20Z"
    dataStart = issues[-1]["created_at"]
    dataEnd = issues[0]["created_at"]
    dataVersion = 1.0
    dataOrigin = "Utlizes data/gh_Issues.json, data/gh_Pulls.json and dynamic requests to the Github API"

    # predicted symbols
    tbd = "tbd"
    predSym = [tbd]

    # entities
    dataEntities = [] # entities list
    valid = ""
    symbols = [] #symbols list
    symDict = {"contribution type": type, "valid from": valid, "valid to": valid}
    symbols.append(symDict)
    properties = [] # properties list
    propDict = {"committer type": committerType, "valid from": valid, "valid to": valid}
    properties.append(propDict)
    entDict = {"id": entityId, "symbols":symbols, "properties":properties}
    dataEntities.append(entDict)

    
    # Header info ___________________________________________________________________________________
    
    githubDataFormatted = {"Data Name":dataName, "Creation Date":dataCreation, "Data Range Start":dataStart, "Data Range End":dataEnd, "Version Information":dataVersion, "Provenance Information":dataOrigin, "Predicted Symbols":predSym, "Prediction Period": tbd, "Entities": dataEntities, "Properties": tbd, "data":data}
    
    with open(argv[3], "wt") as outFile:
        json.dump(githubDataFormatted, outFile, indent=4)