from pathlib import Path

PATH_DATA = Path(__file__).parent.parent / 'data'
if not PATH_DATA.exists():
    PATH_DATA.mkdir(parents=True)