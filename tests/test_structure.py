from pathlib import Path

def test_required_files():
    root=Path(__file__).resolve().parents[1]
    for name in ["app.py","database/schema.sql","database/seed.sql","src/db.py","powerbi/README.md"]:
        assert (root/name).is_file()
