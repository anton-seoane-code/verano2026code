#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico', '.tiff', '.tif'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv', '.md', '.json', '.xml', '.html', '.htm', '.epub'}


def classify(filepath):
    ext = filepath.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return 'images'
    if ext in VIDEO_EXTENSIONS:
        return 'videos'
    if ext in DOCUMENT_EXTENSIONS:
        return 'documents'
    return None


def is_in_subdirectory(filepath, root):
    relative = filepath.relative_to(root)
    return len(relative.parts) > 1


def main():
    parser = argparse.ArgumentParser(description='Classify and organize files in a directory by type.')
    parser.add_argument('directory', help='Path to the directory to analyze')
    parser.add_argument('--dry-run', action='store_true', help='Preview without moving or copying files')
    parser.add_argument('--copy', action='store_true', help='Copy files instead of moving them')
    parser.add_argument('--recursive', action='store_true', help='Scan subdirectories recursively')
    args = parser.parse_args()

    root = Path(args.directory).resolve()
    if not root.is_dir():
        print(f'Error: {root} is not a valid directory')
        return

    categories = {'images': [], 'videos': [], 'documents': []}
    unrecognized = []

    files = [f for f in root.rglob('*') if f.is_file()] if args.recursive else [f for f in root.iterdir() if f.is_file()]

    for filepath in files:
        if is_in_subdirectory(filepath, root):
            continue
        cat = classify(filepath)
        if cat:
            categories[cat].append(filepath)
        else:
            unrecognized.append(filepath)

    total_found = sum(len(v) for v in categories.values()) + len(unrecognized)
    print(f'Found {total_found} files in {root}')
    for cat, cat_files in categories.items():
        print(f'  {cat}: {len(cat_files)}')
    if unrecognized:
        print(f'  unrecognized: {len(unrecognized)}')
    print()

    if args.dry_run:
        print('Dry run — no files were moved or copied')
        return

    for cat, cat_files in categories.items():
        if not cat_files:
            continue
        dest_dir = root / cat
        dest_dir.mkdir(exist_ok=True)
        for src in cat_files:
            dest = dest_dir / src.name
            if dest.exists():
                print(f'Skipped {src.name} — already exists in {cat}/')
                continue
            fn = shutil.copy2 if args.copy else shutil.move
            fn(src, dest)
            action = 'Copied' if args.copy else 'Moved'
            print(f'{action} {src.name} -> {cat}/')

    if unrecognized:
        print(f'\nUnrecognized files ({len(unrecognized)}):')
        for f in unrecognized:
            print(f'  {f.name}')


if __name__ == '__main__':
    main()
