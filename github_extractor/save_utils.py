import json
import os
from itertools import groupby
from pathlib import Path

from common import get_logger # Updated import

# Initialize logger
logger = get_logger(__name__)


def save_diffs_to_files(results: list, card_number: str, output_dir: str = "./commit_diffs"):
    """Save commit diffs to a JSON file grouped by repository."""
    logger.info(f"Saving commit diffs for card: {card_number} to directory: {output_dir}")

    # Create output directory if it doesn't exist
    logger.debug(f"Ensuring output directory exists: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    # Sort and group results by repository
    logger.debug(f"Sorting and grouping {len(results)} results by repository")
    results.sort(key=lambda x: x['repo'])
    groupedByRepo = {key: list(group) for key, group in groupby(results, key=lambda x: x['repo'])}

    # Create file path
    filename = f"{card_number}.json"
    filepath = Path(output_dir) / filename
    logger.debug(f"Writing results to file: {filepath}")

    # Write to file
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(groupedByRepo, f)
            logger.info(f"Successfully saved diffs for card {card_number} to: {filepath}")
    except Exception as e:
        logger.error(f"Error saving diffs to file {filepath}: {e}")
