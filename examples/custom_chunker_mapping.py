from officechunker.converter import Converter

def test_custom_chunker_mapping():
    print("Test: Custom Chunker Mapping (Different chunkers per extension)")
    custom_mapping = {
        ".pdf": "token",
        ".docx": "word",
        ".xlsx": "sentence",
        ".pptx": "late",
    }
    try:
        converter = Converter(
            src_folder="./test_dataset_1",
            dst_folder="./test_md_custom_mapping",
            chunker_config=custom_mapping
        )
        converter.convert()
        print("Custom Mapping Test Passed: Files converted with custom chunker mapping.")
    except Exception as e:
        print(f" Custom Mapping Test Failed: {e}")
        
if __name__ == "__main__":
    test_custom_chunker_mapping()