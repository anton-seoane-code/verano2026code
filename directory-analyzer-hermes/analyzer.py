#!/usr/bin/env python3
"""
Directory Analyzer (Hermes Edition)
Scans a directory, classifies files by type (images, videos, documents),
and organizes them into auto-created subdirectories.
"""
import argparse
import hashlib
import shutil
import sys
from collections import defaultdict
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpeg', '.mpg'}
DOCUMENT_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.md', '.json', '.xml', '.html', '.htm',
    '.epub', '.odt', '.ods', '.odp', '.rtf', '.tex',
}

CATEGORY_DIRS = {
    'images': '📷 Images',
    'videos': '🎬 Videos',
    'documents': '📄 Documents',
}


def classify(filepath):
    """Classify a file into 'images', 'videos', 'documents', or None."""
    ext = filepath.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return 'images'
    if ext in VIDEO_EXTENSIONS:
        return 'videos'
    if ext in DOCUMENT_EXTENSIONS:
        return 'documents'
    return None


def is_in_subdirectory(filepath, root):
    """Check if a file is already inside a subdirectory of root."""
    try:
        relative = filepath.relative_to(root)
        return len(relative.parts) > 1
    except ValueError:
        return False


def scan(directory, recursive=False):
    """Scan a directory and classify files into categories."""
    root = Path(directory).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f'{root} is not a valid directory')

    categories = {'images': [], 'videos': [], 'documents': []}
    unrecognized = []

    pattern = '**/*' if recursive else '*'
    files = [f for f in root.glob(pattern) if f.is_file()]

    for filepath in files:
        if is_in_subdirectory(filepath, root):
            continue
        cat = classify(filepath)
        if cat:
            categories[cat].append(filepath)
        else:
            unrecognized.append(filepath)

    return categories, unrecognized


def find_duplicates(files):
    """Find duplicate files by SHA256 hash."""
    size_groups = defaultdict(list)
    for f in files:
        try:
            size_groups[f.stat().st_size].append(f)
        except OSError:
            continue

    duplicates = defaultdict(list)
    for size, group in size_groups.items():
        if len(group) < 2:
            continue
        hashes = defaultdict(list)
        for f in group:
            try:
                h = hashlib.sha256(f.read_bytes()).hexdigest()
                hashes[h].append(f)
            except OSError:
                continue
        for h, dup_group in hashes.items():
            if len(dup_group) > 1:
                duplicates[h].extend(dup_group)

    return dict(duplicates)


def organize(categories, root, copy=False):
    """Organize files into categorized subdirectories."""
    root = Path(root).resolve()
    stats = {}

    for cat, cat_files in categories.items():
        if not cat_files:
            stats[cat] = {'moved': 0, 'skipped': 0}
            continue

        dest_dir = root / CATEGORY_DIRS[cat]
        moved = 0
        skipped = 0
        dest_dir.mkdir(exist_ok=True)

        for src in cat_files:
            dest = dest_dir / src.name
            if dest.exists():
                skipped += 1
                continue
            fn = shutil.copy2 if copy else shutil.move
            fn(str(src), str(dest))
            moved += 1

        stats[cat] = {'moved': moved, 'skipped': skipped}

    return stats


def generate_report(categories, unrecognized, duplicates=None, organize_stats=None, directory=''):
    """Generate a formatted text report."""
    lines = []
    lines.append('=' * 58)
    lines.append('   Directory Analyzer Report')
    lines.append(f'   Directory: {directory}')
    lines.append('=' * 58)
    lines.append('')

    total = sum(len(v) for v in categories.values()) + len(unrecognized)
    lines.append(f'  Total files found: {total}')
    lines.append('')

    lines.append('  By category:')
    for cat in ['images', 'videos', 'documents']:
        count = len(categories.get(cat, []))
        lines.append(f'    {CATEGORY_DIRS[cat]}: {count}')
    if unrecognized:
        lines.append(f'    Unrecognized: {len(unrecognized)}')
    lines.append('')

    if duplicates:
        dup_count = sum(len(v) for v in duplicates.values())
        dup_groups = len(duplicates)
        lines.append(f'  Duplicate files: {dup_count} files in {dup_groups} group(s)')
        for h, dup_files in duplicates.items():
            lines.append(f'    Hash {h[:12]}... ({len(dup_files)} files):')
            for f in dup_files:
                lines.append(f'      - {f.name}')
        lines.append('')

    if organize_stats:
        stats_values = [v for k, v in organize_stats.items() if not k.startswith('_')]
        total_moved = sum(v['moved'] for v in stats_values)
        total_skipped = sum(v['skipped'] for v in stats_values)
        action = 'Copied' if organize_stats.get('_copy', False) else 'Moved'
        lines.append(f'  {action}: {total_moved} files')
        lines.append(f'  Skipped: {total_skipped} files')
        for cat, st in organize_stats.items():
            if cat.startswith('_'):
                continue
            if st['moved'] > 0 or st['skipped'] > 0:
                lines.append(f'    {CATEGORY_DIRS[cat]}: {st["moved"]} {action.lower()}, {st["skipped"]} skipped')
        lines.append('')

    if unrecognized:
        lines.append('  Unrecognized files:')
        for f in unrecognized:
            lines.append(f'    - {f.name}')
        lines.append('')

    lines.append('=' * 58)
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Analyze and organize files in a directory by type.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  %(prog)s ~/Downloads                     # scan and organize\n'
            '  %(prog)s ~/Downloads --dry-run            # preview only\n'
            '  %(prog)s ~/Downloads --copy               # copy instead of move\n'
            '  %(prog)s ~/Downloads --recursive          # scan subdirectories too\n'
            '  %(prog)s ~/Downloads --detect-duplicates  # find duplicates\n'
            '  %(prog)s ~/Downloads --analyze-only       # just report, no moves'
        ),
    )
    parser.add_argument('directory', help='Path to the directory to analyze')
    parser.add_argument('--dry-run', action='store_true', help='Preview without moving or copying files')
    parser.add_argument('--copy', action='store_true', help='Copy files instead of moving them')
    parser.add_argument('--recursive', action='store_true', help='Scan subdirectories recursively')
    parser.add_argument('--detect-duplicates', action='store_true', help='Detect duplicate files by SHA256 hash')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze, do not organize')
    args = parser.parse_args()

    try:
        categories, unrecognized = scan(args.directory, args.recursive)
    except (NotADirectoryError, PermissionError, FileNotFoundError) as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    all_files = []
    for v in categories.values():
        all_files.extend(v)
    all_files.extend(unrecognized)

    duplicates = find_duplicates(all_files) if args.detect_duplicates else None

    organize_stats = None
    if not args.analyze_only and not args.dry_run:
        organize_stats = organize(categories, args.directory, args.copy)
        organize_stats['_copy'] = args.copy

    report = generate_report(categories, unrecognized, duplicates, organize_stats, args.directory)
    print(report)

    # Show folder structure created
    if organize_stats and not args.dry_run:
        root = Path(args.directory).resolve()
        print('  Folder structure:')
        for cat in ['images', 'videos', 'documents']:
            st = organize_stats.get(cat, {'moved': 0})
            if st['moved'] > 0 or st['skipped'] > 0:
                print(f'    📁 {CATEGORY_DIRS[cat]}/')
        print()


if __name__ == '__main__':
    main()
