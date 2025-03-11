import os
import shutil
from typing import List
from abc import ABC, abstractmethod

class BaseFileConnector(ABC):
    """_summary_
    Base Format to Connect any File System to Convertor

    Args:
        ABC (_type_): _description_
    """
    
    @abstractmethod
    def copy_tree(self, src: str, dst: str) -> None:
        pass
    
    @abstractmethod
    def remove_tree(self,path: str) -> None:
        pass
    
    @abstractmethod
    def list_files(self, folder_path: str) -> List[str]:
        pass
    
    @abstractmethod
    def remove_file(self, file_path: str) -> None:
        pass
    
    
    
class LocalFileConnector(BaseFileConnector):
    """_summary_
    Connector for local File system
    
    Args:
        BaseFileConnector (_type_)
    """
    
    def copy_tree(self, src:str, dst: str) -> None:
        shutil.copytree(src,dst)
    
    def remove_tree(self, path: str) -> None:
        shutil.rmtree(path)
        
        
    def list_files(self,folder_path:str) -> List[str]:
        file_list = []
        for root, _, files in os.walk(folder_path):
            for f in files:
                file_list.append(os.path.join(root,f))
        return file_list
    
    def remove_file(self,file_path: str) -> None:
        os.remove(file_path)
        
        