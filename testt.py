import json
import requests

def lambda_handler(event, context):
    # Define GitHub user or organization name
    github_username = "Harikrishna351"

    try:
        # Send a GET request to fetch repository information
        github_api_url = f"https://github.com/Harikrishna351?tab=repositories"
        response = requests.get(github_api_url)
        if response.status_code == 200:
            # Parse JSON response
            repos = response.json()
            # Extract repository names
            repo_names = [repo['name'] for repo in repos]
            
            print("Repositories in the GitHub account:")
            for name in repo_names:
                print(name)
        else:
            print(f"Failed to fetch repositories: {response.status_code}")

    except Exception as e:
        print(f"Error occurred while fetching repositories: {e}")

    return {
        'statusCode': 200,
        'body': json.dumps('Repositories listed successfully.')
    }
