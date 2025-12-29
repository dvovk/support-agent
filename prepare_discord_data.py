import os
import json
from bs4 import BeautifulSoup
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_discord_html(file_path: Path) -> list[dict]:
    """Parses a single Discord chat export HTML file."""
    messages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')

        for container in soup.find_all('div', class_='chatlog__message-container'):
            author_tag = container.find('span', class_='chatlog__author')
            timestamp_tag = container.find('span', class_='chatlog__timestamp')
            content_tag = container.find('div', class_='chatlog__content')

            # Skip system messages or messages without key elements
            if not all([author_tag, timestamp_tag, content_tag]):
                continue

            author = author_tag.text.strip()
            timestamp = timestamp_tag.text.strip()
            # Use get_text() to handle complex content like code blocks and mentions correctly
            content = content_tag.get_text(separator='\n', strip=True)

            if author and timestamp and content:
                messages.append({
                    'author': author,
                    'timestamp': timestamp,
                    'content': content,
                    'source': str(file_path.name)
                })
    except Exception as e:
        logging.error(f"Could not parse file {file_path}: {e}")
    
    return messages

def main():
    """
    Finds all HTML files in the 'data' directory, parses them,
    and saves the cleaned messages to a single JSON file.
    """
    data_dir = Path('data')
    output_file = Path('discord_cleaned.json')
    all_messages = []

    if not data_dir.is_dir():
        logging.error(f"Data directory not found: {data_dir}")
        logging.error("Please make sure your Discord HTML exports are placed in a 'data' folder.")
        return

    logging.info(f"Searching for HTML files in '{data_dir}' and its subdirectories...")
    
    # Use rglob to find files in subdirectories as well
    html_files = list(data_dir.rglob('*.html'))

    if not html_files:
        logging.error("No .html files found in the 'data' directory.")
        return

    logging.info(f"Found {len(html_files)} HTML file(s) to parse.")

    for file_path in html_files:
        logging.info(f"Parsing {file_path}...")
        messages = parse_discord_html(file_path)
        all_messages.extend(messages)
        logging.info(f"Parsed {len(messages)} messages from {file_path.name}.")

    logging.info(f"Total messages parsed: {len(all_messages)}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_messages, f, indent=2, ensure_ascii=False)
        logging.info(f"Successfully saved all messages to {output_file}")
    except Exception as e:
        logging.error(f"Could not write to output file {output_file}: {e}")

if __name__ == '__main__':
    main()
