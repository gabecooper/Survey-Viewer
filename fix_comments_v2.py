
import json
import re

def fix_comments():
    # 1. Read the old comments from part1.json
    try:
        with open('part1.json', 'r') as f:
            content = f.read()
            # If there's an issue with loading, make sure it's valid JSON
            old_comments_list = json.loads(content)
            print(f"Loaded {len(old_comments_list)} old comments from part1.json")
    except Exception as e:
        print(f"Error loading part1.json: {e}")
        return

    # 2. Read the new comments from comments_data.js
    # Important: The comments_data.js file might have duplicate data or it might just be the new ones.
    # In step 78 (not visible), I assume I created it with new data.
    # In step 172, the user diff showed the file comments_viewer.html having "Camp Galil" etc.
    # Let's read comments_data.js if it exists.
    # If not, I can extract from the current comments_viewer.html content itself?
    # Yes, let's extract what is CURRENTLY in comments_viewer.html because that's what the user sees (and says is "new ones")
    
    with open('comments_viewer.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    current_comments = []
    match = re.search(r'const commentsData = (\[.*?\]);', html_content, re.DOTALL)
    if match:
        try:
            current_comments = json.loads(match.group(1))
            print(f"Loaded {len(current_comments)} comments currently in HTML (new ones)")
        except:
            print("Failed to parse current HTML comments")
            # If JSON parsing fails (maybe because of single quotes or keys without quotes in HTML sometimes),
            # we might need a more robust parser or just rely on the assumption that I wrote valid JSON before.
            pass
            
    # Combine
    # We want to avoid duplicates if I've been running this in circles.
    # A simple way to dedup is by (organization, row, comment) tuple.
    
    seen = set()
    final_list = []
    
    # helper
    def add(comment_list):
        for c in comment_list:
            # Normalize org name (remove Org_ prefix if present)
            org = c.get("organization", "")
            if org.startswith("Org_"):
                org = org[4:]
            c["organization"] = org
            
            # create signature
            sig = (c.get("organization"), c.get("row"), c.get("comment"))
            if sig not in seen:
                seen.add(sig)
                final_list.append(c)

    # Add old first (so they appear first or whatever order)
    # The user said "Include the comments data from the old ones".
    add(old_comments_list)
    add(current_comments)
    
    print(f"Total unique comments: {len(final_list)}")

    # Construct JS
    combined_json = json.dumps(final_list, indent=2)
    # We need to make sure we don't break the regex replacement.
    # formatting the string to replace the existing block.
    new_js_block = f"    // Combined comments data\n    const commentsData = {combined_json};\n"

    # Replace in HTML
    pattern = r'const commentsData = \[.*?\];'
    
    if re.search(pattern, html_content, re.DOTALL):
        new_html = re.sub(pattern, new_js_block, html_content, flags=re.DOTALL, count=1)
        with open('comments_viewer.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        print("Updated comments_viewer.html with merged data")
    else:
        print("Could not find commentsData block in HTML to replace.")

if __name__ == "__main__":
    fix_comments()
