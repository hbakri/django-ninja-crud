import os
import subprocess

import yaml

project_name = "ninja_crud"
modules = [
    "views.abstract",
    "views.retrieve",
    "views.update",
    "views.partial_update",
    "views.delete",
]

template_path = "docs/pydoc-markdown.yml"
with open(template_path, "r") as file:
    template = yaml.load(file, Loader=yaml.FullLoader)

root_dir = os.path.abspath(os.path.join(os.getcwd()))

for module in modules:
    output_path = f"docs/reference/{module.replace('.', '/')}.md"
    template["renderer"]["filename"] = output_path

    # Create necessary directories if they don't exist
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    module_path = os.path.join(root_dir, f"{project_name}/{module.replace('.', '/')}")
    yaml_config_str = yaml.dump(template)
    subprocess.run(
        ["poetry", "run", "pydoc-markdown", "-m", module_path, yaml_config_str]
    )
