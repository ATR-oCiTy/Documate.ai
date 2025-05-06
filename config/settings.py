import os
from dotenv import load_dotenv

load_dotenv()

JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_PASSWORD = os.getenv("JIRA_PASSWORD")
EPIC_KEY = os.getenv("EPIC_KEY") # This might be better handled if it changes per request

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG_NAME = os.getenv("GITHUB_ORG_NAME")
GITHUB_REPO_PREFIX = os.getenv("GITHUB_REPO_PREFIX")

CHANGELOG_OUTPUT_FILE = os.getenv("CHANGELOG_OUTPUT_FILE", "changelog.md") # Provide a default
DEFAULT_GOOGLE_API_KEY = os.getenv("DEFAULT_GOOGLE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", DEFAULT_GOOGLE_API_KEY) # Handle fallback

# Consider adding constants for file paths like JIRA_DATA_FILE and COMMIT_DIFFS_DIR if they are fixed.
JIRA_DATA_FILE = "jira.json"
COMMIT_DIFFS_DIR = "./commit_diffs"
