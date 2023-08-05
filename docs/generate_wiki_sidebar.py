import os
import sys


def get_markdown_title(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
    return None


def generate_sidebar(directory, wiki_path, indentation, file_output):
    for item in sorted(os.listdir(directory)):
        if item == "_Sidebar.md":
            continue
        path = os.path.join(directory, item)
        if os.path.isdir(path):
            separator = "-" if indentation else "##"
            file_output.write(f"{indentation}{separator} {item}\n")
            generate_sidebar(
                path, f"{wiki_path}/{item}", indentation + "  ", file_output
            )
        elif os.path.isfile(path):
            name, ext = os.path.splitext(item)
            if ext == ".md":
                title = get_markdown_title(path) or name
                file_output.write(f"{indentation}- [{title}]({name})\n")


if __name__ == "__main__":
    docs_directory = sys.argv[1]
    sidebar_path = sys.argv[2]

    with open(sidebar_path, "w") as sidebar_file:
        generate_sidebar(docs_directory, docs_directory, "", sidebar_file)
