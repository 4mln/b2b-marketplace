import os
import re

PLUGIN_DIR = "./plugins"  # adjust if needed

# Regex for Depends(get_session) or get_db_sync
DEPEND_PATTERN = re.compile(r"Depends\(\s*(get_session|get_db_sync)\s*\)")

# Correct replacement
REPLACEMENTS = {
    "get_session": 'Depends(lambda: __import__("importlib").import_module("app.db.session").get_session)',
    "get_db_sync": 'Depends(lambda: __import__("importlib").import_module("app.db.session").get_db_sync)',
}

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    def repl(match):
        func = match.group(1)
        return REPLACEMENTS[func]

    new_content, count = DEPEND_PATTERN.subn(repl, content)

    if count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[Fixed] {file_path} | Replacements: {count}")

def walk_plugins():
    for root, dirs, files in os.walk(PLUGIN_DIR):
        for file in files:
            if file.endswith(".py"):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    walk_plugins()
    print("✅ All plugins checked and fixed for lazy get_session / get_db_sync usage.")
