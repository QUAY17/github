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
    print("python githubToJson.py gh_Issues.json gh_Pulls.json finalOutFile.json")
    print("\tgh_Issues.json - the Issues json file")
    print("\tgh_Pulls.json - the Pulls json file")
    print("\tfinalOutFile.json - a json file that will contain all the Github data we find useful")
    exit(0)

if __name__ == "__main__":
    if len(argv) != 4:
        usage()

    with open(argv[1], "rt") as issuesJson:
        issues = json.load(issuesJson)
     
    githubData = {"Issues":[]}

    for attribute in issues[:5]:
        issueId = attribute["id"]
        issueNumber = attribute["number"]
        #issueState = attribute["state"]
        #issueComments = attribute["comments"]
        issueCreatedAt = attribute["created_at"]
        issueClosedAt = attribute["closed_at"]
        issueUserLogin = attribute["user"]["login"]
        issueUserId = attribute["user"]["id"]
        issueUrl = attribute["url"]
        issueCommentsUrl = attribute["comments_url"]
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

        allCommenters = [] # list of issue commenters
        issueCommentLoginId = [] #list of issue commenters login and id
        for attribute in issueComment:
            if attribute["created_at"] is not None:
                commentCreatedAt = attribute["created_at"]
            if attribute["user"] is not None: # if None value, ignore
                commentInfo = attribute["user"]
                allCommenters.append(commentInfo)
                keys = ["login", "id"]
                for attribute in allCommenters:
                    result = dict((k, attribute[k]) for k in keys if k in attribute)
                    result["created_at"] = commentCreatedAt
                issueCommentLoginId.append(result)     
        # ______________________________________________________________________________

        issueDict = {"issue_id":issueId, "issue_number":issueNumber, "issue_creator_login":issueUserLogin, "issue_creator_id":issueUserId,
                    "issue_created_at":issueCreatedAt, "issue_closed_at":issueClosedAt, "issue_assignees":issueAssigneesLoginId, "issue_comments":issueCommentLoginId}

        # Pulls
        with open(argv[2], "rt") as pullsJson:
            pulls = json.load(pullsJson)

        for attribute in pulls:
            pullIssueUrl = attribute["issue_url"]
            if pullIssueUrl == issueUrl: 
                #pullId = attribute["id"]
                pullNumber = attribute["number"]
                #pullState = attribute["state"]
                pullCreatedAt = attribute["created_at"]
                pullClosedAt = attribute["closed_at"]
                pullMergedAt = attribute["merged_at"]
                commitUrl = attribute["commits_url"]
                pullUserLogin = attribute["user"]["login"]
                pullUserId = attribute["user"]["id"]
                pullCommentUrl = attribute["review_comments_url"]
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
                # _________________________________________________________________________________________`

                # Get all Commits dynamically
                gitHubAPI_URL_getCommits = f"{commitUrl}"
                response = requests.get(gitHubAPI_URL_getCommits, auth=(gh_user, gh_token))
                dataCommit = response.json()

                allCommitters = [] # list of commiters
                commitLoginId = [] # list of commiters login and id
                for attribute in dataCommit:
                    if attribute["commit"] is not None:
                        commitDate = attribute["commit"]["author"]["date"]
                    if attribute["author"] is not None: # if None value, ignore
                        commitInfo = attribute["author"]
                        allCommitters.append(commitInfo)
                        keys = ["login", "id"]            
                        for attribute in allCommitters:
                            result = dict((k, attribute[k]) for k in keys if k in attribute)
                            result["created_at"] = commitDate
                        commitLoginId.append(result)
            
                # Comments- we are retrieving the commemts on each pull request
                # _________________________________________________________________________________________               
                
                # Get all Comments dynamically
                gitHubAPI_URL_getComments = f"{pullCommentUrl}"
                response = requests.get(gitHubAPI_URL_getComments, auth=(gh_user, gh_token))
                pullComment = response.json()

                pullCommenters = [] # list of pull commenters
                pullCommentLoginId = [] # list pull commenters login and id
                for attribute in pullComment:
                    if attribute["created_at"] is not None:
                        commentCreatedAt = attribute["created_at"]
                    if attribute["user"] is not None: # if None value, ignore
                        commentInfo = attribute["user"]
                        pullCommenters.append(commentInfo)
                        keys = ["login", "id"]
                        for attribute in pullCommenters:
                            result = dict((k, attribute[k]) for k in keys if k in attribute)
                            result["created_at"] = commentCreatedAt
                        pullCommentLoginId.append(result)  

                issueDict = {"issue_id":issueId, "issue_number":issueNumber, "issue_creator_login":issueUserLogin, "issue_creator_id":issueUserId,
                            "issue_created_at":issueCreatedAt, "issue_closed_at":issueClosedAt, "issue_assignees":issueAssigneesLoginId, "issue_comments":issueCommentLoginId,
                            "pull_number":pullNumber, "pull_created_at":pullCreatedAt, "pull_merged_at":pullMergedAt,"pull_closed_at": pullClosedAt,"pull_creator_login":pullUserLogin, 
                            "pull_creator_id":pullUserId,"pull_assignees":pullAssigneesLoginId, "pull_reviewers":pullReviewersLoginId, "pull_commits":commitLoginId, 
                            "pull_comments":pullCommentLoginId}
                # _________________________________________________________________________________________  
                    
        githubData["Issues"].append(issueDict)

    with open(argv[3], "wt") as outFile:
        json.dump(githubData, outFile, indent=4)




