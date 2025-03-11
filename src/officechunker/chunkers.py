import tiktoken
from typing import Any
from chonkie import (
    TokenChunker,
    WordChunker,
    SentenceChunker,
    RecursiveChunker,
    SemanticChunker,
    SemanticChunker,
    SDPMChunker,
    LateChunker,
)

from chonkie import RecursiveRules

CHONKER_MAP = {
    "token": TokenChunker,
    "word": WordChunker,
    "sentence": SentenceChunker,
    "recursive": RecursiveChunker,
    "semantic": SemanticChunker,
    "sdpm": SDPMChunker,
    "late": LateChunker
}


DEFAULT_PARAMS = {
    "token": {
        "tokenizer": "gpt2",      # tiktoken에서 string identifier 사용
        "chunk_size":1024,
        "chunk_overlap": 30,
        "return_type": "chunks",
    },
    "word": {
        "tokenizer_or_token_counter": "gpt2",
        "chunk_size": 512,
        "chunk_overlap": 30,
        "return_type": "chunks",
    },
    "sentence": {
        "tokenizer_or_token_counter": "gpt2",
        "chunk_size": 512,
        "chunk_overlap": 30,
        "min_sentences_per_chunk": 1,
        "min_characters_per_sentence": 12,
        "approximate": True,
        "delim": [".", "?", "!", "\n"],
        "include_delim": "prev",
        "return_type": "chunks",
    },
    "recursive": {
        "tokenizer_or_token_counter": "gpt2",
        "chunk_size": 512,
        "rules": None,  # None이면 RecursiveRules()로 대체됨
        "min_characters_per_chunk": 12,
        "return_type": "chunks",
    },
    "semantic": {
        "embedding_model": "minishlab/potion-base-8M",
        "mode": "window",
        "threshold": "auto",
        "chunk_size": 512,
        "similarity_window": 1,
        "min_sentences": 1,
        "min_characters_per_sentence": 12,
        "min_chunk_size": 2,
        "threshold_step": 0.01,
        "delim": [".", "!", "?", "\n"],
        "return_type": "chunks",
    },
    "sdpm": {
        "embedding_model": "minishlab/potion-base-8M",
        "threshold": 0.5,
        "chunk_size": 512,
        "min_sentences": 1,
        "skip_window": 1,
    },
    "late": {
        "embedding_model": "all-MiniLM-L6-v2",
        "mode": "sentence",
        "chunk_size": 512,
        "min_sentences_per_chunk": 1,
        "min_characters_per_sentence": 12,
    },
}

def create_chunker(chunker_type : str = "token", **chunker_kwargs: Any):
    """
    Create Chunker Instance based on the chunker_type
    
    Args:
        chunker_type (string)
        **chunker_kwargs: Any
    """ 
    
    
    if chunker_type not in CHONKER_MAP:
        raise ValueError(f"Unsupported chunker_type: {chunker_type}")
    
    params = DEFAULT_PARAMS.get(chunker_type, {}).copy()
    params.update(chunker_kwargs)
    
    # TokenChunker: Conver Tokenizer string to Tiktoken Encoding Instance
    if chunker_type == "token":
        tokenizer_val = params.get("tokenizer", "gpt2")
        if isinstance(tokenizer_val,str) :
            params["tokenizer"] = tiktoken.get_encoding(tokenizer_val)
            
    # RecursiveChunker: if rules is none use RecursiveRules
    if chunker_type == "recursive" and (("rules" not in params) or (params["rules"] is None)):
        params["rules"] = RecursiveRules()

    chunker_class = CHONKER_MAP[chunker_type]
    return chunker_class(**params)