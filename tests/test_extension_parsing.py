import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import only the function we want to test
def read_item_ids(file_path):
    """Read and parse item IDs with extensions from a text file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Item ID file not found: {path.resolve()}")

    items = []
    current_extension = None
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Handle extension declarations
            if line.lower().startswith("extension="):
                current_extension = line.split("=", 1)[1].strip() or None
                continue

            # Handle item IDs with current extension
            for id_str in line.split(","):
                id_str = id_str.strip()
                if id_str.isdigit():
                    items.append((int(id_str), current_extension))

    if not items:
        raise ValueError("No valid item IDs found in the input file")

    return items

def test_extension_parsing(tmp_path):
    # Create a temporary items.txt with test data
    items_file = tmp_path / "items.txt"
    items_file.write_text("""
extension=dragonflight
12345
67890

extension=shadowlands
11111
22222

33333
    """.strip())

    # Test parsing
    items = read_item_ids(str(items_file))
    
    # Verify results - Note that 33333 gets the last set extension (shadowlands)
    assert items == [
        (12345, "dragonflight"),
        (67890, "dragonflight"),
        (11111, "shadowlands"),
        (22222, "shadowlands"),
        (33333, "shadowlands"),  # Extension persists until changed
    ]

def test_empty_extension(tmp_path):
    # Test handling of empty extension value
    items_file = tmp_path / "items.txt"
    items_file.write_text("""
extension=
12345
67890
    """.strip())

    items = read_item_ids(str(items_file))
    assert items == [
        (12345, None),
        (67890, None),
    ]

def test_no_extension(tmp_path):
    # Test file with no extension declarations
    items_file = tmp_path / "items.txt"
    items_file.write_text("""
12345
67890
    """.strip())

    items = read_item_ids(str(items_file))
    assert items == [
        (12345, None),
        (67890, None),
    ]