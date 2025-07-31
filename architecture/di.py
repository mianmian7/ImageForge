"""
Dependency injection container for ImagePass
Provides simple dependency management
"""

from typing import Dict, Any, Type, Callable, Optional
from .interfaces import IConfigManager, IFileManager, IImageProcessor, IEventManager


class DependencyContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any, singleton: bool = False):
        """Register a service instance"""
        if singleton:
            self._singletons[name] = service
        else:
            self._services[name] = service
    
    def register_factory(self, name: str, factory: Callable, singleton: bool = False):
        """Register a factory function"""
        self._factories[name] = (factory, singleton)
    
    def register_type(self, name: str, service_type: Type, singleton: bool = False, **kwargs):
        """Register a service type"""
        def factory():
            return service_type(**kwargs)
        
        self.register_factory(name, factory, singleton)
    
    def get(self, name: str) -> Any:
        """Get a service instance"""
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]
        
        # Check direct services
        if name in self._services:
            return self._services[name]
        
        # Check factories
        if name in self._factories:
            factory, is_singleton = self._factories[name]
            instance = factory()
            
            if is_singleton:
                self._singletons[name] = instance
            
            return instance
        
        raise KeyError(f"Service '{name}' not registered")
    
    def has(self, name: str) -> bool:
        """Check if service is registered"""
        return (name in self._services or 
                name in self._factories or 
                name in self._singletons)
    
    def remove(self, name: str):
        """Remove a service"""
        self._services.pop(name, None)
        self._factories.pop(name, None)
        self._singletons.pop(name, None)
    
    def clear(self):
        """Clear all services"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
    
    def get_config(self) -> IConfigManager:
        """Get configuration manager"""
        return self.get('config')
    
    def get_file_manager(self) -> IFileManager:
        """Get file manager"""
        return self.get('file_manager')
    
    def get_image_processor(self) -> IImageProcessor:
        """Get image processor"""
        return self.get('image_processor')
    
    def get_event_manager(self) -> IEventManager:
        """Get event manager"""
        return self.get('event_manager')


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get global container instance"""
    global _container
    if _container is None:
        _container = DependencyContainer()
    return _container


def set_container(container: DependencyContainer):
    """Set global container instance"""
    global _container
    _container = container


def inject(service_name: str):
    """Decorator for dependency injection"""
    def decorator(cls):
        original_init = cls.__init__
        
        def __init__(self, *args, **kwargs):
            # Get service from container
            if hasattr(self, '_container'):
                container = self._container
            else:
                container = get_container()
            
            service = container.get(service_name)
            
            # Inject service
            setattr(self, f"_{service_name}", service)
            
            # Call original init
            original_init(self, *args, **kwargs)
        
        cls.__init__ = __init__
        return cls
    
    return decorator