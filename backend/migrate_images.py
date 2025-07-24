#!/usr/bin/env python3
"""
Migration script to rename image files from ID-based to slug-based filenames
"""
import json
import os
import shutil

def main():
    # Read poems to get the filename mappings
    with open('poems.json', 'r') as f:
        poems = json.load(f)

    print('Migrating image files to slug-based filenames...')
    images_dir = 'static/images'

    if not os.path.exists(images_dir):
        print(f'Images directory {images_dir} does not exist')
        return

    renamed_count = 0
    skipped_count = 0

    for poem in poems:
        old_filename = f'{poem["id"]}.png'
        old_path = os.path.join(images_dir, old_filename)
        
        if poem.get('image_filename') and os.path.exists(old_path):
            new_filename = poem['image_filename']
            new_path = os.path.join(images_dir, new_filename)
            
            # Only rename if the new filename is different
            if old_filename != new_filename:
                if os.path.exists(new_path):
                    print(f'SKIP: {new_filename} already exists')
                    skipped_count += 1
                else:
                    shutil.move(old_path, new_path)
                    print(f'RENAMED: {old_filename} -> {new_filename}')
                    renamed_count += 1
            else:
                print(f'SKIP: {old_filename} already has correct name')
                skipped_count += 1
        elif os.path.exists(old_path):
            print(f'SKIP: {old_filename} (no slug filename for poem {poem["id"]})')
            skipped_count += 1

    print(f'\nMigration complete: {renamed_count} renamed, {skipped_count} skipped')

if __name__ == '__main__':
    main()