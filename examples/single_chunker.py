from officechunker.converter import Converter

def test_single_chunker():
    print("Test: Single Chunker for All Files")
    try:
        converter = Converter(
            src_folder="./test_dataset_1",
            dst_folder="./test_md_token",
            chunker_config="token"
        )
        converter.convert()
        print(" Single Chunker Test Passed: All files processed with 'token' chunker.")
    except Exception as e:
        print(f" Single Chunker Test Failed: {e}")


if __name__ == "__main__":
    test_single_chunker()