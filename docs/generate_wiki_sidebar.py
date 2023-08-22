import os
import sys


def get_markdown_title(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return None


def generate_sidebar(path, level, file_output):
    if level == 1:
        file_output.write("# Table of Contents\n")

    for item in sorted(os.listdir(path)):
        if item == "_Sidebar.md":
            continue
        new_path = os.path.join(path, item)
        if os.path.isdir(new_path):
            separator = "#" * (level + 1)
            file_output.write(f"{separator} {item.capitalize()}\n")
            generate_sidebar(path=new_path, level=level + 1, file_output=file_output)
        elif os.path.isfile(new_path):
            name, ext = os.path.splitext(item)
            if ext == ".md":
                if name != "Home":
                    title = get_markdown_title(new_path) or name
                else:
                    title = name
                file_output.write(f"  - [{title}]({name})\n")


if __name__ == "__main__":
    docs_directory = sys.argv[1]
    sidebar_path = sys.argv[2]

    with open(sidebar_path, "w") as sidebar_file:
        generate_sidebar(docs_directory, level=1, file_output=sidebar_file)
