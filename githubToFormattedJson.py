import json
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
    if "total_count" not in userCommits: # this occurs when a user is private/ isn't found
        commit_type = None
    elif userCommits["total_count"]:
        commits = userCommits["total_count"]
        if commits < 2500:
            commit_type = "Light Committer"
        else:
            commit_type = "Heavy Committer"
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

# get merged by info
def merger_id(pullNumber, gh_user, gh_token):
    pullByUrl = f"https://api.github.com/repos/tensorflow/tensorflow/pulls/{pullNumber}"
    gitHubAPI_URL_getMergerId = f"{pullByUrl}"
    response = requests.get(gitHubAPI_URL_getMergerId, auth=(gh_user, gh_token))
    getMergerId = response.json()
    if "merged_by" in getMergerId:
        pullMergerId = getMergerId["merged_by"]["id"] # Pull merger id
        return pullMergerId

def merger_login(pullNumber, gh_user, gh_token):
    pullByUrl = f"https://api.github.com/repos/tensorflow/tensorflow/pulls/{pullNumber}"
    gitHubAPI_URL_getMergerLogin = f"{pullByUrl}"
    response = requests.get(gitHubAPI_URL_getMergerLogin, auth=(gh_user, gh_token))
    getMergerLogin = response.json()
    if "merged_by" in getMergerLogin:
        pullMergerLogin = getMergerLogin["merged_by"]["login"] # Pull merger login
        print("in func", pullMergerLogin)
        return pullMergerLogin

def merger_url(pullNumber, gh_user, gh_token):
    pullByUrl = f"https://api.github.com/repos/tensorflow/tensorflow/pulls/{pullNumber}"
    gitHubAPI_URL_getMergedId = f"{pullByUrl}"
    response = requests.get(gitHubAPI_URL_getMergedId, auth=(gh_user, gh_token))
    getMergerUrl = response.json()
    if "merged_by" in getMergerUrl:
        pullMergerUserUrl = getMergerUrl["merged_by"]["url"] # Pull merger url
        print("in func", pullMergerUserUrl)
        return pullMergerUserUrl


if __name__ == "__main__":
    if len(argv) != 4:
        usage()

    with open(argv[1], "rt") as issuesJson: # Issues
        issues = json.load(issuesJson)

    data = []
    dataEntities = []

    # Issues ___________________________________________________________________________________

    for attribute in issues[0:50]:
        # Issue Creation
        relationalalIds = []
        if attribute["created_at"]:
            issueTitle = attribute["title"] # Issue Title
            issueNumber = attribute["number"] # To match issue and pr
            print(issueNumber)
            issueCreatedAt = attribute["created_at"] # Timestamp created
            issueClosedAt = attribute["closed_at"] # Timestamp closed
            issueUserLogin = attribute["user"]["login"] 
            issueUserId = attribute["user"]["id"] # Entity Ids []
            entityId = issueUserId
            contributeType = "Issue Creator"
            if attribute["body"]: # Issue Body
                issueMessage = attribute["body"] 
                issueContext = issueTitle+ ". "+issueMessage # Issue title + body
    
            #login = issueUserLogin # Login to follow url for user stats
            committerType = commit_type(issueUserLogin, gh_user, gh_token)
            followingType = follow_type(issueUserLogin, gh_user, gh_token)

            # User date range
            issueUserUrl = attribute["user"]["url"]
            gitHubAPI_URL_getUserDates = f"{issueUserUrl}"
            response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
            dataUser = response.json()
            #print("\n\n", dataUser)
            if "created_at" not in dataUser: # this occurs when api returns a message that user isn't found
                userCreatedAt = None
                userUpdatedAt = None
            elif dataUser["created_at"]:
                userCreatedAt = dataUser["created_at"] # valid from
                userUpdatedAt = dataUser["updated_at"] # "updated" is the timestamp of the last activity

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

        for attribute in pulls: # PR Creation
            pullNumber = attribute["number"]
            if pullNumber == issueNumber:
                prTitle = attribute["title"] # PR Title
                if attribute["body"]: # PR message body
                    prMessage = attribute["body"] 
                    prContext = prTitle+ ". "+prMessage  
                pullCreatedAt = attribute["created_at"] # Timestamp created at
                pullClosedAt = attribute["closed_at"] # Timestamp closed at
                pullMergedAt = attribute["merged_at"] # Merged at
                pullUserId = attribute["user"]["id"] # Pull Creator Id
                pullUserLogin = attribute["user"]["login"]
                #login = pullUserLogin # Login to follow url
                committerType = commit_type(pullUserLogin, gh_user, gh_token)

                # Pull Requestor _____________________________________________________________________
                
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

                prData = {"Timestamp":pullCreatedAt, "Entity Ids":entityIds, "Symbol":eventName, "Relational IDs":relationalalIds, "Context":prContext}
                data.append(prData)

                # Pull Merger/Closer  _____________________________________________________________________

                if pullMergedAt is not None:
                    pullMergerId = merger_id(pullNumber, gh_token, gh_user)
                    print("pull 2 block",pullMergedAt, pullMergerId)
                    contributeType = "Pull Merger"
                    entityIds = []
                    entityIds.append(pullMergerId)
                    eventName = "Pull Request Merged" # Symbol Name
                    prMergeId = id_generator() # Pull Request Id
                    samePrMergeId = prMergeId # when we need id to be the same for multiple events
                    relationalalIds = [sameIssueId, samePrId, prMergeId]

                    # Symbols
                    symbols = []
                    symMerge = {"Contribution Type": contributeType, "Valid From": pullMergedAt, "Valid To": pullClosedAt}
                    symbols.append(symMerge)

                    # Properties this should be a function ?
                    mergerLogin =  merger_login(pullNumber, gh_user, gh_token)
                    #login = mergerLogin # Login to follow url for user stats
                    committerType = commit_type(mergerLogin, gh_user, gh_token)
                    followingType = follow_type(mergerLogin, gh_user, gh_token)
                    # User date range
                    mergerUrl = merger_url(pullNumber, gh_user, gh_token)
                    if mergerUrl is not None:
                        gitHubAPI_URL_getUserDates = f"{mergerUrl}"
                        response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
                        dataUser = response.json()
                        if "created_at" not in dataUser: # this occurs when api returns a message that user isn't found or a bot profile
                            userCreatedAt = None
                            userUpdatedAt = None
                        elif dataUser["created_at"]:
                            userCreatedAt = dataUser["created_at"] # valid from
                            userUpdatedAt = dataUser["updated_at"] # "updated" is the timestamp of the last activity
                    else: # error handling, not sure edge case
                        userCreatedAt = None
                        userUpdatedAt = None

                    properties = [] # properties list
                    propMergeDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
                    properties.append(propMergeDict)

                    entMergeDict = {"Id": pullMergerId, "Symbols":symbols, "Properties":properties}
                    dataEntities.append(entMergeDict)

                    prMergeData = {"Timestamp":pullMergedAt, "Entity Ids":entityIds, "Symbol":eventName, "Relational IDs":relationalalIds, "Context":prContext}
                    data.append(prMergeData)
                
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