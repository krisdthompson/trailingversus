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
    
    # Main dump file is read from the host's "dump/" directory
    dump_dir = ensure_dump_directory() 
    filepath = os.path.join(dump_dir, filename)
    
    if not os.path.exists(filepath):
        logger.error(f"Error: File {filepath} not found")
        sys.exit(1)
    
    # Read the combined data from the main dump file
    with open(filepath, 'r') as f:
        data = json.load(f)

    # Remove PK from verse to ensure a new ID is assigned by Django
    original_pk_present_in_verse = False
    if 'pk' in data['verse']:
        original_pk_present_in_verse = True
        del data['verse']['pk']

    # If we removed the PK (meaning we intend to create a new verse),
    # modify the slug to prevent collision.
    if original_pk_present_in_verse and 'fields' in data['verse'] and 'slug' in data['verse']['fields']:
        original_slug = data['verse']['fields']['slug']
        # Generate a unique suffix. Using timestamp with microseconds.
        timestamp_suffix = datetime.now().strftime("%Y%m%d%H%M%S%f")
        new_slug = f"{original_slug}-{timestamp_suffix}"
        # Ensure slug doesn't exceed max_length if applicable (truncate if necessary)
        # Assuming a hypothetical max_length of 255 for slug, adjust as per your model
        # max_slug_length = getattr(Verse._meta.get_field('slug'), 'max_length', 255) # This would require Django model access here
        # For now, let's assume slugs can be long enough or handle truncation if you know the limit.
        # Simplified: if len(new_slug) > max_slug_length: new_slug = new_slug[:max_slug_length]
        data['verse']['fields']['slug'] = new_slug
        logger.info(f"Original slug '{original_slug}' modified to '{new_slug}' to ensure uniqueness.")

    # Remove PK from lines to ensure new IDs are assigned by Django.
    if data.get('lines'): # Ensure 'lines' key exists
        for line_obj in data['lines']:
            if 'pk' in line_obj:
                del line_obj['pk']
    
    # Define host and container paths for temporary fixture files
    # These will be placed in a subdirectory of 'webapp/' which is mapped to '/opt/app/'
    temp_fixture_host_base_dir = "webapp"
    temp_fixture_subdir_name = "tmp_loaddata_fixtures"
    temp_fixture_host_path = os.path.join(temp_fixture_host_base_dir, temp_fixture_subdir_name)

    # Ensure the temporary directory exists on the host
    os.makedirs(temp_fixture_host_path, exist_ok=True)

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_verse_basename = f"temp_verse_{timestamp_str}.json"
    temp_lines_basename = f"temp_lines_{timestamp_str}.json"

    # Full host paths for the temporary fixture files
    temp_verse_file_on_host = os.path.join(temp_fixture_host_path, temp_verse_basename)
    temp_lines_file_on_host = os.path.join(temp_fixture_host_path, temp_lines_basename)

    # Corresponding absolute paths for these files inside the container
    # Assumes $PWD/webapp on host is mapped to /opt/app in container
    temp_verse_file_in_container = f"/opt/app/{temp_fixture_subdir_name}/{temp_verse_basename}"
    temp_lines_file_in_container = f"/opt/app/{temp_fixture_subdir_name}/{temp_lines_basename}"
    
    new_verse_pk = None # To store the PK of the newly created verse

    try:
        # Write verse data to temp file on host (in webapp/tmp_loaddata_fixtures/)
        # The data['verse'] object no longer contains a 'pk' field.
        with open(temp_verse_file_on_host, 'w') as f:
            json.dump([data['verse']], f, indent=2)
        
        # Load verse using the container-accessible path
        verse_result = subprocess.run(
            ["docker-compose", "exec", "-T", "trailing", "./manage.py", "loaddata", temp_verse_file_in_container],
            capture_output=True,
            text=True
        )
        
        if verse_result.returncode != 0:
            logger.error(f"Error loading verse data: {verse_result.stderr}")
            # Clean up before exiting if verse loading failed
            if os.path.exists(temp_verse_file_on_host):
                os.remove(temp_verse_file_on_host)
            sys.exit(1)
        
        # If verse was loaded and its slug was modified, try to get its new PK
        if original_pk_present_in_verse: # Indicates we intended to create a new verse
            # The slug used for loading was data['verse']['fields']['slug'] (the potentially modified one)
            slug_to_find = data['verse']['fields']['slug']
            get_pk_command = [
                "docker-compose", "exec", "-T", "trailing", 
                "./manage.py", "shell", "-c", 
                f"from versus.models import Verse; print(Verse.objects.get(slug='{slug_to_find}').pk)"
            ]
            pk_result = subprocess.run(get_pk_command, capture_output=True, text=True)
            
            # Extract the last non-empty line from stdout, which should be the PK
            potential_pk_lines = [line for line in pk_result.stdout.strip().split('\n') if line.strip()]
            extracted_pk_str = potential_pk_lines[-1] if potential_pk_lines else ""

            if pk_result.returncode == 0 and extracted_pk_str.isdigit():
                new_verse_pk = int(extracted_pk_str)
                logger.info(f"Successfully retrieved new PK {new_verse_pk} for verse with slug '{slug_to_find}'.")
            else:
                logger.error(f"Could not retrieve new PK for verse with slug '{slug_to_find}'. stdout: '{pk_result.stdout.strip()}', stderr: '{pk_result.stderr.strip()}'")
                # Decide if you want to exit or try to load lines with original FKs (which will likely fail as before or misassociate)
                sys.exit(1) # Exiting for safety

        if data.get('lines'):
            if new_verse_pk is not None:
                logger.info(f"Updating foreign keys for {len(data['lines'])} lines to new verse PK {new_verse_pk}.")
                for line_obj in data['lines']:
                    if 'fields' in line_obj and 'verse' in line_obj['fields']:
                        original_fk = line_obj['fields']['verse']
                        line_obj['fields']['verse'] = new_verse_pk
                        # logger.debug(f"Updated line FK from {original_fk} to {new_verse_pk}") # Optional: for verbose logging
            else:
                # This case should ideally not be reached if original_pk_present_in_verse was true,
                # as we exit if new_verse_pk isn't found.
                # If original_pk_present_in_verse was false, lines are loaded with original FKs (intended for updating existing verse).
                if original_pk_present_in_verse:
                     logger.warning("New verse PK not available. Lines will be loaded with original foreign keys, which might cause issues or misassociation.")

            # Write lines data to temp file on host (in webapp/tmp_loaddata_fixtures/)
            # The line objects in data['lines'] no longer contain 'pk' fields.
            with open(temp_lines_file_on_host, 'w') as f:
                json.dump(data['lines'], f, indent=2)
            
            # Load lines using the container-accessible path
            lines_result = subprocess.run(
                ["docker-compose", "exec", "-T", "trailing", "./manage.py", "loaddata", temp_lines_file_in_container],
                capture_output=True,
                text=True
            )
            
            if lines_result.returncode != 0:
                logger.error(f"Error loading verse line data: {lines_result.stderr}")
                # Clean up lines file if it exists, verse file was already loaded
                if os.path.exists(temp_lines_file_on_host):
                    os.remove(temp_lines_file_on_host)
                sys.exit(1) # Consider if you want to rollback verse load or just report error
        
        logger.info(f"Successfully loaded verse and {len(data['lines'])} lines from {filepath}")
    
    finally:
        # Clean up temporary files from the host
        if os.path.exists(temp_verse_file_on_host):
            os.remove(temp_verse_file_on_host)
        if os.path.exists(temp_lines_file_on_host):
            os.remove(temp_lines_file_on_host)
        
        # Attempt to remove the temporary directory if it's empty
        try:
            if os.path.exists(temp_fixture_host_path) and not os.listdir(temp_fixture_host_path):
                os.rmdir(temp_fixture_host_path)
        except OSError as e:
            # This might fail if another process created a file there, or if it was already removed.
            # It's not critical, so just log a warning.
            logger.warning(f"Could not remove temporary directory {temp_fixture_host_path}: {e}")

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