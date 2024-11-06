import requests

class GitHubAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = 'https://api.github.com'

    def get_endpoint(self, endpoint):
        url = f'{self.base_url}/{endpoint}'
        headers = {'Authorization': f'token {self.token}'}
        response = requests.get(url, headers=headers)
        return response.json()

# Example usage
api = GitHubAPI('your_github_token')
repos = api.get_endpoint('user/repos')
print(repos)