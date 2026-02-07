"""
Storage module for managing job snapshots.

Handles saving, loading, and managing historical snapshots of job listings.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from sjs_jobwatch.core import config
from sjs_jobwatch.core.models import Snapshot

logger = logging.getLogger(__name__)


class SnapshotStore:
    """
    Filesystem-based storage for job snapshots.
    
    Snapshots are stored as JSON files with timestamps in the filename.
    This provides:
    - Simple, readable storage format
    - Easy manual inspection
    - Natural chronological ordering
    - Git-friendly diffs (if desired)
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        """
        Initialize snapshot storage.
        
        Args:
            base_dir: Directory to store snapshots (defaults to config.SNAPSHOT_DIR)
        """
        self.base_dir = base_dir or config.SNAPSHOT_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, snapshot: Snapshot) -> Path:
        """
        Save a snapshot to disk.
        
        Args:
            snapshot: Snapshot to save
            
        Returns:
            Path where snapshot was saved
        """
        filename = self._get_filename(snapshot.timestamp)
        filepath = self.base_dir / filename

        # Convert to JSON
        data = snapshot.model_dump(mode="json")

        # Write atomically (write to temp file, then rename)
        temp_path = filepath.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_path.rename(filepath)
            logger.info(f"Saved snapshot with {len(snapshot.jobs)} jobs to {filepath}")
            return filepath
        except Exception as e:
            # Clean up temp file if something went wrong
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed to save snapshot: {e}") from e

    def load(self, timestamp: datetime) -> Optional[Snapshot]:
        """
        Load a specific snapshot by timestamp.
        
        Args:
            timestamp: Timestamp of snapshot to load
            
        Returns:
            Snapshot or None if not found
        """
        filename = self._get_filename(timestamp)
        filepath = self.base_dir / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Snapshot(**data)
        except Exception as e:
            logger.error(f"Failed to load snapshot from {filepath}: {e}")
            return None

    def load_latest(self, n: int = 1) -> list[Snapshot]:
        """
        Load the most recent N snapshots.
        
        Args:
            n: Number of snapshots to load
            
        Returns:
            List of snapshots (newest first)
        """
        files = self.list_snapshots()
        
        snapshots = []
        for filepath in files[:n]:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                snapshot = Snapshot(**data)
                snapshots.append(snapshot)
            except Exception as e:
                logger.warning(f"Failed to load snapshot from {filepath}: {e}")
                continue

        return snapshots

    def list_snapshots(self) -> list[Path]:
        """
        List all snapshot files, sorted by timestamp (newest first).
        
        Returns:
            List of snapshot file paths
        """
        files = list(self.base_dir.glob("snapshot_*.json"))
        # Sort by modification time, newest first
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return files

    def count(self) -> int:
        """Get total number of snapshots stored."""
        return len(self.list_snapshots())

    def prune_old_snapshots(
        self,
        days: Optional[int] = None,
        max_count: Optional[int] = None,
    ) -> int:
        """
        Remove old snapshots based on age or count limits.
        
        Args:
            days: Remove snapshots older than this many days (None = use config)
            max_count: Keep at most this many snapshots (None = use config)
            
        Returns:
            Number of snapshots deleted
        """
        days = days if days is not None else config.SNAPSHOT_RETENTION_DAYS
        max_count = max_count if max_count is not None else config.MAX_SNAPSHOTS

        all_files = self.list_snapshots()
        to_delete = []

        # Check age limit
        if days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            for filepath in all_files:
                timestamp = self._parse_timestamp_from_filename(filepath.name)
                if timestamp and timestamp < cutoff:
                    to_delete.append(filepath)

        # Check count limit
        if max_count > 0 and len(all_files) > max_count:
            # Keep the newest max_count, delete the rest
            to_delete.extend(all_files[max_count:])

        # Remove duplicates
        to_delete = list(set(to_delete))

        # Delete files
        deleted = 0
        for filepath in to_delete:
            try:
                filepath.unlink()
                deleted += 1
                logger.debug(f"Deleted old snapshot: {filepath.name}")
            except Exception as e:
                logger.warning(f"Failed to delete {filepath}: {e}")

        if deleted > 0:
            logger.info(f"Pruned {deleted} old snapshots")

        return deleted

    def export_to_csv(self, snapshot: Snapshot, output_path: Path) -> None:
        """
        Export a snapshot to CSV format.
        
        Args:
            snapshot: Snapshot to export
            output_path: Where to save the CSV
        """
        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            if not snapshot.jobs:
                return

            # Use all fields from the first job as headers
            fieldnames = list(snapshot.jobs[0].model_dump().keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            for job in snapshot.jobs:
                # Convert job to dict, handling None values
                row = job.model_dump(mode="json")
                writer.writerow(row)

        logger.info(f"Exported {len(snapshot.jobs)} jobs to {output_path}")

    def export_to_json(self, snapshot: Snapshot, output_path: Path) -> None:
        """
        Export a snapshot to JSON format.
        
        Args:
            snapshot: Snapshot to export
            output_path: Where to save the JSON
        """
        data = snapshot.model_dump(mode="json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported snapshot to {output_path}")

    @staticmethod
    def _get_filename(timestamp: datetime) -> str:
        """
        Generate filename for a snapshot.
        
        Format: snapshot_YYYY-MM-DD_HH-MM-SS.json
        """
        return timestamp.strftime("snapshot_%Y-%m-%d_%H-%M-%S.json")

    @staticmethod
    def _parse_timestamp_from_filename(filename: str) -> Optional[datetime]:
        """
        Extract timestamp from a snapshot filename.
        
        Args:
            filename: Snapshot filename
            
        Returns:
            Datetime or None if parsing fails
        """
        try:
            # Remove prefix and suffix
            date_str = filename.replace("snapshot_", "").replace(".json", "")
            return datetime.strptime(date_str, "%Y-%m-%d_%H-%M-%S")
        except ValueError:
            return None
