#!/usr/bin/env python3
import os
import sys
import subprocess
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def ensure_dump_directory():
    """Ensure the Dump directory exists."""
    dump_dir = "dump"
    if not os.path.exists(dump_dir):
        os.makedirs(dump_dir)
    return dump_dir

def dump_verses():
    """Dump each verse and its lines into separate files in the Dump directory."""
    dump_dir = ensure_dump_directory()
    
    # Get list of verses
    verse_result = subprocess.run(
        ["docker-compose", "exec", "-T", "trailing", "./manage.py", "dumpdata", "versus.verse", "--indent", "2"],
        capture_output=True,
        text=True
    )
    
    if verse_result.returncode != 0:
        logger.error(f"Error getting verse data: {verse_result.stderr}")
        sys.exit(1)
    
    # Get list of verse lines
    line_result = subprocess.run(
        ["docker-compose", "exec", "-T", "trailing", "./manage.py", "dumpdata", "versus.verseline", "--indent", "2"],
        capture_output=True,
        text=True
    )
    
    if line_result.returncode != 0:
        logger.error(f"Error getting verse line data: {line_result.stderr}")
        sys.exit(1)
    
    verses = json.loads(verse_result.stdout)
    lines = json.loads(line_result.stdout)
    
    # Group lines by verse
    verse_lines = {}
    for line in lines:
        verse_id = line['fields']['verse']
        if verse_id not in verse_lines:
            verse_lines[verse_id] = []
        verse_lines[verse_id].append(line)
    
    # Dump each verse with its lines
    for verse in verses:
        verse_id = verse['pk']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dump_dir}/verse_{verse_id}_{timestamp}.json"
        
        # Create the combined data structure
        verse_data = {
            'verse': verse,
            'lines': verse_lines.get(verse_id, [])
        }
        
        with open(filename, 'w') as f:
            json.dump(verse_data, f, indent=2)
        
        logger.info(f"Dumped verse {verse_id} with {len(verse_lines.get(verse_id, []))} lines to {filename}")

def load_verse(filename):
    """Load a verse and its lines from a dump file."""
    if not filename.endswith('.json'):
        filename += '.json'
    
    dump_dir = ensure_dump_directory()
    filepath = os.path.join(dump_dir, filename)
    
    if not os.path.exists(filepath):
        logger.error(f"Error: File {filepath} not found")
        sys.exit(1)
    
    # Read the combined data
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Create temporary files for verse and lines
    temp_verse_file = os.path.join(dump_dir, f"temp_verse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    temp_lines_file = os.path.join(dump_dir, f"temp_lines_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    try:
        # Write verse data to temp file
        with open(temp_verse_file, 'w') as f:
            json.dump([data['verse']], f, indent=2)
        
        # Load verse first
        verse_result = subprocess.run(
            ["docker-compose", "exec", "-T", "trailing", "./manage.py", "loaddata", temp_verse_file],
            capture_output=True,
            text=True
        )
        
        if verse_result.returncode != 0:
            logger.error(f"Error loading verse data: {verse_result.stderr}")
            sys.exit(1)
        
        if data['lines']:
            # Write lines data to temp file
            with open(temp_lines_file, 'w') as f:
                json.dump(data['lines'], f, indent=2)
            
            # Load lines
            lines_result = subprocess.run(
                ["docker-compose", "exec", "-T", "trailing", "./manage.py", "loaddata", temp_lines_file],
                capture_output=True,
                text=True
            )
            
            if lines_result.returncode != 0:
                logger.error(f"Error loading verse line data: {lines_result.stderr}")
                sys.exit(1)
        
        logger.info(f"Successfully loaded verse and {len(data['lines'])} lines from {filepath}")
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_verse_file):
            os.remove(temp_verse_file)
        if os.path.exists(temp_lines_file):
            os.remove(temp_lines_file)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  To dump all verses: python manage_verses.py dump")
        print("  To load a verse: python manage_verses.py load <filename>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "dump":
        dump_verses()
    elif command == "load":
        if len(sys.argv) < 3:
            print("Error: Please provide a filename to load")
            sys.exit(1)
        load_verse(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main() 