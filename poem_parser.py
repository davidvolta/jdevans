#!/usr/bin/env python3
"""
Poem Parser
Converts text files of poems to JSON format.
Each poem has a title, content, signature, and ID.
Can process multiple files in batch.
"""

import json
import re
import os
import glob
from collections import OrderedDict

def is_signature_end(line):
    # End of signature if line contains 'occasionally' or 'occsinlly' and ends with ')'
    l = line.lower()
    return (('occasionally' in l or 'occsinlly' in l) and l.endswith(')'))

def parse_poems(file_path):
    """
    Parse poems from a text file and return a list of poem dictionaries.
    
    Args:
        file_path: Path to the text file containing poems
        
    Returns:
        List of dictionaries, each containing id, title, content, and signature
    """
    poems = []
    poem_id = 1
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    lines = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                lines = file.readlines()
            print(f"    Successfully read with {encoding} encoding")
            break
        except UnicodeDecodeError:
            continue
    
    if lines is None:
        raise Exception(f"Could not read file with any of the attempted encodings: {encodings}")

    n = len(lines)
    i = 0
    while i < n:
        # Skip leading blank lines
        while i < n and not lines[i].strip():
            i += 1
        if i >= n:
            break
        # Title: first one or two non-empty lines
        title_lines = [lines[i].strip()]
        i += 1
        if i < n:
            next_line = lines[i].strip()
            if next_line and not (next_line.startswith('(') and ('J.D. Evans' in next_line or 'J.D. Evns' in next_line)):
                if len(next_line) < 60:
                    title_lines.append(next_line)
                    i += 1
        title = ' '.join(title_lines)
        # Collect poem content until signature
        content_lines = []
        signature = ""
        while i < n:
            line = lines[i].strip()
            if not line:
                content_lines.append('')
                i += 1
                continue
            
            # Check if this is the start of a signature (starts with '(' and contains 'J.D. Evans' or 'J.D. Evns')
            if line.startswith('(') and ('J.D. Evans' in line or 'J.D. Evns' in line):
                # Collect signature lines until we find one with 'occasionally' or 'occsinlly' and ending with ')'
                signature_lines = [line]
                i += 1
                signature_complete = False
                while i < n and not signature_complete:
                    sig_line = lines[i].strip()
                    signature_lines.append(sig_line)
                    if is_signature_end(sig_line):
                        signature_complete = True
                    i += 1
                signature = '\n'.join(signature_lines)
                break
            else:
                content_lines.append(line)
                i += 1
        # Skip any blank lines after the signature before the next poem
        while i < n and not lines[i].strip():
            i += 1
        # Save poem with ordered fields
        poem = OrderedDict([
            ('id', poem_id),
            ('title', title),
            ('content', '\n'.join(content_lines).strip()),
            ('signature', signature)
        ])
        poems.append(poem)
        poem_id += 1
    return poems


def save_poems_to_json(poems, output_file):
    """
    Save poems to a JSON file.
    
    Args:
        poems: List of poem dictionaries
        output_file: Path to output JSON file
    """
    with open(output_file, 'w') as file:
        json.dump(poems, file, indent=2, ensure_ascii=False)


def process_all_text_files(texts_dir="texts", output_file="poems.json"):
    """
    Process all .txt files in the texts directory and combine them into one JSON file.
    
    Args:
        texts_dir: Directory containing text files
        output_file: Path to output JSON file
    """
    # Get all .txt files in the texts directory
    text_files = glob.glob(os.path.join(texts_dir, "*.txt"))
    text_files.sort()  # Sort to ensure consistent ordering
    
    if not text_files:
        print(f"No .txt files found in {texts_dir} directory")
        return
    
    print(f"Found {len(text_files)} text files to process:")
    for file in text_files:
        print(f"  - {os.path.basename(file)}")
    
    all_poems = []
    total_poems = 0
    
    for file_path in text_files:
        print(f"\nProcessing {os.path.basename(file_path)}...")
        try:
            poems = parse_poems(file_path)
            # Update IDs to be sequential across all files
            for poem in poems:
                poem['id'] = total_poems + poem['id']
            all_poems.extend(poems)
            total_poems = len(all_poems)
            print(f"  Found {len(poems)} poems (total so far: {total_poems})")
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
    
    print(f"\nTotal poems found: {len(all_poems)}")
    
    # Save to JSON
    save_poems_to_json(all_poems, output_file)
    print(f"Saved all poems to {output_file}")
    
    # Show first poem as example
    if all_poems:
        print("\nFirst poem:")
        print(json.dumps(all_poems[0], indent=2))


def main():
    """Main function to parse poems and save to JSON."""
    # Check if texts directory exists
    if os.path.exists("texts"):
        print("Processing all text files in 'texts' directory...")
        process_all_text_files()
    else:
        # Fallback to single file processing
        input_file = "Occasionally1-100.txt"
        output_file = "poems.json"
        
        if os.path.exists(input_file):
            print("Parsing poems from {}...".format(input_file))
            poems = parse_poems(input_file)
            
            print("Found {} poems".format(len(poems)))
            
            # Save to JSON
            save_poems_to_json(poems, output_file)
            print("Saved poems to {}".format(output_file))
            
            # Show first poem as example
            if poems:
                print("\nFirst poem:")
                print(json.dumps(poems[0], indent=2))
        else:
            print("No input file found. Please ensure 'texts' directory exists or 'Occasionally1-100.txt' is present.")


if __name__ == "__main__":
    main() 