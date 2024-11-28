# app/functions/base/tile_naming.py
import re
from dataclasses import dataclass

@dataclass
class TileCoordinates:
    parent_row: int
    parent_col: int
    child_row: int | None = None
    child_col: int | None = None

class TileNaming:
    # Regex patterns for tile filenames
    ORIGINAL_PATTERN = r'\d+-(\d+)_(\d+)\.png$'
    SUBDIVIDED_PATTERN = r'(\d+)-(\d+)_(\d+)-(\d+)\.png$'

    @staticmethod
    def parse_original_tile_name(filename: str) -> TileCoordinates:
        """Parse original tile filename to get coordinates."""
        match = re.search(TileNaming.ORIGINAL_PATTERN, filename)
        if not match:
            raise ValueError(f"Invalid original tile filename format: {filename}")
        return TileCoordinates(
            parent_row=int(match.group(1)),
            parent_col=int(match.group(2))
        )

    @staticmethod
    def parse_subdivided_tile_name(filename: str) -> TileCoordinates:
        """Parse subdivided tile filename to get coordinates."""
        match = re.search(TileNaming.SUBDIVIDED_PATTERN, filename)
        if not match:
            raise ValueError(f"Invalid subdivided tile filename format: {filename}")
        return TileCoordinates(
            parent_row=int(match.group(1)),
            parent_col=int(match.group(2)),
            child_row=int(match.group(3)),
            child_col=int(match.group(4))
        )

    @staticmethod
    def create_subdivided_tile_name(parent_row: int, parent_col: int, 
                                  child_row: int, child_col: int) -> str:
        """Create a subdivided tile filename."""
        return f"{parent_row}-{parent_col}_{child_row}-{child_col}.png"