from unstructured.partition.auto import partition
import logfire

def parse_office(file_path:str):
    """
    Loads .docx and .pptx files using the Unstructured library.
    """
    try:
        doc_elements = partition(filename=file_path)
        full_text = [str(el) for el in doc_elements]

        logfire.info(f"Extracted text from {file_path}: Total elements: {len(full_text)}")
        
        final_text = "\n".join(full_text)

        return final_text.strip()
    
    except Exception as e:
        logfire.error(f"Office Load Failed: {e}")
        raise e
     

