import json
import os
from typing import List, Dict, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

# Updated imports to use __init__.py exposures
from confluence_uploader import convert_markdown_to_html, create_confluence_page
# CardCommitScanner is used by DataCoordinator, not directly in main.py
# from github_extractor import CardCommitScanner 
from github_extractor import GitHubClient 
from jira_extractor import JiraClient
from summarize_ai import ChangeLogGenerator
from datetime import datetime
from jira_extractor import add_comment # Updated import
from flask import Flask, request
import config.settings as settings
from common import get_logger # Updated import
from services import DataCoordinator # Updated import

# Initialize logger
logger = get_logger(__name__)

def main(epic_key: str): # Added epic_key parameter
    """Main function to orchestrate data fetching and changelog generation."""
    logger.info(f"Starting autodoc changelog generation process for EPIC_KEY: {epic_key}")

    # Initialize clients
    # JiraClient and GitHubClient will use settings for their respective configurations
    # These settings are loaded once from .env and are not request-specific for these clients
    jira_client = JiraClient(settings.JIRA_SERVER, settings.JIRA_USERNAME, settings.JIRA_PASSWORD)
    github_client = GitHubClient(settings.GITHUB_TOKEN, settings.GITHUB_ORG_NAME)

    # Instantiate DataCoordinator
    coordinator = DataCoordinator(jira_client, github_client)

    logger.info(f"Fetching Jira epic data for EPIC_KEY: {epic_key}")
    # Pass the explicit epic_key to the coordinator
    epic_data = coordinator.fetch_jira_cards_for_epic(epic_key=epic_key)

    if not epic_data:
        logger.error("Failed to fetch Jira data, exiting")
        return # Exit if fetching Jira data failed

    card_keys = [card['id'] for card in epic_data.get('cards', [])]
    logger.info(f"Extracted {len(card_keys)} card keys from epic data")

    logger.info("Fetching commit diffs from GitHub")
    coordinator.fetch_commit_diffs_for_cards(card_keys)

    logger.info("Ingesting Jira and GitHub data")
    full_epic = coordinator.ingest_jira_and_github_data(epic_data)

    # GOOGLE_API_KEY is already handled in settings.py with a fallback mechanism
    logger.info("Initializing LLM for changelog generation")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=settings.GOOGLE_API_KEY, # Use the key from settings
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    logger.info(f"Generating changelog and saving to {settings.CHANGELOG_OUTPUT_FILE}")
    generator = ChangeLogGenerator(llm)
    generator.generate(full_epic, settings.CHANGELOG_OUTPUT_FILE)

    logger.info("Changelog generation completed successfully")
    logger.info("Uploading to Confluence page...")
    html = convert_markdown_to_html(settings.CHANGELOG_OUTPUT_FILE)
    # Use the explicit epic_key for the page title
    page_title = f"{epic_key}-Summary-{datetime.now()}"
    page_url = create_confluence_page(page_title, html)
    logger.info(f"✅ Confluence page created: {page_url}")
    # Pass the explicit epic_key to add_comment
    add_comment(page_url, epic_key=epic_key)
    logger.info(f"✅ Linked to jira ticket: {epic_key}")
    return f"✅ Confluence page created: {page_url}"

# if __name__ == "__main__":
#     # This block is for potential direct script execution, not used by Flask.
#     # Ensure settings.EPIC_KEY is loaded from .env if you plan to use this.
#     default_epic_key_from_env = settings.EPIC_KEY
#     if default_epic_key_from_env:
#         logger.info(f"Running directly with EPIC_KEY from .env: {default_epic_key_from_env}")
#         main(epic_key=default_epic_key_from_env)
#     else:
#         logger.error("Attempted to run directly, but EPIC_KEY is not set in .env or config.settings.")
    # Note: The Flask app functionality is now handled by app.py.
    # The if __name__ == "__main__": block below can be used for direct script execution if needed.

if __name__ == "__main__":
    # This block is for potential direct script execution.
    # Example: python main.py YOUR_EPIC_KEY
    # You might want to use argparse for more robust CLI argument handling.
    import sys
    if len(sys.argv) > 1:
        epic_key_arg = sys.argv[1]
        logger.info(f"Running directly with EPIC_KEY from command line: {epic_key_arg}")
        try:
            result_url = main(epic_key=epic_key_arg)
            logger.info(f"Direct execution finished. Result: {result_url}")
        except Exception as e:
            logger.error(f"Error during direct execution: {e}", exc_info=True)
    elif settings.EPIC_KEY:
        logger.info(f"Running directly with EPIC_KEY from .env: {settings.EPIC_KEY}")
        try:
            result_url = main(epic_key=settings.EPIC_KEY)
            logger.info(f"Direct execution finished. Result: {result_url}")
        except Exception as e:
            logger.error(f"Error during direct execution: {e}", exc_info=True)
    else:
        logger.warning("Attempted to run directly, but no EPIC_KEY provided via command line or .env.")
        logger.warning("Usage for direct execution: python main.py <YOUR_EPIC_KEY>")