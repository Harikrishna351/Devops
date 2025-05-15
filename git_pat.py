import json
import requests

def lambda_handler(event, context):
    github_username = "Harikrishna351"
    github_repo = "testingsamplefiles"
    personal_access_token = "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"

    github_branches_url = f"https://api.github.com/repos/{github_username}/{github_repo}/branches"
    headers = {"Authorization": f"Bearer {personal_access_token}"}
    branches_response = requests.get(github_branches_url, headers=headers)

    print("Branches response status code:", branches_response.status_code)
    print("Branches response content:", branches_response.content)

    if branches_response.status_code == 200:
        branches_data = branches_response.json()
        for branch in branches_data:
            branch_name = branch['name']
            print(f"Branch: {branch_name}")
            # Fetch commits for the branch
            github_commits_url = f"https://api.github.com/repos/{github_username}/{github_repo}/commits?sha={branch_name}"
            commits_response = requests.get(github_commits_url, headers=headers)
            if commits_response.status_code == 200:
                commits_data = commits_response.json()
                for commit in commits_data:
                    print(f"Commit: {commit['sha']}")
                    print(f"Message: {commit['commit']['message']}")
                    # Extract other relevant commit information as needed
            else:
                print(f"Failed to fetch commits for branch {branch_name}: {commits_response.status_code}")
    else:
        print(f"Failed to fetch branches: {branches_response.status_code}")

    return {
        'statusCode': 200,
        'body': json.dumps('Branches and commits listed successfully.')
    }

lambda_handler("", "")