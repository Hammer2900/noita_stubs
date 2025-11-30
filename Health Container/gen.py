import os
import time
from pathlib import Path
from datetime import datetime

OUTPUT_FILENAME = 'context_bundle.txt'
TARGETS = [
    '/storage/_bottle_area/Noita/drive_c/Games/Noita v02.06.2023/2006631283_helsy_container/data',
    '/storage/_bottle_area/Noita/drive_c/Games/Noita v02.06.2023/2006631283_helsy_container/files',
    '/storage/_bottle_area/Noita/drive_c/Games/Noita v02.06.2023/2006631283_helsy_container/init.lua',
    '/storage/_bottle_area/Noita/drive_c/Games/Noita v02.06.2023/2006631283_helsy_container/settings.lua',
]
TEXT_EXTENSIONS = {'.lua', '.xml',}
IGNORE_DIRS = {'__pycache__', '.git', '.idea', '.vscode'}


def get_readable_size(size_in_bytes):
    """Converts bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f'{size_in_bytes:.2f} {unit}'
        size_in_bytes /= 1024.0
    return f'{size_in_bytes:.2f} PB'


def get_time_elapsed(timestamp):
    """Returns formatted elapsed time string from timestamp."""
    if not timestamp:
        return 'Never'
    diff = time.time() - timestamp
    intervals = (
        ('years', 31536000), ('days', 86400), ('hours', 3600),
        ('mins', 60), ('secs', 1)
    )
    for name, seconds in intervals:
        value = diff // seconds
        if value >= 1:
            return f'{int(value)} {name} ago'
    return 'just now'


def count_tokens(text):
    """Estimates token count."""
    return len(text) // 4


def collect_files(targets):
    """Generator yielding valid text file paths from targets."""
    for path in map(Path, targets):
        if not path.exists():
            print(f'Warning: Path not found: {path}')
            continue

        if path.is_file() and path.suffix in TEXT_EXTENSIONS:
            yield path
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if (file_path.is_file() and
                        file_path.suffix in TEXT_EXTENSIONS and
                        set(file_path.parts).isdisjoint(IGNORE_DIRS)):
                    yield file_path


def get_file_stats(path):
    """Returns a dict with file size, modification time, and token count."""
    if not path.exists():
        return {'size': 0, 'mtime': 0, 'tokens': 0, 'exists': False}

    try:
        content = path.read_text(encoding='utf-8', errors='ignore')
        return {
            'size': path.stat().st_size,
            'mtime': path.stat().st_mtime,
            'tokens': count_tokens(content),
            'exists': True
        }
    except OSError:
        return {'size': 0, 'mtime': 0, 'tokens': 0, 'exists': False}


def main():
    """Main execution flow."""
    root = Path.cwd()
    out_file = root / OUTPUT_FILENAME

    old_stats = get_file_stats(out_file)

    print(f'--- Building context: {OUTPUT_FILENAME} ---')

    current_tokens = 0
    with out_file.open('w', encoding='utf-8') as f_out:
        for file_path in sorted(set(collect_files(TARGETS))):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                f_out.write(f"{'=' * 80}\nFILE PATH: {file_path.resolve()}\n{'=' * 80}\n\n{content}\n\n")
                current_tokens += count_tokens(content)
                print(f'Added: {file_path.relative_to(root) if file_path.is_relative_to(root) else file_path}')
            except Exception as e:
                print(f'Error reading {file_path}: {e}')

    new_stats = get_file_stats(out_file)

    print(f'\n{"=" * 60}\n                 FINAL STATISTICS\n{"=" * 60}')
    print(f" CURRENT SIZE:   {get_readable_size(new_stats['size'])}")
    print(f" TOTAL TOKENS:   ~{current_tokens}")
    print('-' * 60)

    if old_stats['exists']:
        diff_size = new_stats['size'] - old_stats['size']
        diff_tokens = current_tokens - old_stats['tokens']

        sign_map = {True: '+', False: '-'}

        print(
            f" LAST RUN:       {get_time_elapsed(old_stats['mtime'])} ({datetime.fromtimestamp(old_stats['mtime']):%Y-%m-%d %H:%M})")
        print(f" Previous size:  {get_readable_size(old_stats['size'])}")
        print(f" Previous tokens:~{old_stats['tokens']}")
        print('-' * 60)
        print(f" CHANGE:         {sign_map[diff_size >= 0]}{get_readable_size(abs(diff_size))} / "
              f"{sign_map[diff_tokens >= 0]}{abs(diff_tokens)} tokens")
    else:
        print(" (First run, no previous version)")

    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    main()