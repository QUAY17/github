import json
from sys import argv

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
        pullsFile = json.load(pullsJson)

    with open(argv[3], "rt") as commentsJson:
        commentsFile = json.load(commentsJson)

    with open(argv[4], "rt") as commitsJson:
        commitsFile = json.load(commitsJson)

    githubData = {"Issues": []}
    
    for attribute in issues:
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
        res = []
        for attribute in issueAssignees:
            result = dict((k, attribute[k]) for k in keys if k in attribute)
            res.append(result)

        """ flattened version
        for i in issueAssignees:
            i=0
            issueAssigneesLogin = issueAssignees[i]["login"]
            issueAssigneesId = issueAssignees[i]["id"]
            i+=1 
        """
        
    issueDict = {"id":issueId, "number":issueNumber, "state":issueState, "comments":issueComments, "created_at":issueCreatedAt, 
                        "closed_at":issueClosedAt, "user_login":issueUserLogin, "user_id":issueUserId, "url":issueURL, "assignees":res}


    githubData["Issues"].append(issueDict)

    with open(argv[5], "wt") as outFile:
        json.dump(githubData, outFile, indent=4)

