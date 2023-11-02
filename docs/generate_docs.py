import os
import subprocess

import yaml

root_dir = os.path.abspath(os.path.join(os.getcwd()))
project_name = "ninja_crud"
modules = [
    ("views/abstract", "AbstractModelView"),
    ("views/retrieve", "RetrieveModelView"),
    ("views/update", "UpdateModelView"),
    ("views/delete", "DeleteModelView"),
    ("views/list", "ListModelView"),
    ("views/create", "CreateModelView"),
    ("views/types", "Types"),
    ("views/viewset", "ModelViewSet"),
]

template_path = "docs/pydoc-markdown.yml"
with open(template_path, "r") as file:
    template = yaml.load(file, Loader=yaml.FullLoader)

for module_path, module_title in modules:
    reference_dir = "docs/reference"
    module_dir = "/".join(module_path.split("/")[:-1])
    output_path = os.path.join(reference_dir, module_dir, f"{module_title}.md")
    template["renderer"]["filename"] = output_path
    yaml_config_str = yaml.dump(template)

    # Create necessary directories if they don't exist
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    module_absolute_path = os.path.join(root_dir, project_name, module_path)
    subprocess.run(
        ["poetry", "run", "pydoc-markdown", "-m", module_absolute_path, yaml_config_str]
    )
