import json
import requests
import subprocess
import boto3
from botocore.exceptions import ClientError
def lambda_handler(event, context):
    github_username = "Harikrishna351"
    github_repo = "newjen"
    git_branch = "main"  
    
    # Check GitHub Changes
    def check_github_changes():
        # Send a GET request to fetch information about all branches of the repository
        github_branches_url = f"https://api.github.com/repos/{github_username}/{github_repo}/branches"
        branches_response = requests.get(github_branches_url)

        if branches_response.status_code == 200:
            branches_data = branches_response.json()
            for branch in branches_data:
                branch_name = branch['name']
                print(f"Branch: {branch_name}")
                # Fetch commits for the branch
                github_commits_url = f"https://api.github.com/repos/{github_username}/{github_repo}/commits?sha={branch_name}"
                commits_response = requests.get(github_commits_url)
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

    # Check Glue Jobs
    def check_glue_jobs():
        # Initialize AWS Glue client
        glue_client = boto3.client('glue')


        job_name = 'sample' 
        response = glue_client.get_job_runs()
        print (response)
       
        if 'JobRuns' not in response or not response['JobRuns']:
            print("No existing Glue job found.")
            latest_run_state = response['JobRuns'][0]['JobRunState']

            if latest_run_state == 'SUCCEEDED':
                # Fetch latest changes from the Git repository
              git_command = ["git", "fetch", "--all"]
              subprocess.check_call(git_command)
                # Get the diff between local and the specified branch
              git_diff_command = ["git", "diff", "--name-only", f"HEAD", f"origin/{git_branch}"]
              diff_output = subprocess.check_output(git_diff_command, universal_newlines=True)
              if diff_output:
                print("New changes found in the Git repository:")
                print(diff_output)
              else:
                print("No new changes found in the Git repository.")
            else:
              print("The latest Glue job execution was not successful.")

    # Call the functions to check GitHub changes and Glue jobs
    check_github_changes()
    check_glue_jobs()

    return {
        'statusCode': 200,
        'body': json.dumps('GitHub changes and Glue jobs checked successfully.')
    }

lambda_handler("", "")