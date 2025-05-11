import requests
from typing import List, Dict

from logger import get_logger

# Initialize logger
logger = get_logger(__name__)


class GitHubClient:
    def __init__(self, token: str, org_name: str):
        logger.debug(f"Initializing GitHub client for organization: {org_name}")
        self.token = token
        self.org_name = org_name
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.debug("GitHub client initialized successfully")

    def get_org_repos(self, prefix: str = "") -> List[str]:
        logger.info(f"Fetching repositories for organization: {self.org_name} with prefix: '{prefix}'")
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/orgs/{self.org_name}/repos?per_page=100&page={page}"
            logger.debug(f"Fetching page {page} of repositories")
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                error_msg = f"Error fetching repos: {res.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            data = res.json()
            if not data:
                logger.debug(f"No more repositories found on page {page}")
                break
            # Apply prefix filter
            filtered_repos = 0
            for repo in data:
                if repo["name"].startswith(prefix):
                    repos.append(repo["name"])
                    filtered_repos += 1
            logger.debug(f"Found {filtered_repos} repositories with prefix '{prefix}' on page {page}")
            page += 1

        logger.info(f"Found a total of {len(repos)} repositories with prefix '{prefix}'")
        return repos

    def get_commits_with_card(self, repo: str, card_number: str) -> List[Dict]:
        logger.info(f"Fetching commits for repository: {repo} containing card number: {card_number}")
        commits = []
        url = f"https://api.github.com/repos/{self.org_name}/{repo}/commits"
        params = {"per_page": 100}
        page = 1
        while True:
            params["page"] = page
            logger.debug(f"Fetching page {page} of commits for repository: {repo}")
            res = requests.get(url, headers=self.headers, params=params)
            if res.status_code != 200:
                logger.warning(f"Skipping {repo}: HTTP status {res.status_code}")
                break
            data = res.json()
            if not data:
                logger.debug(f"No more commits found on page {page} for repository: {repo}")
                break

            matches_on_page = 0
            for commit in data:
                message = commit["commit"]["message"]
                if card_number in message:
                    logger.debug(f"Found commit {commit['sha'][:7]} matching card number: {card_number}")
                    commits.append({
                        "repo": repo,
                        "sha": commit["sha"],
                        "message": message,
                        "date": commit["commit"]["author"]["date"]
                    })
                    matches_on_page += 1

            logger.debug(f"Found {matches_on_page} commits matching card number on page {page}")
            page += 1

        logger.info(f"Found a total of {len(commits)} commits matching card number: {card_number} in repository: {repo}")
        return commits

    def get_commit_diff(self, repo: str, sha: str) -> str:
        """Get the raw diff of a commit."""
        logger.debug(f"Fetching diff for commit: {sha[:7]} in repository: {repo}")
        url = f"https://api.github.com/repos/{self.org_name}/{repo}/commits/{sha}"
        diff_headers = self.headers.copy()
        diff_headers["Accept"] = "application/vnd.github.v3.diff"
        res = requests.get(url, headers=diff_headers)
        if res.status_code == 200:
            diff_size = len(res.text)
            logger.debug(f"Successfully fetched diff for commit: {sha[:7]} (size: {diff_size} bytes)")
            return res.text
        else:
            error_msg = f"Error fetching diff: {res.status_code}"
            logger.error(f"{error_msg} for commit: {sha[:7]} in repository: {repo}")
            return error_msg
