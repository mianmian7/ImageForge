"""
Data models for processing
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class ProcessType(Enum):
    """Processing type enumeration"""
    RESIZE = "resize"
    COMPRESS = "compress"
    FORMAT_CONVERSION = "format_conversion"
    OPTIMIZE = "optimize"


class OutputMode(Enum):
    """Output mode enumeration"""
    OVERWRITE = "overwrite"
    NEW_FOLDER = "new_folder"
    CUSTOM_DIR = "custom_dir"


@dataclass
class ProcessingOptions:
    """Processing options data class"""
    process_type: ProcessType
    output_mode: OutputMode
    output_dir: Optional[str] = None
    params: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class ProcessingResult:
    """Processing result data class"""
    success: bool
    input_path: str
    output_path: str
    input_size: int
    output_size: int
    error: Optional[str] = None
    compression_ratio: Optional[float] = None
    processing_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def compression_percentage(self) -> Optional[float]:
        """Get compression percentage"""
        if self.input_size > 0 and self.output_size > 0:
            return (1 - self.output_size / self.input_size) * 100
        return None


@dataclass
class ImageInfo:
    """Image information data class"""
    width: int
    height: int
    format: str
    filesize: int
    resolution: Optional[tuple] = None
    dpi: Optional[int] = None
    
    @property
    def aspect_ratio(self) -> float:
        """Get aspect ratio"""
        return self.width / self.height if self.height > 0 else 0
    
    @property
    def megapixels(self) -> float:
        """Get megapixels"""
        return (self.width * self.height) / 1000000


@dataclass
class BatchProcessingOptions:
    """Batch processing options"""
    files: list
    options: ProcessingOptions
    create_backups: bool = True
    stop_on_error: bool = False
    
    @property
    def total_files(self) -> int:
        """Get total number of files"""
        return len(self.files)