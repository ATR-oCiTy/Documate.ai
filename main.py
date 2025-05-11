import json
import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from github_extractor.card_commit_scanner import CardCommitScanner
from github_extractor.github_client import GitHubClient
from github_extractor.save_utils import save_diffs_to_files
from jira_extractor.jira_client import JiraClient
from summarize_ai.card import Card
from summarize_ai.change_log_generator import ChangeLogGenerator
from summarize_ai.commit import Commit
from summarize_ai.epic import Epic
from logger import get_logger

# Initialize logger
logger = get_logger(__name__)

JIRA_DATA_FILE = "jira.json"
COMMIT_DIFFS_DIR = "./commit_diffs"
CHANGELOG_OUTPUT_FILE = "AI_CHANGELOG.md"
DEFAULT_GOOGLE_API_KEY = "AIzaSyACKIWQDvtBoxsXRn1WtnPcBWXH2iEiXWM"

def fetch_jira_cards_for_epic() -> Optional[Dict]:
    """Fetches Jira epic and linked card data and returns it."""
    logger.info("Fetching Jira cards for epic")
    jira_server = os.getenv("JIRA_SERVER")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_password = os.getenv("JIRA_PASSWORD")
    epic_key = os.getenv("EPIC_KEY")

    if not all([jira_server, jira_username, jira_password, epic_key]):
        logger.error("Missing required environment variables for Jira connection")
        return None

    logger.debug(f"Connecting to Jira server: {jira_server} with user: {jira_username}")
    jira_client = JiraClient(jira_server, jira_username, jira_password)

    logger.info(f"Retrieving epic data for key: {epic_key}")
    epic_data = jira_client.get_epic_data(epic_key)
    if not epic_data:
        logger.error(f"Failed to retrieve epic data for key: {epic_key}")
        return None

    final_data = epic_data
    final_data["cards"] = []

    logger.info(f"Retrieving issues linked to epic: {epic_key}")
    linked_issue_keys = jira_client.get_issues_linked_to_epic(epic_key)
    if linked_issue_keys:
        logger.info(f"Found {len(linked_issue_keys)} issues linked to epic")
        for card_key in linked_issue_keys:
            logger.debug(f"Retrieving card data for: {card_key}")
            card_data = jira_client.get_card_data(card_key)
            if card_data:
                logger.debug(f"Successfully retrieved data for card: {card_key}")
                final_data["cards"].append(card_data)
            else:
                logger.warning(f"Failed to retrieve data for card: {card_key}")

    # Optionally save to a file, but not strictly necessary for the data flow
    # try:
    #     with open(JIRA_DATA_FILE, 'w') as f:
    #         json.dump(final_data, f, indent=4)
    #     logger.info(f"Data successfully written to {JIRA_DATA_FILE}")
    # except Exception as e:
    #     logger.error(f"Error writing to JSON file: {e}")

    logger.info(f"Successfully fetched data for epic: {epic_key} with {len(final_data.get('cards', []))} cards")
    return final_data


def fetch_commit_diffs_for_cards(card_keys: List[str]):
    """Fetches commit diffs for a list of card keys from GitHub."""
    logger.info(f"Fetching commit diffs for {len(card_keys)} cards")
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN not found in environment")
        raise Exception("GITHUB_TOKEN not found in environment.")

    org_name = os.getenv("GITHUB_ORG_NAME")
    prefix = os.getenv("GITHUB_REPO_PREFIX")
    logger.debug(f"Using GitHub organization: {org_name} and repo prefix: {prefix}")

    for card_key in card_keys:
        logger.info(f"Processing card: {card_key}")
        github_client = GitHubClient(token, org_name)
        scanner = CardCommitScanner(github_client, card_key)

        logger.debug(f"Scanning for commits related to card: {card_key}")
        results = scanner.scan(prefix)

        logger.info(f"Saving commit diffs for card: {card_key}")
        save_diffs_to_files(results, card_key, COMMIT_DIFFS_DIR)

def ingest_jira_and_github_data(epic_data: Dict) -> Epic:
    """Ingests Jira and GitHub data to create an Epic object."""
    logger.info("Ingesting Jira and GitHub data to create Epic object")
    card_list = []

    cards = epic_data.get("cards", [])
    logger.info(f"Processing {len(cards)} cards from epic data")

    for card in cards:
        logger.debug(f"Processing card: {card['id']}")
        commit_list = []
        try:
            commit_file = f"{COMMIT_DIFFS_DIR}/{card['id']}.json"
            logger.debug(f"Reading commit diffs from file: {commit_file}")
            with open(commit_file, "r") as f:
                commit_json = json.load(f)
                logger.debug(f"Found commit data in {len(commit_json)} repositories")
        except FileNotFoundError:
            logger.warning(f"Commit diffs file not found for card {card['id']}. Skipping.")
            continue
        except Exception as e:
            logger.error(f"Error reading commit diffs for card {card['id']}: {e}")
            continue

        total_commits = 0
        for repo in commit_json.keys():
            repo_commits = len(commit_json[repo])
            total_commits += repo_commits
            logger.debug(f"Processing {repo_commits} commits from repository: {repo}")
            for commit in commit_json[repo]:
                commit_list.append(Commit(commit["repo"], commit["sha"], commit["diff"]))

        logger.info(f"Added {total_commits} commits for card: {card['id']}")
        card_list.append(Card(card['id'], card['title'], card['description'], commit_list))

    logger.info(f"Created Epic object with {len(card_list)} cards")
    return Epic(epic_data['id'], epic_data['title'], epic_data['description'], card_list)

def main():
    """Main function to orchestrate data fetching and changelog generation."""
    logger.info("Starting autodoc changelog generation process")

    logger.debug("Loading environment variables from .env file")
    load_dotenv()

    logger.info("Fetching Jira epic data")
    epic_data = fetch_jira_cards_for_epic()

    if not epic_data:
        logger.error("Failed to fetch Jira data, exiting")
        return # Exit if fetching Jira data failed

    card_keys = [card['id'] for card in epic_data.get('cards', [])]
    logger.info(f"Extracted {len(card_keys)} card keys from epic data")

    logger.info("Fetching commit diffs from GitHub")
    fetch_commit_diffs_for_cards(card_keys)

    logger.info("Ingesting Jira and GitHub data")
    full_epic = ingest_jira_and_github_data(epic_data)

    if "GOOGLE_API_KEY" not in os.environ:
        logger.debug("GOOGLE_API_KEY not found in environment, using default key")
        os.environ["GOOGLE_API_KEY"] = DEFAULT_GOOGLE_API_KEY
    else:
        logger.debug("Using GOOGLE_API_KEY from environment")

    logger.info("Initializing LLM for changelog generation")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    logger.info(f"Generating changelog and saving to {CHANGELOG_OUTPUT_FILE}")
    generator = ChangeLogGenerator(llm)
    generator.generate(full_epic, CHANGELOG_OUTPUT_FILE)

    logger.info("Changelog generation completed successfully")


if __name__ == "__main__":
    main()
