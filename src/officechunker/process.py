from markitdown import MarkItDown


def parse_to_md(file_path: str) -> str:
    """
    Use MarkItDown to conver File to md format

    Args:
        file_path(str): path for individual file
    """

    md = MarkItDown(enable_plugins=False)
    try:
        result = md.convert(file_path)
        return result.markdown

    except ValueError as e:
        raise RuntimeError(f"Error converting file: {file_path}. Reason: {e}")
    except Exception as e:
        raise
