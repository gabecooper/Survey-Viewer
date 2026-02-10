
import json
import re

def fix_comments():
    # 1. Read the old comments from part1.json
    try:
        with open('part1.json', 'r') as f:
            old_data = json.load(f)
            # Normalize old data if needed
            for c in old_data:
                 if c.get("organization", "").startswith("Org_"):
                     c["organization"] = c["organization"][4:]
            print(f"Loaded {len(old_data)} old comments")
    except Exception as e:
        print(f"Error loading part1.json: {e}")
        return

    # 2. Extract current comments from HTML
    with open('comments_viewer.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    current_comments = []
    # Regex to find the JSON array inside commentsData
    # Pattern: const commentsData = [ ... ];
    match = re.search(r'const commentsData = (\[.*?\]);', html_content, re.DOTALL)
    if match:
        try:
            current_comments = json.loads(match.group(1))
            # Normalize current data
            for c in current_comments:
                 if c.get("organization", "").startswith("Org_"):
                     c["organization"] = c["organization"][4:]
            print(f"Loaded {len(current_comments)} comments currently in HTML")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error on HTML content: {e}")
            # If decode error, maybe try to be lenient or manual extraction?
            # Or just proceed with empty list if it fails severely.
            pass
    else:
        print("Could not locate existing commentsData in HTML")

    # 3. Merge and Dedup
    # Use a dictionary keyed by distinct content to dedup
    # Key: (organization, row, comment_text)
    merged_map = {}
    
    # Add old first
    for c in old_data:
        key = (c.get("organization"), c.get("row"), c.get("comment"))
        merged_map[key] = c
        
    # Add new (overwriting old if identical key, or appending if new)
    # Actually, we want to KEEP old if it exists, and append new.
    # But current_comments represents "new ones" according to user.
    for c in current_comments:
        key = (c.get("organization"), c.get("row"), c.get("comment"))
        merged_map[key] = c
        
    final_list = list(merged_map.values())
    
    # Sort for consistency? Maybe by Org then Row.
    final_list.sort(key=lambda x: (x.get("organization", ""), x.get("row", 0)))
    
    print(f"Total unique comments after merge: {len(final_list)}")

    # 4. Construct JS block
    # json.dumps ensures proper escaping of characters like \u2019
    combined_json = json.dumps(final_list, indent=2)
    new_js_block = f"    // Combined comments data\n    const commentsData = {combined_json};"

    # 5. Replace in HTML using string slicing (safer than re.sub for content with backslashes)
    if match:
        start_idx = match.start()
        end_idx = match.end()
        
        new_html = html_content[:start_idx] + new_js_block + html_content[end_idx:]
        
        with open('comments_viewer.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        print("Successfully updated comments_viewer.html")
    else:
        print("Skipping update: could not find insertion point.")

if __name__ == "__main__":
    fix_comments()
