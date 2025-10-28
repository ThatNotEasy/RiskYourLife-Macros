import requests
import os
import time
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from modules.clients import Colors

class UpdateManager:
    def __init__(self, current_version: str = "2.3"):
        self.current_version = current_version
        self.update_url = "https://api.github.com/repos/ThatNotEasy/RiskYourLife-Macros/releases/latest"
        self.raw_url = "https://raw.githubusercontent.com/ThatNotEasy/RiskYourLife-Macros/main"
        self.download_path = Path("update_temp")

    def get_current_version(self) -> str:
        """Get current version from version.txt file"""
        try:
            if os.path.exists("version.txt"):
                with open("version.txt", "r") as f:
                    return f.read().strip()
        except Exception as e:
            print(f"{Colors.BRIGHT_RED}[ERROR] Failed to read version file: {e}{Colors.RESET}")
        return self.current_version

    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """
        Check for updates from GitHub releases
        Returns update info dict if update available, None otherwise
        """
        try:
            time.sleep(0.030)
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()

            release_data = response.json()

            latest_version = release_data.get("tag_name", "").lstrip("v")
            current_version = self.get_current_version()

            # Compare versions
            if self._compare_versions(latest_version, current_version) > 0:
                print(f"[UPDATE] New version available: {latest_version}")
                print(f"[UPDATE] Current version: {current_version}")

                return {
                    "version": latest_version,
                    "download_url": release_data.get("assets", [{}])[0].get("browser_download_url", ""),
                    "changelog": release_data.get("body", ""),
                    "release_url": release_data.get("html_url", "")
                }
            else:
                return None

        except requests.exceptions.RequestException as e:
            print(f"[UPDATE] Failed to check for updates: {e}")
        except Exception as e:
            print(f"[UPDATE] Error checking for updates: {e}")

        return None

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
        try:
            # Strip 'V' or 'v' prefix if present and clean whitespace
            v1_clean = version1.lstrip('Vv').strip()
            v2_clean = version2.lstrip('Vv').strip()

            v1_parts = [int(x) for x in v1_clean.split(".")]
            v2_parts = [int(x) for x in v2_clean.split(".")]

            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            return 0
        except Exception as e:
            print(f"[UPDATE] Version comparison error: {e}")
            return 0

    def download_update(self, download_url: str) -> bool:
        """Download update file"""
        try:
            print(f"[UPDATE] Downloading update...")

            # Create temp directory
            self.download_path.mkdir(exist_ok=True)

            # Download file
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            # Get filename from URL or headers
            filename = download_url.split("/")[-1]
            if not filename:
                filename = "update.zip"

            file_path = self.download_path / filename

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"[UPDATE] Download completed: {file_path}")
            return True

        except Exception as e:
            print(f"[UPDATE] Failed to download update: {e}")
            return False

    def extract_update(self, zip_path: Path) -> bool:
        """Extract update files"""
        try:
            print(f"[UPDATE] Extracting update...")

            # Extract to temp directory first
            extract_path = self.download_path / "extracted"
            extract_path.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            print(f"[UPDATE] Extraction completed")
            return True

        except Exception as e:
            print(f"[UPDATE] Failed to extract update: {e}")
            return False

    def apply_update(self) -> bool:
        """Apply the downloaded and extracted update"""
        try:
            print(f"[UPDATE] Applying update...")

            extract_path = self.download_path / "extracted"

            # Check if extracted directory exists
            if not extract_path.exists():
                print(f"[UPDATE] Extracted files not found")
                return False

            # Create backup of current version
            backup_path = Path(f"backup_{int(time.time())}")
            backup_path.mkdir(exist_ok=True)

            # Copy current files to backup (excluding certain files)
            exclude_files = {".git", "update_temp", "backup_*", "__pycache__"}
            for item in Path(".").iterdir():
                if item.name not in exclude_files and item.is_file():
                    shutil.copy2(item, backup_path / item.name)

            # Copy new files (excluding update files)
            for item in extract_path.iterdir():
                if item.name not in exclude_files:
                    if item.is_file():
                        shutil.copy2(item, item.name)
                    elif item.is_dir():
                        if item.name == ".git":
                            continue
                        if Path(item.name).exists():
                            shutil.rmtree(item.name)
                        shutil.copytree(item, item.name)

            print(f"[UPDATE] Update applied successfully!")
            print(f"[UPDATE] Backup created at: {backup_path}")
            return True

        except Exception as e:
            print(f"[UPDATE] Failed to apply update: {e}")
            return False

    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.download_path.exists():
                shutil.rmtree(self.download_path)
                print(f"[UPDATE] Temporary files cleaned up")
        except Exception as e:
            print(f"[UPDATE] Failed to cleanup: {e}")

    def perform_update(self, update_info: Dict[str, Any]) -> bool:
        """Perform complete update process"""
        download_url = update_info.get("download_url")

        if not download_url:
            print(f"[UPDATE] No download URL available")
            return False

        # Download update
        if not self.download_update(download_url):
            return False

        # Find downloaded file
        zip_files = list(self.download_path.glob("*.zip"))
        if not zip_files:
            print(f"{Colors.BRIGHT_RED}[UPDATE] No zip file found after download{Colors.RESET}")
            return False

        # Extract update
        if not self.extract_update(zip_files[0]):
            return False

        # Apply update
        if not self.apply_update():
            return False

        # Cleanup
        self.cleanup()

        return True



# Global update manager instance
update_manager = UpdateManager()
