from docx import Document
import os
import re
import glob
import json
from difflib import SequenceMatcher

def slugify(text):
    """Convert text to a safe filename by replacing non-alphanumeric chars with underscores"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text.strip())[:50] or "untitled"

def load_poem_titles():
    """Load the poem titles lookup file"""
    try:
        with open("poem_titles_lookup.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: poem_titles_lookup.json not found. Will use slugified names.")
        return []

def find_best_poem_match(image_title, poems):
    """Find the best matching poem title and return its ID"""
    if not poems:
        return None
    
    best_match = None
    best_ratio = 0.0
    
    # Normalize the image title for comparison
    image_title_normalized = image_title.lower().strip()
    
    for poem in poems:
        poem_title_normalized = poem['title'].lower().strip()
        
        # Use sequence matcher for fuzzy matching
        ratio = SequenceMatcher(None, image_title_normalized, poem_title_normalized).ratio()
        
        if ratio > best_ratio and ratio > 0.8:  # Threshold for good match
            best_ratio = ratio
            best_match = poem
    
    return best_match

def extract_images_from_docx_with_text_above(docx_path, output_folder, poems_lookup):
    """Extract images from a Word document, using the preceding paragraph as the title"""
    print(f"Processing: {os.path.basename(docx_path)}")
    
    doc = Document(docx_path)
    rels = doc.part._rels
    last_text = "untitled"
    image_counter = 1
    extracted_images = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Iterate through paragraphs to find text and images
    for paragraph in doc.paragraphs:
        # Get text from paragraph
        text = paragraph.text.strip()
        if text:
            last_text = text
        
        # Check if this paragraph contains images
        for run in paragraph.runs:
            # Look for images in the run
            for element in run._element.iter():
                if element.tag.endswith('}drawing'):
                    # Find blip elements (images)
                    for blip in element.iter():
                        if blip.tag.endswith('}blip'):
                            embed = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                            if embed and embed in doc.part._rels:
                                image_part = doc.part._rels[embed].target_part
                                image_data = image_part.blob
                                
                                # Get file extension from content type
                                content_type = image_part.content_type
                                if 'jpeg' in content_type or 'jpg' in content_type:
                                    ext = 'jpg'
                                elif 'png' in content_type:
                                    ext = 'png'
                                elif 'gif' in content_type:
                                    ext = 'gif'
                                else:
                                    ext = 'png'  # default
                                
                                # Try to find a matching poem
                                poem_match = find_best_poem_match(last_text, poems_lookup)
                                
                                if poem_match:
                                    filename = f"{poem_match['id']}.{ext}"
                                    print(f"  Extracted: {filename} (matched to poem ID {poem_match['id']}: '{poem_match['title']}')")
                                else:
                                    filename = f"{slugify(last_text)}_{image_counter}.{ext}"
                                    print(f"  Extracted: {filename} (no match found, using slug)")
                                
                                filepath = os.path.join(output_folder, filename)
                                
                                with open(filepath, "wb") as f:
                                    f.write(image_data)
                                
                                extracted_images.append({
                                    'filename': filename,
                                    'title': last_text,
                                    'filepath': filepath,
                                    'poem_id': poem_match['id'] if poem_match else None,
                                    'poem_title': poem_match['title'] if poem_match else None
                                })
                                image_counter += 1
    
    return extracted_images

def process_all_documents():
    """Process all Word documents in the word/ folder"""
    word_folder = "word"
    output_folder = "extracted_images"
    
    # Load poem titles lookup
    poems_lookup = load_poem_titles()
    print(f"Loaded {len(poems_lookup)} poem titles for matching")
    
    # Get all .docx files (excluding .zip files)
    docx_files = glob.glob(os.path.join(word_folder, "*.docx"))
    
    if not docx_files:
        print("No .docx files found in the word/ folder")
        return
    
    print(f"Found {len(docx_files)} Word documents to process")
    print("=" * 50)
    
    all_extracted = []
    
    for docx_file in sorted(docx_files):
        try:
            extracted = extract_images_from_docx_with_text_above(docx_file, output_folder, poems_lookup)
            all_extracted.extend(extracted)
            print(f"  Total images from this file: {len(extracted)}")
            print()
        except Exception as e:
            print(f"Error processing {docx_file}: {e}")
            print()
    
    print("=" * 50)
    print(f"Extraction complete! Total images extracted: {len(all_extracted)}")
    print(f"Images saved to: {output_folder}/")
    
    # Save a summary of extracted images
    summary_file = os.path.join(output_folder, "extraction_summary.txt")
    with open(summary_file, "w") as f:
        f.write("Extracted Images Summary\n")
        f.write("=" * 30 + "\n\n")
        for i, img in enumerate(all_extracted, 1):
            f.write(f"{i}. {img['filename']}\n")
            f.write(f"   Title: {img['title']}\n")
            f.write(f"   Path: {img['filepath']}\n\n")
    
    print(f"Summary saved to: {summary_file}")

def test_single_file():
    """Test the extraction on a single file"""
    word_folder = "word"
    output_folder = "extracted_images_test"
    
    # Load poem titles lookup
    poems_lookup = load_poem_titles()
    print(f"Loaded {len(poems_lookup)} poem titles for matching")
    
    # Get the first .docx file for testing
    docx_files = glob.glob(os.path.join(word_folder, "*.docx"))
    
    if not docx_files:
        print("No .docx files found in the word/ folder")
        return
    
    test_file = sorted(docx_files)[0]  # Use the first file
    print(f"Testing with: {os.path.basename(test_file)}")
    print("=" * 50)
    
    try:
        extracted = extract_images_from_docx_with_text_above(test_file, output_folder, poems_lookup)
        print(f"Test complete! Extracted {len(extracted)} images")
        print(f"Images saved to: {output_folder}/")
        
        # Show what was extracted
        for i, img in enumerate(extracted, 1):
            if img['poem_id']:
                print(f"{i}. {img['filename']} (matched to poem {img['poem_id']}: '{img['poem_title']}')")
            else:
                print(f"{i}. {img['filename']} (no match found for: '{img['title']}')")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    process_all_documents() 