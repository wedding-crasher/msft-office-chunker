import os
import asyncio
from typing import Optional, List, Tuple, Union, Dict, Any
from tqdm import tqdm
from officechunker.file_handlers import BaseFileConnector, LocalFileConnector
from officechunker.chunkers import create_chunker, DEFAULT_PARAMS
from officechunker.process import parse_to_md


DEFAULT_EXTENSION_CHUNKER_MAP = {
    ".pdf": "token",
    ".docx": "sentence",
    ".xlsx": "word",
    ".pptx": "late"

}
class Converter:
    def __init__(
        self,
        src_folder: str,
        dst_folder: Optional[str] = None,
        # chunker_config: Either a single string or a dict mapping file extensions to configurations.
        # Each value can be a string or a dict in the form {"type": <chunker_type>, "params": <additional parameters dict>}
        chunker_config: Optional[Union[str, Dict[str, Union[str, Dict[str, Any]]]]] = None,
        delete_md_files: bool = True,
        file_handler: Optional['BaseFileConnector'] = None,
    ):
        """
        Initializes the Converter.

        Parameters:
        - src_folder: The source folder containing the original files.
        - dst_folder: The destination folder for converted files (default: '<src_folder>_md' in the current directory).
        - chunker_config: Either a single string to apply the same chunker to all files or a dict mapping file extensions to configurations.
                          Example: "token"
                          or
                          {
                              ".pdf": "token",
                              ".docx": {"type": "sentence", "params": {"chunk_overlap": 20}},
                              ...
                          }
                          If not provided, the default DEFAULT_EXTENSION_CHUNKER_MAP is used.
        - delete_md_files: Whether to delete temporary .md files after conversion.
        - file_handler: The file handler to use (default: LocalFileConnector).
        """
        self.src_folder = src_folder
        self.dst_folder = (
            dst_folder
            if dst_folder is not None
            else os.path.join(os.getcwd(), os.path.basename(src_folder) + "_md")
        )
        self.delete_md_files = delete_md_files
        self.file_handler = file_handler if file_handler is not None else LocalFileConnector()
        
        # Validate and initialize chunker_config
        if chunker_config is None:
            self.chunker_config = DEFAULT_EXTENSION_CHUNKER_MAP
        elif isinstance(chunker_config, str):
            self.chunker_config = chunker_config
        elif isinstance(chunker_config, dict):
            for ext, conf in chunker_config.items():
                if not isinstance(ext, str):
                    raise ValueError(f"Extension key must be a string, got {type(ext)} for key {ext}")
                if isinstance(conf, str):
                    continue
                elif isinstance(conf, dict):
                    if "type" not in conf:
                        raise ValueError(f"Configuration for extension '{ext}' must include a 'type' key.")
                    if not isinstance(conf["type"], str):
                        raise ValueError(f"'type' for extension '{ext}' must be a string.")
                    if "params" in conf and not isinstance(conf["params"], dict):
                        raise ValueError(f"'params' for extension '{ext}' must be a dictionary if provided.")
                else:
                    raise ValueError(f"Configuration for extension '{ext}' must be either a string or a dict.")
            self.chunker_config = chunker_config
        else:
            raise ValueError("chunker_config must be either None, a string, or a dict mapping extensions to configurations.")

    def _validate_chunker_params(self, chunker_type: str, user_params: Dict[str, Any]) -> None:
        """
        Validates user-provided parameters against the default parameters for the given chunker type.
        """
        default_params = DEFAULT_PARAMS.get(chunker_type, {})
        for key, value in user_params.items():
            if key in default_params:
                # If the default is None, skip type checking.
                if default_params[key] is None:
                    continue
                if not isinstance(value, type(default_params[key])):
                    raise ValueError(
                        f"Parameter '{key}' for chunker '{chunker_type}' should be of type "
                        f"{type(default_params[key]).__name__}, got {type(value).__name__}"
                    )

    def _get_chunker_config(self, ext: str) -> Tuple[str, Dict[str, Any]]:
        """
        Retrieves the chunker type and parameters based on the file extension.
        """
        if isinstance(self.chunker_config, str):
            return self.chunker_config, {}
        elif isinstance(self.chunker_config, dict):
            conf = self.chunker_config.get(ext, "token")  # Default to "token"
            if isinstance(conf, str):
                return conf, {}
            elif isinstance(conf, dict):
                return conf["type"], conf.get("params", {})
        return "token", {}

    def _remove_file(self, file_path: str) -> None:
        """
        Removes the specified file if it exists.
        """
        if os.path.exists(file_path):
            os.remove(file_path)

    async def _write_chunks(self, base_name: str, chunks: List[str], directory: str) -> None:
        """
        Writes each chunk to a separate markdown file.
        """
        loop = asyncio.get_running_loop()
        for i, chunk_text in enumerate(chunks):
            chunk_file_path = os.path.join(directory, f"{base_name}_{i+1}.md")
            def write_chunk():
                with open(chunk_file_path, "w", encoding="utf-8") as f:
                    f.write(chunk_text)
            await loop.run_in_executor(None, write_chunk)

    async def _convert_single_file(self, file_path: str) -> Tuple[str, Optional[str]]:
        """
        Converts a single file to markdown and performs chunking.
        Returns a tuple (file_path, None) on success or (file_path, error_message) on error.
        """
        try:
            loop = asyncio.get_running_loop()
            
            # Step 1: Convert file to markdown
            result = await loop.run_in_executor(None, parse_to_md, file_path)
            
            # Step 2: Write markdown content to file
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            md_file_path = os.path.join(os.path.dirname(file_path), f"{base_name}.md")
            def write_md():
                with open(md_file_path, "w", encoding="utf-8") as f:
                    f.write(result)
            await loop.run_in_executor(None, write_md)
            
            # Step 3: Determine chunker settings based on file extension
            ext = os.path.splitext(file_path)[1].lower()
            chosen_type, chosen_params = self._get_chunker_config(ext)
            
            # Step 4: Validate chunker parameters
            self._validate_chunker_params(chosen_type, chosen_params)
            
            # Step 5: Create the chunker instance
            chunker_instance = create_chunker(chosen_type, **chosen_params)
            
            # Step 6: Read markdown file and perform chunking
            def read_md_and_chunk():
                with open(md_file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
                chunks = chunker_instance(text_content)
                return [chunk.text for chunk in chunks]
            chunks = await loop.run_in_executor(None, read_md_and_chunk)
            
            # Step 7: Write chunks to individual files
            await self._write_chunks(base_name, chunks, os.path.dirname(file_path))
            
            # Step 8: Remove the original file and, if specified, the temporary markdown file
            await loop.run_in_executor(None, self._remove_file, file_path)
            if self.delete_md_files:
                await loop.run_in_executor(None, self._remove_file, md_file_path)
                
            return (file_path, None)
        except Exception as e:
            return (file_path, str(e))

    async def _convert_folder_async(self) -> List[Tuple[str, str]]:
        """
        Converts all files in the destination folder to markdown and performs chunking.
        Returns a list of error logs.
        """
        # Prepare the destination folder by removing it if it exists and then copying the source folder.
        if os.path.exists(self.dst_folder):
            self.file_handler.remove_tree(self.dst_folder)
        self.file_handler.copy_tree(self.src_folder, self.dst_folder)
        
        # Get all file paths from the destination folder.
        all_files = self.file_handler.list_files(self.dst_folder)
        tasks = [self._convert_single_file(fp) for fp in all_files]
        error_logs: List[Tuple[str, str]] = []
        
        results = []
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Converting files"):
            result = await coro
            results.append(result)
            
        for file_path, err in results:
            if err is not None:
                error_logs.append((file_path, err))
        return error_logs

    def convert(self) -> None:
        """
        Converts all files in the folder to markdown and performs chunking.
        """
        if self.dst_folder in [".", "..", "/"]:
            raise ValueError("Invalid destination folder.")
        print("Checking environment and preparing for conversion...")
        
        async def run():
            return await self._convert_folder_async()
        
        error_log = asyncio.run(run())
        
        if error_log:
            print("Errors encountered during conversion:")
            for fp, err in error_log:
                print(f"[Error] File: {fp}, Reason: {err}")
        else:
            print("All files converted successfully!")