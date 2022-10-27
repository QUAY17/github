from html import entities
import json
import os
from sys import argv
from urllib.request import urlopen
import requests
from datetime import datetime
import random
import string
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
    commitCountUrl = f"https://api.github.com/search/commits?q=author:{login}&sort=author-date&order=desc&page=1%27"
    gitHubAPI_URL_getCommitCount = f"{commitCountUrl}"
    response = requests.get(gitHubAPI_URL_getCommitCount, auth=(gh_user, gh_token))
    userCommits = response.json()
    print("\n\n", userCommits)

    if userCommits["total_count"]:
        commits = userCommits["total_count"]
        if commits < 2500:
            commit_type = "Light Committer"
        else:
            commit_type = "Heavy Committer"
    elif userCommits["message"]:
        commit_type = None
    else:
        commit_type = None

    return commit_type

# get follower count dynamically
def follow_type(login, gh_user, gh_token):
    followerCountUrl = f"https://api.github.com/users/{login}/followers"
    gitHubAPI_URL_getFollowerCount = f"{followerCountUrl}"
    response = requests.get(gitHubAPI_URL_getFollowerCount, auth=(gh_user, gh_token))
    userFollowers = response.json()
    count = len(userFollowers)
    if count < 10:
        followingType = "Less Followers"
    elif count >= 10 and count < 25:
        followingType = "Average Followers"
    else:
        followingType = "More Followers"
    return followingType

if __name__ == "__main__":
    if len(argv) != 4:
        usage()

    with open(argv[1], "rt") as issuesJson: # Issues
        issues = json.load(issuesJson)

    data = []
    dataEntities = []

    # Issues ___________________________________________________________________________________

    for attribute in issues[0:75]:
        # Issue Creation
        relationalalIds = []
        if attribute["created_at"]:
            issueTitle = attribute["title"] # Issue Title
        if attribute["body"]: # Issue Body
            issueMessage = attribute["body"] 
            issueContext = issueTitle+ ". "+issueMessage # Issue title + body
            issueNumber = attribute["number"] # To match issue and pr
            issueCreatedAt = attribute["created_at"] # Timestamp created
            issueClosedAt = attribute["closed_at"] # Timestamp closed
            issueUserLogin = attribute["user"]["login"] 
                
            login = issueUserLogin # Login to follow url for user stats
            committerType = commit_type(login, gh_user, gh_token)
            followingType = follow_type(login, gh_user, gh_token)

            # User date range
            issueUserUrl = attribute["user"]["url"]
            gitHubAPI_URL_getUserDates = f"{issueUserUrl}"
            response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
            dataUser = response.json()
            if dataUser["created_at"]:
                userCreatedAt = dataUser["created_at"] # valid from
            if dataUser["updated_at"]:
                userUpdatedAt = dataUser["updated_at"] # valid to: "updated" is the timestamp of the last activity
            issueUserId = attribute["user"]["id"] # Entity Ids []
            entityId = issueUserId
            contributeType = "Issue Creator"

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

            symbols = [] #symbols list
            symIssue = {"Contribution Type": contributeType, "Valid From": issueCreatedAt, "Valid To": issueClosedAt}
            symbols.append(symIssue)

            properties = [] # properties list
            propDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
            properties.append(propDict)

            entDict = {"Id": entityId, "Symbols":symbols, "Properties":properties}
            dataEntities.append(entDict)

            issueData = {"Timestamp":issueCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":issueContext}

            #dataEntities.append(dataIssueEntities)    
            data.append(issueData)

            # Pulls ___________________________________________________________________________________

        with open(argv[2], "rt") as pullsJson: # Pulls
            pulls = json.load(pullsJson)

        for attribute in pulls:        
            # PR Creation
            pullNumber = attribute["number"]
            if pullNumber == issueNumber:
                prTitle = attribute["title"] # PR Title
                if attribute["body"]: # PR Body
                    prMessage = attribute["body"] # PR Body
                    prContext = prTitle+ ". "+prMessage
                pullCreatedAt = attribute["created_at"] # Timestamp created at
                pullClosedAt = attribute["closed_at"] # Timestamp closed at
                pullUserId = attribute["user"]["id"]
                pullUserLogin = attribute["user"]["login"] 
                
                login = pullUserLogin # Login to follow url for number of commits
                committerType = commit_type(login, gh_user, gh_token)
                entityId = pullUserId

                contributeType = "Pull Requestor"
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

                symPull = {"Contribution Type": contributeType, "Valid From": pullCreatedAt, "Valid To": pullClosedAt}
                symbols.append(symPull)

                #entDict = {"Symbols":symbols}
                #dataEntities.append(entDict)

                prData = {"Timestamp":pullCreatedAt, "Entity Ids":entityIds, "Symbol":eventName, "Relational IDs":relationalalIds, "Context":prContext}

                data.append(prData)


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

    # _________________________________________________________________________________________________

    githubDataFormatted = {"Data Name":dataName, "Creation Date":dataCreation, "Data Range Start":dataStart, "Data Range End":dataEnd, "Version Information":dataVersion, "Provenance Information":dataOrigin, "Predicted Symbols":predSym, "Prediction Period": tbd, "Entities": dataEntities, "Data":data}

    with open(argv[3], "wt") as outFile:
        json.dump(githubDataFormatted, outFile, indent=4)