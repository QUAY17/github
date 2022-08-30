import json
from re import I
from sys import argv
from urllib.request import urlopen
import requests

"""
def authentication():
    gh_user="QUAY17"
    gh_token=""
"""

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
     
    githubData = {"Issues":[]}

    for attribute in issues[:100]:
        issueId = attribute["id"]
        issueNumber = attribute["number"]
        issueState = attribute["state"]
        issueComments = attribute["comments"]
        issueCreatedAt = attribute["created_at"]
        issueClosedAt = attribute["closed_at"]
        issueUserLogin = attribute["user"]["login"]
        issueUserId = attribute["user"]["id"]
        issueUrl = attribute["url"]
        issueCommentsUrl = attribute["comments_url"]
        # test with multiple assignees... works!
        issueAssignees = attribute["assignees"]
        keys = ["login", "id"]
        issueAssigneesLoginId = []
        for attribute in issueAssignees:
            result = dict((k, attribute[k]) for k in keys if k in attribute)
            issueAssigneesLoginId.append(result)
        """ flattened version
        for i in issueAssignees:
            issueAssigneesLogin = issueAssignees[i]["login"]
            issueAssigneesId = issueAssignees[i]["id"]
            """ 

        # Get all Comments since repo creation, dynamic for now
        # Issue comments- we are retrieving the comments on each issue
        # _________________________________________________________________________________________

        gh_user="QUAY17"
        gh_token="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"

        gitHubAPI_URL_getComments = f"{issueCommentsUrl}"
        response = requests.get(gitHubAPI_URL_getComments, auth=(gh_user, gh_token))
        issueComment = response.json()

        allCommenters = [] # list of commmenters
        for attribute in issueComment:
            if attribute["user"] is not None: # if None value, ignore
                commentInfo = attribute["user"]
                allCommenters.append(commentInfo)
                keys = ["login", "id"]
                commentLoginId = []
                for attribute in allCommenters:
                    result = dict((k, attribute[k]) for k in keys if k in attribute)
                    commentLoginId.append(result)  
        # ______________________________________________________________________________

        issueDict = {"issue_id":issueId, "issue_number":issueNumber, "issue_state":issueState, "issue_comments":issueComments, "issue_created_at":issueCreatedAt, 
                "issue_closed_at":issueClosedAt, "issue_user_login":issueUserLogin, "issue_user_id":issueUserId, "issue_assignees":issueAssigneesLoginId, "comment_author":commentLoginId}

        # Pulls
        with open(argv[2], "rt") as pullsJson:
            pulls = json.load(pullsJson)

        for attribute in pulls:
            pullIssueUrl = attribute["issue_url"]
            if pullIssueUrl == issueUrl: 
                pullId = attribute["id"]
                pullNumber = attribute["number"]
                pullState = attribute["state"]
                pullCreatedAt = attribute["created_at"]
                pullClosedAt = attribute["closed_at"]
                pullMergedAt = attribute["merged_at"]
                commitUrl = attribute["commits_url"]
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

            # Commits- we are retrieving the commits on each pull request
            # _________________________________________________________________________________________

                # Get all Commits since repo creation, dynamic for now
                gitHubAPI_URL_getCommits = f"{commitUrl}"
                response = requests.get(gitHubAPI_URL_getCommits, auth=(gh_user, gh_token))
                dataCommit = response.json()

                allCommitters = [] # list of commiters
                for attribute in dataCommit:
                    if attribute["author"] is not None: # if None value, ignore
                        commitInfo = attribute["author"]
                        allCommitters.append(commitInfo)
                        keys = ["login", "id"]
                        commitLoginId = []
                        for attribute in allCommitters:
                            result = dict((k, attribute[k]) for k in keys if k in attribute)
                            commitLoginId.append(result)

                issueDict = {"issue_id":issueId, "issue_number":issueNumber, "issue_state":issueState, "issue_comments":issueComments, "issue_created_at":issueCreatedAt, 
                        "issue_closed_at":issueClosedAt, "issue_user_login":issueUserLogin, "issue_user_id":issueUserId, "issue_assignees":issueAssigneesLoginId, 
                        "comment_author":commentLoginId, "pull_id":pullId, "pull_number":pullNumber, "pull_state":pullState, "pull_created_at":pullCreatedAt,"pull_merged_at":pullMergedAt,
                        "pull_closed_at": pullClosedAt,"pull_user_login":pullUserLogin, "pull_user_id":pullUserId,"pull_assignees":pullAssigneesLoginId, 
                        "pull_reviewers":pullReviewersLoginId, "commit_author":commitLoginId}
           # _________________________________________________________________________________________  
                
        githubData["Issues"].append(issueDict)

    with open(argv[5], "wt") as outFile:
        json.dump(githubData, outFile, indent=4)




