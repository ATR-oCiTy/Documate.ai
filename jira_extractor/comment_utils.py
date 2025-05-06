import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
import json

def add_comment(confluence_page_url: str, epic_key: str):
    load_dotenv()
    # Use the passed epic_key argument instead of os.environ.get('EPIC_KEY')
    url = f"{os.environ.get('JIRA_SERVER')}/rest/api/2/issue/{epic_key}/comment"
    auth = HTTPBasicAuth(os.environ.get("JIRA_USERNAME"), os.environ.get("JIRA_PASSWORD"))
    headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
    }
    payload = json.dumps( {
      "body": "(AI Generated Content) New technical documentation page created on Confluence: " + confluence_page_url
    } )

    requests.request(
       "POST",
       url,
       data=payload,
       headers=headers,
       auth=auth
    )