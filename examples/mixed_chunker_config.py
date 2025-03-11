from officechunker.converter import Converter

def test_mixed_chunker_config():
    print("Test: Mixed Custom and Default Chunker Config")
    custom_mapping = {
        ".docx": {"type": "sentence", "params": {"chunk_overlap": 100}},
        ".pptx": {"type": "late", "params": {"chunk_size": 512}}
    }
    try:
        converter = Converter(
            src_folder="./test_dataset_1",
            dst_folder="./test_md_mixed",
            chunker_config=custom_mapping
        )
        converter.convert()
        print(" Mixed Config Test Passed: Default and custom settings applied correctly.")
    except Exception as e:
        print(f" Mixed Config Test Failed: {e}")

if __name__ == "__main__":
    test_mixed_chunker_config()