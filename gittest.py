import json
import subprocess
import boto3
from botocore.exceptions import ClientError
 
def lambda_handler(event, context):
    git_repo_url = "https://github.com/Harikrishna351/testingsamplefiles"
    git_branch = "main"
 
    # Initialize AWS Glue client
    glue_client = boto3.client('glue')
 
    try:
        job_name = 'sample' 
        response = glue_client.get_job_runs(JobName=job_name, MaxResults=1)
        if 'JobRuns' not in response or not response['JobRuns']:
            print("No existing Glue job found.")
            return {
                'statusCode': 200,
                'body': json.dumps('No existing Glue job found.')
            }
 
        latest_run_state = response['JobRuns'][0]['JobRunState']
 
        # If the latest run was successful, proceed to check Git changes
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
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            print("No existing Glue job found.")
            return {
                'statusCode': 200,
                'body': json.dumps('No existing Glue job found.')
            }
        else:
            print(f"Error occurred: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error occurred: {e}')
            }
 
    return {
        'statusCode': 200,
        'body': json.dumps('Git changes checked successfully.')
    }
lambda_handler("","")