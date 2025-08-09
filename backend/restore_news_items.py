#!/usr/bin/env python3

import json
import re

def extract_and_clean_news_items(poems_file):
    """
    Extract news items from poem content, remove prefixes, and create new newsItem property.
    """
    
    with open(poems_file, 'r', encoding='utf-8') as f:
        poems = json.load(f)
    
    processed_count = 0
    
    for poem in poems:
        content = poem.get('content', '')
        
        # Check if content starts with "News item:"
        if content.startswith('News item:'):
            # Find the first occurrence of double newline after "News item:"
            match = re.match(r'(News item:.*?)\n\n(.*)', content, re.DOTALL)
            
            if match:
                news_item_raw = match.group(1)
                poem_content = match.group(2)
                
                # Remove the "News item: " prefix (11 characters)
                news_item_clean = news_item_raw[11:] if news_item_raw.startswith('News item: ') else news_item_raw
                
                # Add newsItem property and update content
                poem['newsItem'] = news_item_clean
                poem['content'] = poem_content
                
                processed_count += 1
            else:
                # Fallback: if pattern doesn't match exactly, leave as is
                print(f"Warning: Poem {poem.get('id')} has 'News item:' but doesn't match expected pattern")
                poem['newsItem'] = None
        else:
            # No news item, add null newsItem property for consistency
            poem['newsItem'] = None
    
    return poems, processed_count

def main():
    input_file = 'poems.json'
    
    print("Re-extracting and cleaning news items from poems...")
    poems, count = extract_and_clean_news_items(input_file)
    
    # Save updated poems
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(poems, f, indent=2, ensure_ascii=False)
    
    print(f"Processing complete!")
    print(f"- Processed {count} poems with news items")
    print(f"- Total poems: {len(poems)}")

if __name__ == '__main__':
    main()