from .github_client import GitHubClient
from typing import List, Dict

from common.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

class CardCommitScanner:
    def __init__(self, github_client: GitHubClient, card_number: str):
        logger.debug(f"Initializing CardCommitScanner for card number: {card_number}")
        self.github_client = github_client
        self.card_number = card_number
        logger.debug("CardCommitScanner initialized successfully")

    def scan(self, prefix) -> List[Dict]:
        logger.info(f"Scanning repositories with prefix '{prefix}' for commits related to card: {self.card_number}")
        results = []

        logger.debug("Fetching list of repositories")
        repos = self.github_client.get_org_repos(prefix)
        logger.info(f"Found {len(repos)} repositories to scan")

        for repo in repos:
            logger.info(f"Searching in repository: {repo}")
            commits = self.github_client.get_commits_with_card(repo, self.card_number)

            if commits:
                logger.info(f"Found {len(commits)} commits in repository {repo} for card {self.card_number}")
                for commit in commits:
                    logger.debug(f"Fetching diff for commit: {commit['sha'][:7]}")
                    diff = self.github_client.get_commit_diff(repo, commit["sha"])
                    results.append({
                        "repo": repo,
                        "sha": commit["sha"][:7],
                        "message": commit["message"],
                        "date": commit["date"],
                        "diff": diff
                    })
                    logger.debug(f"Added commit {commit['sha'][:7]} to results")
            else:
                logger.debug(f"No matching commits found in repository: {repo}")

        logger.info(f"Scan completed. Found {len(results)} total commits across all repositories")
        return results
