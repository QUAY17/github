import json
from sys import argv
import pprint as pp

def usage():
    print("python githubToJson.py gh_Issues.json gh_Pulls.json gh_Comments.json gh_Commits.json finalOutFile.json")
    print("\tgh_Issues.json - the Issues json file")
    print("\tgh_Pulls.json - the Pulls json file")
    print("\tgh_Comments.json - the Comments json file")
    print("\tgh_Commits.json  - the Commits json file")
    print("\tfinalOutFile.json - a json file that will contain all the Github data we find useful")
    exit(0)

if __name__ == "__main__":
    if len(argv) != 6:
        usage()

    with open(argv[1], "rt") as issuesJson:
        issues = json.load(issuesJson)
    
    githubData = {"Issues": [issues]}
    keys = ["id", "number", "state"]
    for attribute in issues:
        result = dict((k, attribute[k]) for k in keys if k in attribute)
        githubData = {"Issues": [result]}
        #githubData["Issues"].append(result)  
        #print(githubData)
    
    with open(argv[5], "wt") as outFile:
        json.dump(githubData, outFile, indent=4)

        exit(0)
        
        issueId = attribute["id"]
        issueNumber = attribute["number"]
        issueState = attribute["state"]
        issueComments = attribute["comments"]
        issueCreatedAt = attribute["created_at"]
        issueClosedAt = attribute["closed_at"]
        issueUserLogin = attribute["user"]["login"]
        issueUserId = attribute["user"]["id"]
        issueURL = attribute["url"]
        # test with multiple assignees
        issueAssignees = attribute["assignees"]
        keys = ["login", "id"]
        issueAssigneesLoginId = []
        for attribute in issueAssignees:
            result = dict((k, attribute[k]) for k in keys if k in attribute)
            issueAssigneesLoginId.append(result)
        """ flattened version
        for i in issueAssignees:
            i=0
            issueAssigneesLogin = issueAssignees[i]["login"]
            issueAssigneesId = issueAssignees[i]["id"]
            i+=1 
        """
    
    issueDict = {"id":issueId, "number":issueNumber, "state":issueState, "comments":issueComments, "created_at":issueCreatedAt, 
                        "closed_at":issueClosedAt, "user_login":issueUserLogin, "user_id":issueUserId, "assignees":issueAssigneesLoginId, "url":issueURL}

    githubData["Issues"].append(issueDict)

    """   
    with open(argv[2], "rt") as pullsJson:
        pulls = json.load(pullsJson)

    with open(argv[3], "rt") as commentsJson:
        commentsFile = json.load(commentsJson)

    with open(argv[4], "rt") as commitsJson:
        commitsFile = json.load(commitsJson)

    for attribute in pulls:
        pullsId = attribute["id"]
        pullsNumber = attribute["number"]
        pullsState = attribute["state"]
        pullsCreatedAt = attribute["created_at"]
        pullsClosedAt = attribute["closed_at"]
        pullsMergedAt = attribute["merged_at"]
        pullsUserLogin = attribute["user"]["login"]
        pullsUserId = attribute["user"]["id"]
        pullsAssignees = attribute["assignees"]
        keys = ["login", "id"]
        pullsAssigneesLoginId = []
        for attribute in pullsAssignees:
            result = dict((k, attribute[k]) for k in keys if k in attribute)
            pullsAssigneesLoginId.append(result)
        #pullsReviewers = attribute["requested_reviewers"]
        keys = ["login", "id"]
        pullsReviewersLoginId = []
        for attribute in pullsReviewers:
            result = dict((k, attribute[k]) for k in keys if k in attribute)
            pullsReviewersLoginId.append(result)
    pullsDict = {"id":pullsId, "number":pullsNumber, "state":pullsState, "created_at":issueCreatedAt, 
                        "closed_at":issueClosedAt, "merged_at":pullsMergedAt, "user_login":issueUserLogin, "user_id":issueUserId, "assignees":pullsAssigneesLoginId}
                        #"reviewers":pullsReviewers}

    #githubData["Issues"].append(pullsDict)
    """


    




