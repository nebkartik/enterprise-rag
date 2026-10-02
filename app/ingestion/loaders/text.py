import logfire


def text_loader(file_path: str):
    """
    Loads plain text files.
    """
    with logfire.span("Text Loading", filename=file_path):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logfire.error(f"Text Load Failed: {e}")
            raise e
                      