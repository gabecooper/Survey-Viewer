
import json
import re

def fix_comments():
    # 1. Read the old comments from part1.txt
    # part1.txt was created in step 87 with the content of the original array.
    # It likely looks like:
    # const commentsData = [ ... ];
    # OR just [ ... ]
    # Let's inspect it first or just try to parse it. 
    # Based on step 87, it ends with a trailing comma inside the list? No, it looks like it was truncated in the prompt or I wrote a specific block.
    # Let's read it and see.
    with open('part1.txt', 'r') as f:
        part1_content = f.read()

    # 2. Read the new comments from comments_data.js
    with open('comments_data.js', 'r') as f:
        new_data_content = f.read()

    # 3. Read the html shell
    with open('comments_viewer.html', 'r') as f:
        html_content = f.read()

    # Parsers
    def parse_js_array(text):
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                # We need to keys to be quoted for json.loads. 
                # The snippets showed quoted keys.
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                # If simple load fails (maybe trailing commas?), simple fix?
                return None
        return None

    # Try to clean up part1.txt content if it's not pure JSON
    # In Step 87, it looked like it had "const commentsData = [" at the start potentially?
    # Actually, looking at Step 87, I wrote: 
    # const commentsData = [ ...
    # And it cut off. 
    # Wait, Step 87 input shows the `CodeContent` I SENT. I wrote a file validly. 
    # BUT, did I write the *whole* file? The prompt in step 87 says "Restore part 1 of comments data".
    # I might have only written a partial file if I copy-pasted from a truncated view?
    # Let's use `part1.txt` but if it's broken, I might need to rely on the fact that I previously saw the file in step 114?
    # No, step 114 showed the *new* file.
    # Step 87 wrote `part1.txt`.
    
    # Let's assume part1.txt contains the "Beth Emeth" and "JBO" comments. 
    # Let's assume comments_data.js contains "Camp Galil", etc.
    
    # Only way to be sure is to load them.
    
    old_comments_list = []
    # Attempt to parse part1.txt
    try:
        # It might contain "const commentsData = [...]"
        json_str = part1_content
        if "const commentsData =" in json_str:
            json_str = json_str.split("const commentsData =")[1].strip()
        if json_str.endswith(";"):
            json_str = json_str[:-1]
        
        old_comments_list = json.loads(json_str)
        print(f"Loaded {len(old_comments_list)} old comments from part1.txt")
    except Exception as e:
        print(f"Failed to load part1.txt: {e}")
        # Fallback: maybe part1.txt was just the content?
        # Let me just try to find the array in it.
        match = re.search(r'\[(.*)\]', part1_content, re.DOTALL)
        if match:
            try:
                old_comments_list = json.loads("[" + match.group(1) + "]")
                print(f"Loaded {len(old_comments_list)} old comments via regex from part1.txt")
            except:
                pass

    # Read new comments
    new_comments_list = []
    try:
        json_str = new_data_content
        if "const commentsData =" in json_str:
            json_str = json_str.split("const commentsData =")[1].strip()
        if json_str.endswith(";"):
            json_str = json_str[:-1]
        new_comments_list = json.loads(json_str)
        print(f"Loaded {len(new_comments_list)} new comments from comments_data.js")
    except Exception as e:
        print(f"Failed to load comments_data.js: {e}")

    # Combine
    # Note: older tool usage cleaned Org_ names. We should do that for new_comments_list too.
    for c in new_comments_list:
        if c.get("organization", "").startswith("Org_"):
            c["organization"] = c["organization"].replace("Org_", "")

    combined = old_comments_list + new_comments_list
    print(f"Total combined comments: {len(combined)}")

    # Construct JS
    combined_json = json.dumps(combined, indent=2)
    new_js_block = f"    // Combined comments data\n    const commentsData = {combined_json};\n"

    # Replace in HTML
    # We look for "const commentsData = [ ... ];" inside the HTML and replace it.
    
    pattern = r'const commentsData = \[.*?\];'
    # We use DOTALL to match across lines
    
    # Check if we can find it
    if re.search(pattern, html_content, re.DOTALL):
        new_html = re.sub(pattern, new_js_block, html_content, flags=re.DOTALL, count=1)
        with open('comments_viewer.html', 'w') as f:
            f.write(new_html)
        print("Updated comments_viewer.html")
    else:
        print("Could not find commentsData block in HTML to replace.")
        # Fallback: maybe just look for script tag start?
        # But there is other script stuff. 
        # Let's dump the first 100 chars of script tag to debug if needed.
        pass

if __name__ == "__main__":
    fix_comments()
