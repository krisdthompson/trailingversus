#!/usr/bin/env python3
import os
import sys
import subprocess
import logging
from datetime import datetime

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
    """Dump each verse into a separate file in the Dump directory."""
    dump_dir = ensure_dump_directory()
    
    # Get list of verses
    result = subprocess.run(
        ["docker-compose", "exec", "-T", "trailing", "./manage.py", "dumpdata", "versus.verse", "--indent", "2"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"Error getting verse data: {result.stderr}")
        sys.exit(1)
    
    import json
    verses = json.loads(result.stdout)
    
    # Dump each verse to a separate file
    for verse in verses:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{dump_dir}/verse_{verse['pk']}_{timestamp}.json"
        
        # Create a single-item list for compatibility with loaddata
        verse_data = [verse]
        
        with open(filename, 'w') as f:
            json.dump(verse_data, f, indent=2)
        
        logger.info(f"Dumped verse {verse['pk']} to {filename}")

def load_verse(filename):
    """Load a verse from a dump file."""
    if not filename.endswith('.json'):
        filename += '.json'
    
    dump_dir = ensure_dump_directory()
    filepath = os.path.join(dump_dir, filename)
    
    if not os.path.exists(filepath):
        logger.error(f"Error: File {filepath} not found")
        sys.exit(1)
    
    result = subprocess.run(
        ["docker-compose", "exec", "-T", "trailing", "./manage.py", "loaddata", filepath],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        logger.error(f"Error loading verse data: {result.stderr}")
        sys.exit(1)
    
    logger.info(f"Successfully loaded verse data from {filepath}")

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