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

        try:
            # List all Glue jobs
            response = glue_client.get_jobs()
            job_names = [job['Name'] for job in response['Jobs']]

            if not job_names:
                print("No Glue jobs found.")
                return

            for job_name in job_names:
                # Get latest job run for each job
                response = glue_client.get_job_runs(JobName=job_name, MaxResults=1)
                if 'JobRuns' in response and response['JobRuns']:
                    latest_run_state = response['JobRuns'][0]['JobRunState']
                    if latest_run_state == 'SUCCEEDED':
                        # Fetch latest changes from the Git repository
                        git_command = ["git", "fetch", "--all"]
                        subprocess.check_call(git_command)
                        # Get the diff between local and the specified branch
                        git_diff_command = ["git", "diff", "--name-only", f"HEAD", f"origin/{git_branch}"]
                        diff_output = subprocess.check_output(git_diff_command, universal_newlines=True)
                        if diff_output:
                            print(f"New changes found in the Git repository for job: {job_name}")
                            print(diff_output)
                        else:
                            print(f"No new changes found in the Git repository for job: {job_name}")
                    else:
                        print(f"The latest Glue job execution for job {job_name} was not successful.")
                else:
                    print(f"No job runs found for job: {job_name}")

        except ClientError as e:
            print(f"An error occurred: {e}")

    # Call the functions to check GitHub changes and Glue jobs
    check_github_changes()
    check_glue_jobs()

    return {
        'statusCode': 200,
        'body': json.dumps('GitHub changes and Glue jobs checked successfully.')
    }

lambda_handler("", "")