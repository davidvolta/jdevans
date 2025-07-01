import json
import os

def create_poem_titles_lookup():
    """Create a stripped-down version of poems.json with just title and ID"""
    
    input_file = "backend/poems.json"
    output_file = "poem_titles_lookup.json"
    
    print(f"Reading {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            poems = json.load(f)
        
        print(f"Found {len(poems)} poems")
        
        # Extract just title and ID
        titles_lookup = []
        for poem in poems:
            # Assuming the structure has 'id' and 'title' fields
            # Adjust these field names if they're different
            if 'id' in poem and 'title' in poem:
                titles_lookup.append({
                    'id': poem['id'],
                    'title': poem['title']
                })
            else:
                print(f"Warning: Poem missing id or title: {poem.keys()}")
        
        print(f"Extracted {len(titles_lookup)} poems with titles and IDs")
        
        # Save the stripped-down version
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(titles_lookup, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {output_file}")
        
        # Show a few examples
        print("\nFirst few entries:")
        for i, entry in enumerate(titles_lookup[:5]):
            print(f"{i+1}. ID: {entry['id']}, Title: {entry['title']}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please check if the field names are 'id' and 'title' in your JSON file")

if __name__ == "__main__":
    create_poem_titles_lookup() 