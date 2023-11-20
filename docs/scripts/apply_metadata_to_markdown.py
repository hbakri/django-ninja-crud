import logging

import frontmatter
import yaml

READMEIO_CONFIG_PATH = "docs/config/readmeio-config.yml"


def load_yaml_file(file_path: str):
    """Load and return the YAML configuration from the given file path."""
    with open(file_path) as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)


def apply_metadata_to_markdown(markdown_file_path: str, metadata: dict):
    """Apply metadata from readmeio-config to the markdown files."""
    try:
        # Read the existing Markdown file
        post = frontmatter.load(markdown_file_path)

        # Update the frontmatter with the metadata
        post.metadata = metadata

        # Write the updated Markdown file
        frontmatter.dump(post, markdown_file_path)
    except FileNotFoundError:
        logging.error(f"Markdown file not found: {markdown_file_path}")
    except Exception as e:
        logging.error(f"Error applying metadata to {markdown_file_path}: {e}")
        raise e


def main():
    """Apply metadata to the Markdown files."""
    readmeio_config = load_yaml_file(READMEIO_CONFIG_PATH)

    for doc in readmeio_config["docs"]:
        markdown_file_path = doc.pop("path")
        apply_metadata_to_markdown(markdown_file_path=markdown_file_path, metadata=doc)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
