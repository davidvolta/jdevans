#!/usr/bin/env python3
"""
Poem Parser
Converts a text file of poems to JSON format.
Each poem has a title, content, signature, and ID.
"""

import json
import re
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
    with open(file_path, 'r') as file:
        lines = file.readlines()

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


def main():
    """Main function to parse poems and save to JSON."""
    input_file = "Occasionally1-100.txt"
    output_file = "poems.json"
    
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


if __name__ == "__main__":
    main() 