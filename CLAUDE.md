# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py
```

### Testing
```bash
python test_fallback.py  # Test fallback functionality
```

## Architecture Overview

**ImageForge** is a Python GUI application for image processing with a modular, dependency-injected architecture.

### Core Architecture Pattern
- **Dependency Injection**: `architecture/di.py` - Central service container
- **Event Bus**: `architecture/events.py` - Decoupled component communication  
- **Interfaces**: `architecture/interfaces.py` - Contract definitions

### Main Components
- **Entry Point**: `main.py` - Application launcher
- **Core Logic**: `core/` - Business logic (config, image processing, file management, logging)
- **GUI**: `gui/` - Tkinter-based interface with manager pattern for UI components
- **Processing**: `processing/` - Command/Strategy patterns for image operations
- **Utils**: `utils/` - Pillow wrapper, TinyPNG client, asset cleaning tools

### Key Processing Flow
```
main.py → gui.main_window.ImageProcessorGUI → core.image_processor.ImageProcessor
├── utils.pillow_wrapper.PillowWrapper (local processing)
├── utils.tinypng_client.TinyPNGClient (cloud compression)
└── core.file_manager.FileManager (file operations)
```

### Supported Formats
JPEG, PNG, BMP, GIF, TIFF, WebP

### Configuration
- Main config: `config.ini` (TinyPNG API key, processing settings, UI preferences)
- API key currently hardcoded - should be secured for production

### Dependencies
- **Pillow**: Local image processing
- **Wand**: Optional ImageMagick wrapper  
- **requests**: HTTP client for TinyPNG API
- **tkinter**: GUI framework (bundled with Python)

### Output Modes
- Overwrite original files
- Create new folder
- Custom output directory

## Important Notes

- The application uses batch processing with multi-threading and progress callbacks
- Asset cleaning functionality includes Cocos Creator integration
- Multiple virtual environments may be present (venv, venv2, venv3) - use primary `venv`
- Missing PIL.ImageTk in current environment may affect preview functionality