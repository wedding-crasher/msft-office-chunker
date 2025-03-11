import sys
import os
import json
import argparse

from officechunker.converter import Converter

import sys
import os
import json
import argparse

from officechunker.converter import Converter

def main():
    parser = argparse.ArgumentParser(
        description="CLI for converting files using the OfficeChunker Converter."
    )
    parser.add_argument(
        "src_folder",
        type=str,
        help="Path to the source folder containing the files to be converted."
    )
    parser.add_argument(
        "--dst_folder",
        type=str,
        default=None,
        help="Path to the destination folder where the converted files will be saved (default: '<src_folder>_md' in the current directory)."
    )
    parser.add_argument(
        "--chunker_config",
        type=str,
        default=None,
        help=(
            "Chunker configuration. Either a single string (e.g., 'token') or a JSON-formatted dictionary mapping file extensions to chunker settings.\n"
            "Example: '{\".pdf\": {\"type\": \"token\", \"params\": {\"chunk_size\": 512}}}'. For exact format, please refer to the github."
        )
    )
    parser.add_argument(
        "--delete_md_files",
        action="store_true",
        help="Use this option to delete temporary markdown (.md) files after conversion."
    )
    
    args = parser.parse_args()

    # Handle chunker_config parameter: parse JSON string if provided, otherwise use as a plain string
    chunker_config = None
    if args.chunker_config:
        try:
            chunker_config = json.loads(args.chunker_config)
        except json.JSONDecodeError:
            chunker_config = args.chunker_config

    converter = Converter(
        src_folder=args.src_folder,
        dst_folder=args.dst_folder,
        chunker_config=chunker_config,
        delete_md_files=args.delete_md_files
    )

    converter.convert()

if __name__ == "__main__":
    main()
