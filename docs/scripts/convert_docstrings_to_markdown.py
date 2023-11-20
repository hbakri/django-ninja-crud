import logging
import os
import subprocess

import yaml

GLOBAL_CONFIG_PATH = "docs/config/docstring-to-markdown-config.yml"
PYDOC_MARKDOWN_CONFIG_PATH = "docs/config/pydoc-markdown-config.yml"


def load_yaml_file(file_path: str):
    """Load and return the YAML configuration from the given file path."""
    with open(file_path) as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def convert_docstrings_to_markdown(
    input_path: str, output_path: str, markdown_config: dict
):
    """Convert the docstrings in the given input path to Markdown and save to the given output path."""
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Update the output path in the markdown config
        markdown_config["renderer"]["filename"] = output_path

        # Generate the Markdown documentation
        absolute_input_path = os.path.join(os.getcwd(), input_path)
        subprocess.run(
            [
                "poetry",
                "run",
                "pydoc-markdown",
                "-m",
                absolute_input_path,
                yaml.dump(markdown_config),
            ]
        )
    except Exception as e:
        logging.error(f"Error generating documentation for {input_path}: {e}")


def main():
    """Generate Markdown documentation for all modules in the project."""
    global_config = load_yaml_file(GLOBAL_CONFIG_PATH)
    pydoc_markdown_config = load_yaml_file(PYDOC_MARKDOWN_CONFIG_PATH)

    settings = global_config["settings"]
    for module in global_config["modules"]:
        input_path = os.path.join(settings["project_root"], module["input_path"])
        output_path = os.path.join(settings["markdown_root"], module["output_path"])
        convert_docstrings_to_markdown(
            input_path=input_path,
            output_path=output_path,
            markdown_config=pydoc_markdown_config,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
