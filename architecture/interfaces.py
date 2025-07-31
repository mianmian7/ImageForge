"""
Interface definitions for ImagePass architecture
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path


class IImageProcessor(ABC):
    """Image processor interface"""
    
    @abstractmethod
    def process_single_image(self, input_path: str, output_path: str, 
                           process_type: str, process_params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single image"""
        pass
    
    @abstractmethod
    def process_multiple_images(self, input_paths: List[str], output_mode: str,
                              process_type: str, process_params: Dict[str, Any],
                              output_dir: str = None) -> List[Dict[str, Any]]:
        """Process multiple images"""
        pass
    
    @abstractmethod
    def set_processing_callback(self, callback: Callable[[str, int, int], None]):
        """Set processing progress callback"""
        pass
    
    @abstractmethod
    def stop_all_processing(self):
        """Stop all processing tasks"""
        pass
    
    @abstractmethod
    def get_image_info(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Get image information"""
        pass


class IImageProcessingStrategy(ABC):
    """Image processing strategy interface"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get strategy name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get strategy description"""
        pass
    
    @abstractmethod
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate processing parameters"""
        pass
    
    @abstractmethod
    def process_image(self, input_path: str, output_path: str, 
                     params: Dict[str, Any]) -> Dict[str, Any]:
        """Process image with given parameters"""
        pass


class IFileManager(ABC):
    """File manager interface"""
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get supported image formats"""
        pass
    
    @abstractmethod
    def is_image_file(self, file_path: str) -> bool:
        """Check if file is supported image format"""
        pass
    
    @abstractmethod
    def select_single_file(self, file_path: str) -> Optional[str]:
        """Select single file"""
        pass
    
    @abstractmethod
    def select_directory(self, directory_path: str, recursive: bool = True) -> List[str]:
        """Select directory and get image files"""
        pass
    
    @abstractmethod
    def get_output_path(self, input_path: str, output_mode: str, 
                       output_dir: str = None) -> str:
        """Get output path based on mode"""
        pass
    
    @abstractmethod
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create file backup"""
        pass


class IConfigManager(ABC):
    """Configuration manager interface"""
    
    @abstractmethod
    def get(self, key: str, default=None, section='DEFAULT') -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, section='DEFAULT'):
        """Set configuration value"""
        pass
    
    @abstractmethod
    def save(self):
        """Save configuration"""
        pass
    
    @abstractmethod
    def load(self):
        """Load configuration"""
        pass


class IEventManager(ABC):
    """Event manager interface"""
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event"""
        pass
    
    @abstractmethod
    def publish(self, event_type: str, data: Any = None):
        """Publish event"""
        pass


class IUIComponent(ABC):
    """UI component interface"""
    
    @abstractmethod
    def initialize(self, parent):
        """Initialize component"""
        pass
    
    @abstractmethod
    def update(self, data: Any):
        """Update component with data"""
        pass
    
    @abstractmethod
    def get_state(self) -> Any:
        """Get component state"""
        pass
    
    @abstractmethod
    def set_enabled(self, enabled: bool):
        """Enable/disable component"""
        pass