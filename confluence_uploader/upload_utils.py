import os
import requests

# --- Markdown Utils ---
def convert_markdown_to_html(file_path: str) -> str:
    with open(file_path, 'r') as f:
        markdown_text = f.read()
    return markdown_text

# --- Confluence API ---
def create_confluence_page(title: str, html_content: str) -> str:
    CONFLUENCE_BASE_URL = os.environ.get('CONFLUENCE_BASE_URL')
    AUTH = (os.environ.get('JIRA_USERNAME'), os.environ.get('JIRA_PASSWORD'))
    SPACE_KEY = os.environ.get('SPACE_KEY')

    url = f'{CONFLUENCE_BASE_URL}/rest/api/content'
    payload = {
        'type': 'page',
        'title': title,
        'space': {'key': SPACE_KEY},
        'body': {
            'storage': {
                'value': html_content,
                'representation': 'storage'
            }
        }
    }

    response = requests.post(url, json=payload, auth=AUTH)
    response.raise_for_status()
    result = response.json()
    return f"{CONFLUENCE_BASE_URL}{result['_links']['webui']}"