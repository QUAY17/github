import json
from sys import argv
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

# get merger id- was truncated from json
def merger_id(pullNumber, gh_user, gh_token):
    pullByUrl = f"https://api.github.com/repos/tensorflow/tensorflow/pulls/{pullNumber}"
    gitHubAPI_URL_getMergerId = f"{pullByUrl}"
    response = requests.get(gitHubAPI_URL_getMergerId, auth=(gh_user, gh_token))
    getMergerId = response.json()
    if "merged_by" in getMergerId:
        pullMergerId = getMergerId["merged_by"]["id"] # Pull merger id
        return pullMergerId
# get merger login- was truncated from json
def merger_login(pullNumber, gh_user, gh_token):
    pullByUrl = f"https://api.github.com/repos/tensorflow/tensorflow/pulls/{pullNumber}"
    gitHubAPI_URL_getMergerLogin = f"{pullByUrl}"
    response = requests.get(gitHubAPI_URL_getMergerLogin, auth=(gh_user, gh_token))
    getMergerLogin = response.json()
    if "merged_by" in getMergerLogin:
        pullMergerLogin = getMergerLogin["merged_by"]["login"] # Pull merger login
        return pullMergerLogin
# get merger url- was truncated from json
def merger_url(pullNumber, gh_user, gh_token):
    pullByUrl = f"https://api.github.com/repos/tensorflow/tensorflow/pulls/{pullNumber}"
    gitHubAPI_URL_getMergedId = f"{pullByUrl}"
    response = requests.get(gitHubAPI_URL_getMergedId, auth=(gh_user, gh_token))
    getMergerUrl = response.json()
    if "merged_by" in getMergerUrl:
        pullMergerUserUrl = getMergerUrl["merged_by"]["url"] # Pull merger url
        return pullMergerUserUrl


