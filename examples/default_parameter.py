from officechunker.converter import Converter


def test_default_parameters():
    print("Test: Default Parameters (No chunker mapping or custom params)")
    try:
        converter = Converter(
            src_folder="./test_dataset_1",
            dst_folder="./test_md_default"
        )
        converter.convert()
        print(" Default Parameters Test Passed: Files converted using default settings.")
    except Exception as e:
        print(f" Default Parameters Test Failed: {e}")



if __name__ == "__main__":
    test_default_parameters()