from typing import List, Dict, Optional
from jira import JIRA

from logger import get_logger

# Initialize logger
logger = get_logger(__name__)

class JiraClient:

    def __init__(self, server: str, username: str, password: str):
        logger.debug(f"Initializing Jira client for server: {server}")
        self.server = server
        self.username = username
        self.password = password
        self.jira = self._connect()
        logger.debug("Jira client initialized successfully")

    def _connect(self) -> JIRA:
        logger.info(f"Connecting to Jira server: {self.server}")
        try:
            jira_options = {'server': self.server}
            jira = JIRA(options=jira_options, basic_auth=(self.username, self.password))
            logger.info("Successfully connected to Jira server")
            return jira
        except Exception as e:
            error_msg = f"Failed to connect to Jira: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_issue(self, issue_key: str) -> Optional[JIRA]:
        logger.debug(f"Fetching issue with key: {issue_key}")
        try:
            issue = self.jira.issue(issue_key)
            logger.debug(f"Successfully fetched issue: {issue_key}")
            return issue
        except Exception as e:
            logger.error(f"Error getting issue {issue_key}: {e}")
            return None

    def get_card_data(self, card_key: str) -> Optional[Dict]:
        logger.info(f"Getting card data for: {card_key}")
        card_data = self.get_issue(card_key)
        if not card_data:
            logger.warning(f"No card data found for key: {card_key}")
            return None

        try:
            result = {
                "id": card_data.key,
                "title": card_data.fields.summary,
                "description": card_data.fields.description,
                "status": card_data.fields.status.name,
                "assignee": card_data.fields.assignee.displayName if card_data.fields.assignee else 'Unassigned'
            }
            logger.info(f"Successfully retrieved card data for: {card_key}")
            logger.debug(f"Card title: {result['title']}, status: {result['status']}")
            return result
        except Exception as e:
            logger.error(f"Error processing card data for {card_key}: {e}")
            return None


    def get_epic_data(self, epic_key: str) -> Optional[Dict]:
        logger.info(f"Getting epic data for: {epic_key}")
        epic_data = self.get_issue(epic_key)
        if not epic_data:
            logger.warning(f"No epic data found for key: {epic_key}")
            return None

        try:
            result = {
                "id": epic_data.key,
                "title": epic_data.fields.summary,
                "description": epic_data.fields.description,
                "status": epic_data.fields.status.name,
            }
            logger.info(f"Successfully retrieved epic data for: {epic_key}")
            logger.debug(f"Epic title: {result['title']}, status: {result['status']}")
            return result
        except Exception as e:
            logger.error(f"Error processing epic data for {epic_key}: {e}")
            return None


    def get_issues_linked_to_epic(self, epic_key: str) -> Optional[List[str]]:
        logger.info(f"Getting issues linked to epic: {epic_key}")
        try:
            jql = f'parent = {epic_key}'
            logger.debug(f"Executing JQL query: {jql}")
            issues = self.jira.search_issues(jql, fields='key')
            issue_keys = [issue.key for issue in issues]
            logger.info(f"Found {len(issue_keys)} issues linked to epic: {epic_key}")
            logger.debug(f"Linked issues: {', '.join(issue_keys) if issue_keys else 'None'}")
            return issue_keys
        except Exception as e:
            logger.error(f"Error getting linked issues for epic {epic_key}: {e}")
            return None