if __name__ == "__main__":
    if len(argv) != 4:
        usage()

    with open(argv[1], "rt") as issuesJson: # Issues
        issues = json.load(issuesJson)

    data = []
    dataEntities = []

    # Issues ___________________________________________________________________________________

    for attribute in issues[0:20]:
        relationalalIds = []
        if attribute["created_at"]:
            issueTitle = attribute["title"] # Issue Title
            issueNumber = attribute["number"] # To match issue and pr
            print(issueNumber)
            issueCreatedAt = attribute["created_at"] # Timestamp created
            issueClosedAt = attribute["closed_at"] # Timestamp closed
            issueUserLogin = attribute["user"]["login"] 
            issueUserId = attribute["user"]["id"] # Entity Ids []
            issueCommentsUrl = attribute["comments_url"]

            # Issue Creation ___________________________________________________________________________
            
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

            issueSymbols = [] #symbols list
            symIssue = {"Contribution Type": contributeType, "Valid From": issueCreatedAt, "Valid To": issueClosedAt}
            issueSymbols.append(symIssue)

            properties = [] # properties list
            propDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
            properties.append(propDict)

            entDict = {"Id": entityId, "Symbols":issueSymbols, "Properties":properties}
            dataEntities.append(entDict)

            issueData = {"Timestamp":issueCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":issueContext}

            data.append(issueData)

            # Issue Comments ___________________________________________________________________________
            
            gitHubAPI_URL_getIssueComments = f"{issueCommentsUrl}"
            response = requests.get(gitHubAPI_URL_getIssueComments, auth=(gh_user, gh_token))
            issueComment = response.json()
            if issueComment != None:
                for attribute in issueComment:
                    issueCommenterId = attribute["user"]["id"]
                    issueCommenterLogin = attribute["user"]["login"]
                    commentCreatedAt = attribute["created_at"]
                    commentUpdatedAt = attribute["updated_at"]
                    entityId = issueCommenterId
                    contributeType = "Issue Commenter"
                    if attribute["body"]: # Comment Body
                        commentMessage = attribute["body"] 
                    committerType = commit_type(issueCommenterLogin, gh_user, gh_token)
                    followingType = follow_type(issueCommenterLogin, gh_user, gh_token)
                    # User date range
                    issueCommenterUrl = attribute["user"]["url"]
                    gitHubAPI_URL_getUserDates = f"{issueCommenterUrl}"
                    response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
                    dataUser = response.json()
                    if "created_at" not in dataUser: # this occurs when api returns a message that user isn't found
                        userCreatedAt = None
                        userUpdatedAt = None
                    elif dataUser["created_at"]:
                        userCreatedAt = dataUser["created_at"] # valid from
                        userUpdatedAt = dataUser["updated_at"] # "updated" is the timestamp of the last activity
                    #issueUserId = salt_hash_id(issueUserId)
                    eventName = "Issue Comment" # Symbol Name
                    #issueCommentId = id_generator() # Issue Id
                    #sameCommentIssueId = issueCommentId # when we need id to be the same for multiple events
                    #relationalalIds.append(issueCommentId)

                    if issueCommenterId != issueUserId:
                        symbols = [] #symbols list
                        properties = [] # properties list
                        entityIds.append(issueCommenterId) # adds commenters id to entity list
                        propCommentDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
                        properties.append(propCommentDict)
                        entCommentDict = {"Id": entityId, "Symbols":symbols, "Properties":properties}
                        dataEntities.append(entCommentDict)
                        symIssueComment = {"Contribution Type": contributeType, "Valid From": commentCreatedAt, "Valid To": commentUpdatedAt}
                        symbols.append(symIssueComment)
                        issueCommentData = {"Timestamp":commentCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":commentMessage}
                        data.append(issueCommentData)
                    else: 
                        symIssueComment = {"Contribution Type": contributeType, "Valid From": commentCreatedAt, "Valid To": commentUpdatedAt}
                        issueSymbols.append(symIssueComment)
                        issueCommentData = {"Timestamp":commentCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":commentMessage}
                        data.append(issueCommentData)

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
                entityId = pullUserId # for the pr dict
                pullUserLogin = attribute["user"]["login"]
                pullUserUrl = attribute["user"]["url"]
                pullCommitUrl = attribute["commits_url"]

                # Pull Requestor _____________________________________________________________________

                contributeType = "Pull Request"
                eventName = "Pull Request" # Symbol Name
                if pullUserId != issueUserId: # pretty sure all issue creators are the pull requestors but just in case they are not the same/ edge case
                    committerType = commit_type(pullUserLogin, gh_user, gh_token)
                    followingType = follow_type(pullUserLogin, gh_user, gh_token)
                    # User date range
                    pullUserUrl = attribute["user"]["url"]
                    gitHubAPI_URL_getUserDates = f"{pullUserUrl}"
                    response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
                    dataUser = response.json()
                    if "created_at" not in dataUser: # this occurs when api returns a message that user isn't found
                        userCreatedAt = None
                        userUpdatedAt = None
                    elif dataUser["created_at"]:
                        userCreatedAt = dataUser["created_at"] # valid from
                        userUpdatedAt = dataUser["updated_at"] # "updated" is the timestamp of the last activity
                    #issueUserId = salt_hash_id(issueUserId)
                    entityIds.append(pullUserId) # adds requestors id to entity list
                    symbols = [] #symbols list
                    properties = [] # properties list
                    propPullReqDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
                    properties.append(propPullReqDict)
                    entPullReqDict = {"Id": entityId, "Symbols":symbols, "Properties":properties}
                    dataEntities.append(entPullReqDict)
                    symPullReq = {"Contribution Type": contributeType, "Valid From": pullCreatedAt, "Valid To": pullClosedAt}
                    symbols.append(symPullReq)
                    pullReqData = {"Timestamp":pullCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":prContext}
                    data.append(pullReqData)
                else:
                    symPullReq = {"Contribution Type": contributeType, "Valid From": pullCreatedAt, "Valid To": pullClosedAt}
                    issueSymbols.append(symPullReq)
                    pullReqData = {"Timestamp":pullCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":prContext}
                    data.append(pullReqData)
                
                # Pull Review Comments  ___________________________________________________________________

                pullCommentUrl = attribute["review_comments_url"]
                contributeType = "Pull Commenter"
                eventName = "Pull Request Comment"
                gitHubAPI_URL_getPRComments = f"{pullCommentUrl}"
                response = requests.get(gitHubAPI_URL_getPRComments, auth=(gh_user, gh_token))
                dataPRComment = response.json()
                for attribute in dataPRComment:
                    if "user" != None:
                        pullCommentLogin = attribute["user"]["login"]
                        pullCommentId = attribute["user"]["id"]
                        entityId = pullCommentId
                        commentCreatedAt = attribute["created_at"]
                        commentUpdatedAt = attribute["updated_at"]
                        commentContext = attribute["body"]
                        if pullCommentId != pullUserId:
                            committerType = commit_type(pullCommentLogin, gh_user, gh_token)
                            followingType = follow_type(pullCommentLogin, gh_user, gh_token)
                            # User date range
                            if attribute["user"] is not None:
                                pullCommitterUrl = attribute["user"]["url"]
                                gitHubAPI_URL_getUserDates = f"{pullCommitterUrl}"
                                response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
                                dataUser = response.json()
                                if "created_at" not in dataUser: # this occurs when api returns a message that user isn't found
                                    userCreatedAt = None
                                    userUpdatedAt = None
                                elif dataUser["created_at"]:
                                    userCreatedAt = dataUser["created_at"] # valid from
                                    userUpdatedAt = dataUser["updated_at"] # "updated" is the timestamp of the last activity
                            #issueUserId = salt_hash_id(issueUserId)
                            entityIds.append(pullCommentId)
                            symbols = [] #symbols list
                            properties = [] # properties list
                            propPullCommentDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
                            properties.append(propPullCommentDict)
                            entPullCommentDict = {"Id": entityId, "Symbols":symbols, "Properties":properties}
                            dataEntities.append(entPullCommentDict)
                            symPullComment = {"Contribution Type": contributeType, "Valid From": commentCreatedAt, "Valid To": commentUpdatedAt}
                            symbols.append(symPullComment)
                            pullCommentData = {"Timestamp":commentCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":commentContext}
                            data.append(pullCommentData)
                        else:
                            symPullComment = {"Contribution Type": contributeType, "Valid From": commentCreatedAt, "Valid To": commentUpdatedAt}
                            issueSymbols.append(symPullComment)
                            pullCommentData = {"Timestamp":commentCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":commentContext}
                            data.append(pullCommentData)

                # Pull Commits ____________________________________________________________________________

                if pullCommitUrl != None:
                    contributeType = "Pull Commiter"
                    eventName = "Pull Request Commit" # Symbol Name
                    gitHubAPI_URL_getCommits = f"{pullCommitUrl}"
                    response = requests.get(gitHubAPI_URL_getCommits, auth=(gh_user, gh_token))
                    dataCommit = response.json()
                    for attribute in dataCommit:
                        if "commit" != None: # if a commit exists
                            pullCommitLogin = attribute["commit"]["author"]["name"]
                        if attribute["author"] is not None:
                            pullCommitId = attribute["author"]["id"]
                            pullCommitLogin = attribute["author"]["login"]
                        else:
                            userEmail = attribute["commit"]["author"]["email"]
                            userUrlEmail = f"https://api.github.com/search/users?q={userEmail}"
                            gitHubAPI_URL_getUser = f"{userUrlEmail}"
                            response = requests.get(gitHubAPI_URL_getUser, auth=(gh_user, gh_token))
                            dataUser = response.json()
                            if dataUser["items"] != []: # api does not return user, thus returns an empty list 
                                pullCommitId = dataUser["items"]["id"]
                            else:
                                pullCommitId = None
                        entityId = pullCommitId # for the pr dict
                        commitCreatedAt = attribute["commit"]["author"]["date"]
                        commitClosedAt = None
                        commitContext = attribute["commit"]["message"]
                        if pullCommitId != pullUserId:
                            committerType = commit_type(pullCommitLogin, gh_user, gh_token)
                            followingType = follow_type(pullCommitLogin, gh_user, gh_token)
                            # User date range
                            if attribute["author"] is not None:
                                pullCommitterUrl = attribute["author"]["url"]
                                gitHubAPI_URL_getUserDates = f"{pullCommitterUrl}"
                                response = requests.get(gitHubAPI_URL_getUserDates, auth=(gh_user, gh_token))
                                dataUser = response.json()
                                if "created_at" not in dataUser: # this occurs when api returns a message that user isn't found
                                    userCreatedAt = None
                                    userUpdatedAt = None
                                elif dataUser["created_at"]:
                                    userCreatedAt = dataUser["created_at"] # valid from
                                    userUpdatedAt = dataUser["updated_at"] # "updated" is the timestamp of the last activity
                            #issueUserId = salt_hash_id(issueUserId)
                            entityIds.append(pullCommitId)
                            symbols = [] #symbols list
                            properties = [] # properties list
                            propPullCommitDict = {"Follower type": followingType, "Committer Type": committerType, "Valid From": userCreatedAt, "Valid To": userUpdatedAt}
                            properties.append(propPullCommitDict)
                            entPullCommitDict = {"Id": entityId, "Symbols":symbols, "Properties":properties}
                            dataEntities.append(entPullCommitDict)
                            symPullCommit = {"Contribution Type": contributeType, "Valid From": commitCreatedAt, "Valid To": commitClosedAt}
                            symbols.append(symPullCommit)
                            pullCommitData = {"Timestamp":commitCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":commitContext}
                            data.append(pullCommitData)
                        else:
                            symPullCommit = {"Contribution Type": contributeType, "Valid From": commitCreatedAt, "Valid To": commitClosedAt}
                            issueSymbols.append(symPullCommit)
                            pullCommitData = {"Timestamp":commitCreatedAt, "EntityIds":entityIds, "Symbol":eventName, "Relational ID":relationalalIds, "Context":commitContext}
                            data.append(pullCommitData)

                # Pull Merger/Closer  _____________________________________________________________________

                if pullMergedAt != None:
                    pullMergerId = merger_id(pullNumber, gh_token, gh_user)
                    contributeType = "Pull Merger"
                    entityIds = []
                    entityIds.append(pullMergerId)
                    eventName = "Pull Request Merged" # Symbol Name
                    #prMergeId = id_generator() # Pull Request Id
                    #samePrMergeId = prMergeId # when we need id to be the same for multiple events
                    #relationalalIds = [sameIssueId, samePrId, prMergeId]

                    # Symbols
                    symbols = []
                    symMerge = {"Contribution Type": contributeType, "Valid From": pullMergedAt, "Valid To": pullClosedAt}
                    symbols.append(symMerge)

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