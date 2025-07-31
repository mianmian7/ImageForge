"""
Image processor factory for creating strategies and processors
"""

from typing import Dict, List, Optional, Any
from architecture.interfaces import IImageProcessingStrategy

from processing.strategies import (
    ResizeStrategy, CompressStrategy, FormatConversionStrategy, OptimizeStrategy
)
from processing.models import ProcessType, ProcessingOptions


class ImageProcessorFactory:
    """Factory for creating image processing strategies"""
    
    def __init__(self, config=None):
        self.config = config
        self._strategies: Dict[str, IImageProcessingStrategy] = {}
        self._initialize_strategies()
    
    def _initialize_strategies(self):
        """Initialize default strategies"""
        # Get configuration values
        imagemagick_path = None
        tinypng_api_key = None
        
        if self.config:
            try:
                imagemagick_path = self.config.get_imagemagick_path()
                tinypng_api_key = self.config.get_tinypng_api_key()
            except AttributeError:
                pass
        
        # Create strategies
        self._strategies[ProcessType.RESIZE.value] = ResizeStrategy(imagemagick_path)
        self._strategies[ProcessType.COMPRESS.value] = CompressStrategy(tinypng_api_key)
        self._strategies[ProcessType.FORMAT_CONVERSION.value] = FormatConversionStrategy(imagemagick_path)
        self._strategies[ProcessType.OPTIMIZE.value] = OptimizeStrategy(imagemagick_path)
    
    def get_strategy(self, process_type: str) -> Optional[IImageProcessingStrategy]:
        """Get strategy by process type"""
        return self._strategies.get(process_type)
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategy names"""
        return list(self._strategies.keys())
    
    def get_strategy_info(self, process_type: str) -> Dict:
        """Get strategy information"""
        strategy = self.get_strategy(process_type)
        if strategy:
            return {
                'name': strategy.get_name(),
                'description': strategy.get_description(),
                'type': process_type
            }
        return {}
    
    def get_all_strategies_info(self) -> List[Dict]:
        """Get information for all strategies"""
        info = []
        for process_type in self.get_available_strategies():
            strategy_info = self.get_strategy_info(process_type)
            if strategy_info:
                info.append(strategy_info)
        return info
    
    def register_strategy(self, process_type: str, strategy: IImageProcessingStrategy):
        """Register a custom strategy"""
        self._strategies[process_type] = strategy
    
    def unregister_strategy(self, process_type: str):
        """Unregister a strategy"""
        self._strategies.pop(process_type, None)
    
    def validate_strategy_params(self, process_type: str, params: Dict) -> bool:
        """Validate parameters for a strategy"""
        strategy = self.get_strategy(process_type)
        if strategy:
            return strategy.validate_params(params)
        return False
    
    def update_config(self, config):
        """Update configuration and reinitialize strategies"""
        self.config = config
        self._initialize_strategies()
    
    def set_tinypng_api_key(self, api_key: str):
        """Update TinyPNG API key"""
        if ProcessType.COMPRESS.value in self._strategies:
            strategy = self._strategies[ProcessType.COMPRESS.value]
            if isinstance(strategy, CompressStrategy):
                strategy.tinypng = type(strategy.tinypng)(api_key) if api_key else None
    
    def set_imagemagick_path(self, path: str):
        """Update ImageMagick path"""
        for strategy_name, strategy in self._strategies.items():
            if strategy_name != ProcessType.COMPRESS.value:
                if hasattr(strategy, 'imagemagick'):
                    strategy.imagemagick = ImageMagickWrapper(path)


class ProcessingOptionsBuilder:
    """Builder for creating processing options"""
    
    def __init__(self):
        self._process_type = None
        self._output_mode = None
        self._output_dir = None
        self._params = {}
    
    def set_process_type(self, process_type: ProcessType):
        """Set process type"""
        self._process_type = process_type
        return self
    
    def set_output_mode(self, output_mode):
        """Set output mode"""
        self._output_mode = output_mode
        return self
    
    def set_output_dir(self, output_dir: str):
        """Set output directory"""
        self._output_dir = output_dir
        return self
    
    def set_params(self, params: Dict):
        """Set processing parameters"""
        self._params.update(params)
        return self
    
    def add_param(self, key: str, value: Any):
        """Add a single parameter"""
        self._params[key] = value
        return self
    
    def build(self) -> ProcessingOptions:
        """Build processing options"""
        if self._process_type is None:
            raise ValueError("Process type must be set")
        if self._output_mode is None:
            raise ValueError("Output mode must be set")
        
        return ProcessingOptions(
            process_type=self._process_type,
            output_mode=self._output_mode,
            output_dir=self._output_dir,
            params=self._params.copy()
        )
    
    def reset(self):
        """Reset builder"""
        self._process_type = None
        self._output_mode = None
        self._output_dir = None
        self._params.clear()
        return self


class BatchProcessingOptionsBuilder:
    """Builder for creating batch processing options"""
    
    def __init__(self):
        self._files = []
        self._options = None
        self._create_backups = True
        self._stop_on_error = False
    
    def set_files(self, files: List[str]):
        """Set files to process"""
        self._files = files.copy()
        return self
    
    def add_file(self, file_path: str):
        """Add a single file"""
        self._files.append(file_path)
        return self
    
    def set_processing_options(self, options: ProcessingOptions):
        """Set processing options"""
        self._options = options
        return self
    
    def set_create_backups(self, create_backups: bool):
        """Set backup creation flag"""
        self._create_backups = create_backups
        return self
    
    def set_stop_on_error(self, stop_on_error: bool):
        """Set stop on error flag"""
        self._stop_on_error = stop_on_error
        return self
    
    def build(self) -> 'BatchProcessingOptions':
        """Build batch processing options"""
        if not self._files:
            raise ValueError("Files list cannot be empty")
        if self._options is None:
            raise ValueError("Processing options must be set")
        
        from processing.models import BatchProcessingOptions
        return BatchProcessingOptions(
            files=self._files.copy(),
            options=self._options,
            create_backups=self._create_backups,
            stop_on_error=self._stop_on_error
        )
    
    def reset(self):
        """Reset builder"""
        self._files.clear()
        self._options = None
        self._create_backups = True
        self._stop_on_error = False
        return self