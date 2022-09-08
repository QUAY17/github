import json
import requests

import pprint as pp

gh_user="QUAY17"
gh_token="ghp_XnIqqyMUYgjfO3l5ruk3ZTxNbB9kl413OWK"
gh_repo="tensorflow/tensorflow"

#Get all Events since repo creation
gitHubAPI_URL_getEvents = f"https://api.github.com/repos/{gh_repo}/events?branch=master&page=1&per_page=100"
response = requests.get(gitHubAPI_URL_getEvents, auth=(gh_user, gh_token))
data = response.json()
while 'next' in response.links.keys():
  response=requests.get(response.links['next']['url'], auth=(gh_user, gh_token))
  data.extend(response.json())
print("MetaData:")
print("---")
print(response)
print(type(data))
print("<records [{}]>".format(len(data)))
print("---")

with open('data/gh_Events.json', 'w') as jsonFile:
    json.dump(data, jsonFile, indent=4)

"""
# Get all Commits since repo creation
gitHubAPI_URL_getCommits = f"https://api.github.com/repos/{gh_repo}/commits?branch=master&page=1&per_page=100"
response = requests.get(gitHubAPI_URL_getCommits, auth=(gh_user, gh_token))
data = response.json()
while 'next' in response.links.keys():
  response=requests.get(response.links['next']['url'], auth=(gh_user, gh_token))
  data.extend(response.json())
print("MetaData:")
print("---")
print(response)
print(type(data))
print("<records [{}]>".format(len(data)))
print("---")
#print("Record[0]:")
#pp.pprint(data[0])

with open('data/gh_Commits.json', 'w') as jsonFile:
    json.dump(data, jsonFile, indent=4)

# Get all Comments since repo creation
gitHubAPI_URL_getComments = f"https://api.github.com/repos/{gh_repo}/comments?page=1&per_page=100"
response = requests.get(gitHubAPI_URL_getComments, auth=(gh_user, gh_token))
data = response.json()
while 'next' in response.links.keys():
  response=requests.get(response.links['next']['url'], auth=(gh_user, gh_token))
  data.extend(response.json())
print("MetaData:")
print("---")
print(response)
print(type(data))
print("<records [{}]>".format(len(data)))
print("---")
#print("Record[0]:")
#pp.pprint(data[0])
with open('data/gh_Comments.json', 'w') as jsonFile:
    json.dump(data, jsonFile, indent=4)

# Get all Pull Requests since repo creation
gitHubAPI_URL_getPulls = f"https://api.github.com/repos/{gh_repo}/pulls?branch=master&state=all&page=1&per_page=100"
response = requests.get(gitHubAPI_URL_getPulls, auth=(gh_user, gh_token))
data = response.json()
while 'next' in response.links.keys():
  response=requests.get(response.links['next']['url'], auth=(gh_user, gh_token))
  data.extend(response.json())
print("MetaData:")
print("---")
print(response)
print(type(data))
print("<records [{}]>".format(len(data)))
print("---")
#print("Record[0]:")
#pp.pprint(data[0])
with open('data/gh_Pulls.json', 'w') as jsonFile:
    json.dump(data, jsonFile, indent=4)

# Get all Issues since repo creation
gitHubAPI_URL_getIssues = f"https://api.github.com/repos/{gh_repo}/issues?&state=all&page=1&per_page=100"
response = requests.get(gitHubAPI_URL_getIssues, auth=(gh_user, gh_token))
data = response.json()
while 'next' in response.links.keys():
  response=requests.get(response.links['next']['url'], auth=(gh_user, gh_token))
  data.extend(response.json())
print("MetaData:")
print("---")
print(response)
print(type(data))
print("<records [{}]>".format(len(data)))
print("---")
#print("Record[0]:")
#pp.pprint(data[0])
with open('data/gh_Issues.json', 'w') as jsonFile:
    json.dump(data, jsonFile, indent=4)
"""

