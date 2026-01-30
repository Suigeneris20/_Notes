# find_files_advanced.py

import argparse
import os
import sys
from pathlib import Path
import tarfile
import zipfile
import requests
import json
import yaml  # Requires PyYAML: pip install PyYAML
import tempfile
import io

def search_local_path(local_path: Path, targets: set[str]) -> list[dict]:
    """Recursively searches a local filesystem path for target files."""
    print(f"\n--- Searching Local Filesystem ---")
    results = []
    
    if not local_path.is_dir():
        print(f"ERROR: Local path '{local_path}' is not a valid directory.", file=sys.stderr)
        return results
    
    print(f"Recursively searching in: {local_path.resolve()}")
    
    for file_path in local_path.rglob('*'):
        if file_path.is_file() and file_path.name in targets:
            location_details = {
                "source": "Local Filesystem",
                "filename": file_path.name,
                "absolute_path": str(file_path.resolve())
            }
            results.append(location_details)
            print(f"  [FOUND] {file_path.name} at {file_path.resolve()}")

    return results

def search_artifactory_nested(url: str, api_key: str | None, targets: set[str]) -> list[dict]:
    """
    Downloads and searches a nested archive structure (zip -> zip -> tar.gz).
    """
    print(f"\n--- Searching Artifactory Package ---")
    print(f"URL: {url}")
    results = []

    headers = {}
    if api_key:
        headers["X-Jfrog-Art-Api"] = api_key

    try:
        response = requests.get(url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_file.flush()
            print("Successfully downloaded outer zip package.")

            # --- 1. Process the Outer ZIP ---
            with zipfile.ZipFile(tmp_file.name, 'r') as outer_zip:
                print(f"\nInspecting outer zip: {Path(tmp_file.name).name}")
                inner_zip_info = None
                for member in outer_zip.infolist():
                    member_filename = Path(member.filename).name
                    if member_filename in targets:
                        location_details = {
                            "source": "Artifactory",
                            "filename": member_filename,
                            "path_in_archive": member.filename,
                        }
                        results.append(location_details)
                        print(f"  [FOUND] {member_filename} in outer zip at '{member.filename}'")
                    
                    if member.filename.endswith('.zip'):
                        inner_zip_info = member
                        print(f"  [INFO] Found inner zip: '{member.filename}'")

                if not inner_zip_info:
                    print("  [WARN] No inner zip file found in the outer archive.")
                    return results

                # --- 2. Process the Inner ZIP (in memory) ---
                print(f"\nInspecting inner zip: {inner_zip_info.filename}")
                inner_zip_bytes = outer_zip.read(inner_zip_info.filename)
                with zipfile.ZipFile(io.BytesIO(inner_zip_bytes), 'r') as inner_zip:
                    tarball_info = None
                    for member in inner_zip.infolist():
                        member_filename = Path(member.filename).name
                        if member_filename in targets:
                            location_details = {
                                "source": "Artifactory",
                                "filename": member_filename,
                                "path_in_archive": f"{inner_zip_info.filename}/{member.filename}",
                            }
                            results.append(location_details)
                            print(f"  [FOUND] {member_filename} in inner zip at '{member.filename}'")
                        
                        if member.filename.endswith(('.tar.gz', '.tar')):
                            tarball_info = member
                            print(f"  [INFO] Found tarball: '{member.filename}'")

                    if not tarball_info:
                        print("  [WARN] No .tar.gz or .tar file found in the inner zip.")
                        return results
                    
                    # --- 3. Process the TAR.GZ (in memory) ---
                    print(f"\nInspecting tarball: {tarball_info.filename}")
                    tarball_bytes = inner_zip.read(tarball_info.filename)
                    # Use fileobj argument to read from in-memory bytes
                    with tarfile.open(fileobj=io.BytesIO(tarball_bytes), mode='r:*') as tar:
                        for member in tar.getmembers():
                            if member.isfile():
                                member_filename = Path(member.name).name
                                if member_filename in targets:
                                    location_details = {
                                        "source": "Artifactory",
                                        "filename": member_filename,
                                        "path_in_archive": f"{inner_zip_info.filename}/{tarball_info.filename}/{member.name}",
                                    }
                                    results.append(location_details)
                                    print(f"  [FOUND] {member_filename} in tarball at '{member.name}'")
        return results

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download from Artifactory: {e}", file=sys.stderr)
    except (zipfile.BadZipFile, tarfile.ReadError) as e:
        print(f"ERROR: Archive is corrupted or has an invalid format: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred during Artifactory search: {e}", file=sys.stderr)
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Search for files in a nested Artifactory archive and a local directory.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # ... (same arguments as before, with added format/output) ...
    parser.add_argument('--targets', required=True, nargs='+', help="Filenames to search for.")
    parser.add_argument('--artifactory-url', required=True, help="Full URL to the outer .zip package.")
    parser.add_argument('--local-path', required=True, help="Local Linux directory to search recursively.")
    parser.add_argument('--api-key', help="Optional: Artifactory API key.")
    parser.add_argument('--output-file', help="Optional: Path to save the report file.")
    parser.add_argument('--format', choices=['json', 'yaml'], default='yaml', help="Output format.")
    args = parser.parse_args()

    target_files = set(args.targets)
    all_results = []
    
    # Perform searches and collect structured results
    all_results.extend(search_artifactory_nested(args.artifactory_url, args.api_key, target_files))
    all_results.extend(search_local_path(Path(args.local_path), target_files))

    # --- Generate the final report object ---
    report = {target: {"status": "NOT_FOUND", "locations": []} for target in target_files}
    for res in all_results:
        filename = res["filename"]
        if filename in report:
            report[filename]["status"] = "FOUND"
            report[filename]["locations"].append(res)
    
    # --- Output the report ---
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            if args.format == 'json':
                json.dump(report, f, indent=2)
            else: # yaml
                yaml.dump(report, f, indent=2, sort_keys=False)
        print(f"\nReport successfully saved to '{output_path}'")
    else:
        print("\n\n" + "="*20 + " SEARCH REPORT " + "="*20)
        if args.format == 'json':
            print(json.dumps(report, indent=2))
        else: # yaml
            print(yaml.dump(report, indent=2, sort_keys=False))
        print("="*55)

if __name__ == "__main__":
    main()
