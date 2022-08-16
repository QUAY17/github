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
    
    with open(argv[2], "rt") as pullsJson:
        pulls = json.load(pullsJson)
 
    githubData = {"Issues":[]}

    for attribute in issues:
        issueId = attribute["id"]
        issueNumber = attribute["number"]
        issueState = attribute["state"]
        issueComments = attribute["comments"]
        issueCreatedAt = attribute["created_at"]
        issueClosedAt = attribute["closed_at"]
        issueUserLogin = attribute["user"]["login"]
        issueUserId = attribute["user"]["id"]
        issueUrl = attribute["url"]
        # test with multiple assignees... works!
        issueAssignees = attribute["assignees"]
        keys = ["login", "id"]
        issueAssigneesLoginId = []
        for attribute in issueAssignees:
            result = dict((k, attribute[k]) for k in keys if k in attribute)
            issueAssigneesLoginId.append(result)
        issueDict = {"id":issueId, "number":issueNumber, "state":issueState, "comments":issueComments, "created_at":issueCreatedAt, 
                "closed_at":issueClosedAt, "user_login":issueUserLogin, "user_id":issueUserId, "assignees":issueAssigneesLoginId}

        # Pulls
        for attribute in pulls:
            pullIssueUrl = attribute["issue_url"]
            if pullIssueUrl == issueUrl: 
                pullId = attribute["id"]
                pullNumber = attribute["number"]
                pullState = attribute["state"]
                pullCreatedAt = attribute["created_at"]
                pullClosedAt = attribute["closed_at"]
                pullMergedAt = attribute["merged_at"]
                pullUserLogin = attribute["user"]["login"]
                pullUserId = attribute["user"]["id"]
                pullAssignees = attribute["assignees"]
                pullReviewers = attribute["requested_reviewers"]
                keys = ["login", "id"]
                pullAssigneesLoginId = []
                pullReviewersLoginId = []
                for attribute in pullAssignees:
                    result = dict((k, attribute[k]) for k in keys if k in attribute)
                    pullAssigneesLoginId.append(result)
                for attribute in pullReviewers:
                    result = dict((k, attribute[k]) for k in keys if k in attribute)
                    pullReviewersLoginId.append(result)
                issueDict = {"id":issueId, "number":issueNumber, "state":issueState, "comments":issueComments, "created_at":issueCreatedAt, 
                                "closed_at":issueClosedAt, "user_login":issueUserLogin, "user_id":issueUserId, "assignees":issueAssigneesLoginId, 
                                "pull_id":pullId, "pull_number":pullNumber, "pull_state":pullState, "pull_created_at":pullClosedAt, "pull_merged_at":pullMergedAt,
                                "pull_user_login":pullUserLogin, "pull_user_id":pullUserId, "pull_assignees":pullAssigneesLoginId, "pull_reviewers":pullReviewersLoginId}

        githubData["Issues"].append(issueDict)

    with open(argv[5], "wt") as outFile:
        json.dump(githubData, outFile, indent=4)
    
    exit(0)

    
    """ith open(argv[3], "rt") as commentsJson:
        commentsFile = json.load(commentsJson)

    with open(argv[4], "rt") as commitsJson:
        commitsFile = json.load(commitsJson)
            
    pullsDict = {"id":pullsId, "number":pullsNumber, "state":pullsState, "created_at":issueCreatedAt, 
                            "closed_at":issueClosedAt, "merged_at":pullsMergedAt, "user_login":issueUserLogin, "user_id":issueUserId, "assignees":pullsAssigneesLoginId}
                            #"reviewers":pullsReviewers}

    #githubData["Issues"].append(pullsDict)

        #githubData = {"Issues": [issues]}
        for attribute in issues:
        keys = ["id", "number", "state"]
        result = dict((k, attribute[k]) for k in keys if k in attribute)

        githubData = {"Issues": [result]}

        githubData["Issues"] = githubData["Issues"].append(result) 

      "" flattened version
        for i in issueAssignees:
            i=0
            issueAssigneesLogin = issueAssignees[i]["login"]
            issueAssigneesId = issueAssignees[i]["id"]
            i+=1             
            """  


