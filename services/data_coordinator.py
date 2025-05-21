# services/data_coordinator.py
import json
import os
from typing import List, Dict, Optional

# Updated imports to use __init__.py exposures
from github_extractor import CardCommitScanner
from github_extractor import save_diffs_to_files
from jira_extractor import JiraClient
from github_extractor import GitHubClient
from summarize_ai import Card, Commit, Epic # Combined import
from common import get_logger # Updated import
import config.settings as settings 

logger = get_logger(__name__)

class DataCoordinator:
    def __init__(self, jira_client: JiraClient, github_client: GitHubClient):
        self.jira_client = jira_client
        self.github_client = github_client
        self.commit_diffs_dir = settings.COMMIT_DIFFS_DIR 
        # Create commit_diffs_dir if it doesn't exist
        if not os.path.exists(self.commit_diffs_dir):
            os.makedirs(self.commit_diffs_dir)
            logger.info(f"Created directory: {self.commit_diffs_dir}")


    def fetch_jira_cards_for_epic(self, epic_key: str) -> Optional[Dict]:
        # This method body will be moved from main.py
        # Ensure to use self.jira_client
        # epic_key is passed as an argument
        logger.info(f"Fetching Jira cards for epic: {epic_key}")
        # ... (rest of the logic from main.py's fetch_jira_cards_for_epic)
        # Replace direct os.getenv calls for Jira config with self.jira_client initialization if those were not moved to client's __init__
        # For example, jira_client is already initialized with server, username, password.

        epic_data = self.jira_client.get_epic_data(epic_key)
        if not epic_data:
            logger.error(f"Failed to retrieve epic data for key: {epic_key}")
            return None

        final_data = epic_data
        final_data["cards"] = []

        logger.info(f"Retrieving issues linked to epic: {epic_key}")
        linked_issue_keys = self.jira_client.get_issues_linked_to_epic(epic_key)
        if linked_issue_keys:
            logger.info(f"Found {len(linked_issue_keys)} issues linked to epic")
            for card_key in linked_issue_keys:
                logger.debug(f"Retrieving card data for: {card_key}")
                card_data = self.jira_client.get_card_data(card_key)
                if card_data:
                    logger.debug(f"Successfully retrieved data for card: {card_key}")
                    final_data["cards"].append(card_data)
                else:
                    logger.warning(f"Failed to retrieve data for card: {card_key}")
        
        logger.info(f"Successfully fetched data for epic: {epic_key} with {len(final_data.get('cards', []))} cards")
        return final_data


    def fetch_commit_diffs_for_cards(self, card_keys: List[str]):
        # This method body will be moved from main.py
        # Ensure to use self.github_client
        # GitHub org_name and prefix should come from settings via self.github_client or directly from settings
        logger.info(f"Fetching commit diffs for {len(card_keys)} cards")
        
        # github_client is already initialized with token and org_name.
        # org_name = settings.GITHUB_ORG_NAME (can be accessed via self.github_client if stored there, or directly)
        # prefix = settings.GITHUB_REPO_PREFIX (can be accessed via self.github_client if stored there, or directly)

        for card_key in card_keys:
            logger.info(f"Processing card: {card_key}")
            # The CardCommitScanner now takes the already initialized github_client
            scanner = CardCommitScanner(self.github_client, card_key)

            logger.debug(f"Scanning for commits related to card: {card_key}")
            # Ensure GITHUB_REPO_PREFIX is available, e.g. from settings
            results = scanner.scan(settings.GITHUB_REPO_PREFIX)

            logger.info(f"Saving commit diffs for card: {card_key}")
            save_diffs_to_files(results, card_key, self.commit_diffs_dir)


    def ingest_jira_and_github_data(self, epic_data: Dict) -> Epic:
        # This method body will be moved from main.py
        logger.info("Ingesting Jira and GitHub data to create Epic object")
        card_list = []

        cards = epic_data.get("cards", [])
        logger.info(f"Processing {len(cards)} cards from epic data")

        for card_data in cards: # Renamed card to card_data to avoid conflict with Card class
            logger.debug(f"Processing card: {card_data['id']}")
            commit_list = []
            try:
                commit_file = f"{self.commit_diffs_dir}/{card_data['id']}.json"
                logger.debug(f"Reading commit diffs from file: {commit_file}")
                with open(commit_file, "r") as f:
                    commit_json = json.load(f)
                    logger.debug(f"Found commit data in {len(commit_json)} repositories")
            except FileNotFoundError:
                logger.warning(f"Commit diffs file not found for card {card_data['id']}. Skipping.")
                continue
            except Exception as e:
                logger.error(f"Error reading commit diffs for card {card_data['id']}: {e}")
                continue

            total_commits = 0
            for repo in commit_json.keys():
                repo_commits = len(commit_json[repo])
                total_commits += repo_commits
                logger.debug(f"Processing {repo_commits} commits from repository: {repo}")
                for commit_detail in commit_json[repo]: # Renamed commit to commit_detail
                    commit_list.append(Commit(commit_detail["repo"], commit_detail["sha"], commit_detail["diff"]))

            logger.info(f"Added {total_commits} commits for card: {card_data['id']}")
            card_list.append(Card(card_data['id'], card_data['title'], card_data['description'], commit_list))

        logger.info(f"Created Epic object with {len(card_list)} cards")
        return Epic(epic_data['id'], epic_data['title'], epic_data['description'], card_list)
