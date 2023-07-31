import subprocess

import yaml

project_name = "ninja_crud"
modules = [
    "views.abstract",
    "views.list",
    "views.create",
    "views.retrieve",
    "views.update",
    "views.patch",
    "views.delete",
    "views.viewset",
]

template_path = "docs/pydoc-markdown.yml"
with open(template_path, "r") as file:
    template = yaml.load(file, Loader=yaml.FullLoader)

for module in modules:
    template["renderer"]["filename"] = f"docs/reference/{module.replace('.', '/')}.md"

    yaml_config_str = yaml.dump(template)
    subprocess.run(
        ["pydoc-markdown", "-m", f"{project_name}.{module}", yaml_config_str]
    )
