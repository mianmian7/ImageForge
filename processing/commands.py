"""
Command pattern implementation for image processing operations
"""

import time
import threading
from typing import List, Dict, Any, Callable, Optional
from abc import ABC, abstractmethod

from architecture.interfaces import IImageProcessingStrategy
from processing.models import ProcessingResult, ProcessingOptions, BatchProcessingOptions
from core.file_manager import FileManager


class ProcessCommand(ABC):
    """Abstract base class for processing commands"""
    
    @abstractmethod
    def execute(self) -> List[ProcessingResult]:
        """Execute the command"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the command execution"""
        pass
    
    @abstractmethod
    def get_progress(self) -> tuple:
        """Get progress (current, total)"""
        pass


class SingleProcessCommand(ProcessCommand):
    """Command for processing a single image"""
    
    def __init__(self, strategy: IImageProcessingStrategy, 
                 input_path: str, output_path: str, params: Dict[str, Any]):
        self.strategy = strategy
        self.input_path = input_path
        self.output_path = output_path
        self.params = params
        self._stopped = False
        self._progress = (0, 1)
    
    def execute(self) -> List[ProcessingResult]:
        """Execute single image processing"""
        self._progress = (1, 1)
        
        if self._stopped:
            return []
        
        result = self.strategy.process_image(
            self.input_path, self.output_path, self.params
        )
        
        return [result]
    
    def stop(self):
        """Stop processing"""
        self._stopped = True
    
    def get_progress(self) -> tuple:
        """Get progress"""
        return self._progress


class BatchProcessCommand(ProcessCommand):
    """Command for processing multiple images"""
    
    def __init__(self, strategy: IImageProcessingStrategy, 
                 file_manager: FileManager,
                 options: BatchProcessingOptions,
                 progress_callback: Optional[Callable] = None):
        self.strategy = strategy
        self.file_manager = file_manager
        self.options = options
        self.progress_callback = progress_callback
        self._stopped = False
        self._progress = (0, len(options.files))
        self._results = []
    
    def execute(self) -> List[ProcessingResult]:
        """Execute batch image processing"""
        total_files = len(self.options.files)
        results = []
        
        for i, input_path in enumerate(self.options.files):
            if self._stopped:
                break
            
            self._progress = (i, total_files)
            
            try:
                # Get output path
                output_path = self.file_manager.get_output_path(
                    input_path, 
                    self.options.options.output_mode.value,
                    self.options.options.output_dir
                )
                
                # Create backup if needed
                if (self.options.options.output_mode.value == 'overwrite' and 
                    self.options.create_backups):
                    self.file_manager.create_backup(input_path)
                
                # Process image
                result = self.strategy.process_image(
                    input_path, output_path, self.options.options.params
                )
                
                # Add file index to result
                result.metadata['file_index'] = i
                
                results.append(result)
                
                # Call progress callback
                if self.progress_callback:
                    self.progress_callback(input_path, i + 1, total_files)
                    
            except Exception as e:
                # Create error result
                error_result = ProcessingResult(
                    success=False,
                    input_path=input_path,
                    output_path="",
                    input_size=0,
                    output_size=0,
                    error=str(e),
                    metadata={'file_index': i}
                )
                results.append(error_result)
                
                if self.options.stop_on_error:
                    break
        
        self._progress = (len(results), total_files)
        self._results = results
        
        return results
    
    def stop(self):
        """Stop batch processing"""
        self._stopped = True
    
    def get_progress(self) -> tuple:
        """Get progress"""
        return self._progress
    
    def get_results(self) -> List[ProcessingResult]:
        """Get current results"""
        return self._results.copy()


class ThreadedCommandExecutor:
    """Executor for running commands in separate threads"""
    
    def __init__(self, max_workers: int = 2):
        self.max_workers = max_workers
        self._active_threads = []
        self._current_command = None
        self._lock = threading.Lock()
    
    def execute_command(self, command: ProcessCommand, 
                       completion_callback: Optional[Callable] = None) -> bool:
        """Execute command in a separate thread"""
        
        with self._lock:
            if len(self._active_threads) >= self.max_workers:
                return False
            
            self._current_command = command
            
            def run_command():
                try:
                    results = command.execute()
                    
                    if completion_callback:
                        completion_callback(results)
                        
                except Exception as e:
                    print(f"Command execution error: {e}")
                    
                finally:
                    with self._lock:
                        self._current_command = None
                        self._cleanup_threads()
            
            thread = threading.Thread(target=run_command)
            thread.daemon = True
            thread.start()
            self._active_threads.append(thread)
            
            return True
    
    def stop_current(self):
        """Stop current command"""
        with self._lock:
            if self._current_command:
                self._current_command.stop()
    
    def get_progress(self) -> tuple:
        """Get current command progress"""
        with self._lock:
            if self._current_command:
                return self._current_command.get_progress()
            return (0, 0)
    
    def is_processing(self) -> bool:
        """Check if currently processing"""
        with self._lock:
            return self._current_command is not None
    
    def _cleanup_threads(self):
        """Clean up finished threads"""
        self._active_threads = [t for t in self._active_threads if t.is_alive()]


class ProcessingCommandFactory:
    """Factory for creating processing commands"""
    
    @staticmethod
    def create_single_command(strategy: IImageProcessingStrategy,
                             input_path: str, output_path: str, 
                             params: Dict[str, Any]) -> SingleProcessCommand:
        """Create single processing command"""
        return SingleProcessCommand(strategy, input_path, output_path, params)
    
    @staticmethod
    def create_batch_command(strategy: IImageProcessingStrategy,
                           file_manager: FileManager,
                           options: BatchProcessingOptions,
                           progress_callback: Optional[Callable] = None) -> BatchProcessCommand:
        """Create batch processing command"""
        return BatchProcessCommand(strategy, file_manager, options, progress_callback)