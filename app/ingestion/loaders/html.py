from bs4 import BeautifulSoup
import logfire

def load_html(file_path:str):
    """
    Loads and parses HTML files.
    """
    try:
        with open(file_path, 'r',encoding='utf-8', errors='ignore') as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")

        if soup in ["script", "style", "meta", "noscript"]:
            soup.decompose()

        text = soup.get_text(separator="\n")
        logfire.info(f"Extracted text from {file_path}: {text[:100]}...")

        
        lines = (line.strip() for line in text.splitlines())

        #check if code needs modification
        chunks = (chunk.strip() for line in lines for chunk in line.split())
        final_text = "\n".join(chunk for chunk in chunks if chunk)
    except Exception as e:
        logfire.error(f"HTML Load Failed: {e}")
        raise e

    return final_text
