# find_files.py

import argparse
import os
import sys
from pathlib import Path
import tarfile
import tempfile
import requests
from collections import defaultdict

def search_in_tarball(url: str, api_key: str | None, targets: set[str], results: defaultdict) -> None:
    """
    Downloads a .tar.gz file from an Artifactory URL and searches for target files within it.
    """
    print(f"\n--- Searching Artifactory Package ---")
    print(f"URL: {url}")

    headers = {}
    if api_key:
        headers["X-Jfrog-Art-Api"] = api_key

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)

        # Use a temporary file to store the downloaded content
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=True) as tmp_file:
            # Download the file in chunks
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file.flush() # Ensure all content is written to disk before reading

            print(f"Successfully downloaded package to temporary file.")

            # Open the tarball for reading with gzip compression
            with tarfile.open(tmp_file.name, 'r:gz') as tar:
                print("Inspecting package contents...")
                found_in_tar = 0
                for member in tar.getmembers():
                    # We only care about files, not directories
                    if member.isfile():
                        member_filename = Path(member.name).name
                        if member_filename in targets:
                            location_str = f"Artifactory Package -> {member.name}"
                            results[member_filename].append(location_str)
                            found_in_tar += 1
                
                if found_in_tar == 0:
                    print("Found no matching files in the package.")


    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download from Artifactory: {e}", file=sys.stderr)
    except tarfile.ReadError:
        print(f"ERROR: The downloaded file is not a valid .tar.gz archive.", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during tarball search: {e}", file=sys.stderr)


def search_in_local_path(local_path: Path, targets: set[str], results: defaultdict) -> None:
    """
    Recursively searches a local filesystem path for target files.
    """
    print(f"\n--- Searching Local Filesystem ---")
    
    if not local_path.is_dir():
        print(f"ERROR: Local path '{local_path}' is not a valid directory.", file=sys.stderr)
        return
    
    print(f"Recursively searching in: {local_path.resolve()}")
    
    found_in_local = 0
    for file_path in local_path.rglob('*'):
        if file_path.is_file() and file_path.name in targets:
            location_str = f"Local Filesystem -> {file_path.resolve()}"
            results[file_path.name].append(location_str)
            found_in_local += 1
    
    if found_in_local == 0:
        print("Found no matching files in the local path.")


def main():
    """Main function to parse arguments and orchestrate the search."""
    parser = argparse.ArgumentParser(
        description="Search for files in an Artifactory .tar.gz package and a local directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--targets', 
        required=True, 
        nargs='+', 
        help="One or more target filenames to search for (e.g., launcher.sh settings.xml)"
    )
    parser.add_argument(
        '--artifactory-url', 
        required=True, 
        help="The full URL to the .tar.gz package in Artifactory."
    )
    parser.add_argument(
        '--local-path', 
        required=True, 
        help="The local Linux directory to search recursively (e.g., the build directory of the 'larger repo')."
    )
    parser.add_argument(
        '--api-key', 
        help="Optional: Your Artifactory API key for authentication."
    )
    args = parser.parse_args()

    # Use a set for faster lookups
    target_files = set(args.targets)
    
    # Use defaultdict to simplify appending results
    found_files = defaultdict(list)

    # Perform the searches
    search_in_tarball(args.artifactory_url, args.api_key, target_files, found_files)
    search_in_local_path(Path(args.local_path), target_files, found_files)

    # --- Print the final report ---
    print("\n\n" + "="*20 + " SEARCH REPORT " + "="*20)
    all_targets = set(args.targets)
    found_targets = set(found_files.keys())
    
    for target in sorted(list(all_targets)):
        print(f"\nFile: '{target}'")
        if target in found_files:
            print("  Status: FOUND")
            for loc in found_files[target]:
                print(f"    - {loc}")
        else:
            print("  Status: NOT FOUND in any location.")
    
    print("\n" + "="*55)


if __name__ == "__main__":
    main()
