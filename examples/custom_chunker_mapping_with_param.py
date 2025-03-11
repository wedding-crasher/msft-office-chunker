from officechunker.converter import Converter


def test_custom_chunker_mapping_with_params():
    print("Test: Custom Chunker Mapping with Parameters")
    custom_mapping = {
        ".pdf": {"type": "token", "params": {"chunk_size": 512}},
        ".docx": {"type": "sentence", "params": {"chunk_overlap": 20}},
        ".xlsx": {"type": "word", "params": {"chunk_size": 256}},
        ".pptx": "late"
    }
    try:
        converter = Converter(
            src_folder="./test_dataset_1",
            dst_folder="./test_md_custom_mapping_params",
            chunker_config=custom_mapping
        )
        converter.convert()
        print(" Custom Mapping & Parameters Test Passed: Files converted with custom settings.")
    except Exception as e:
        print(f" Custom Mapping & Parameters Test Failed: {e}")
        
if __name__ == "__main__":
    test_custom_chunker_mapping_with_params()