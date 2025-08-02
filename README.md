# ImageForge

A powerful Python GUI application for batch image processing with support for local and cloud-based optimization.

## Features

- **Batch Processing**: Process multiple images simultaneously with progress tracking
- **Multiple Optimization Options**:
  - Local compression using Pillow
  - Cloud compression using TinyPNG API
  - Image resizing with configurable dimensions
  - Format conversion (JPEG, PNG, BMP, GIF, TIFF, WebP)
- **Asset Cleaning**: Built-in asset cleaner with Cocos Creator integration
- **Flexible Output Modes**:
  - Overwrite original files
  - Create new folder with processed images
  - Custom output directory
- **Real-time Preview**: Visual feedback before processing
- **Configurable Settings**: API keys, compression quality, processing preferences

## Screenshots

*Coming soon*

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/ImageForge.git
cd ImageForge
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Edit `config.ini` to set up your TinyPNG API key and customize processing settings:

```ini
[tinypng]
api_key = your_tinypng_api_key_here

[processing]
default_compression = 0.8
max_file_size_mb = 10
supported_formats = jpeg,png,bmp,giff,tiff,webp
```

## Usage

### Running the Application

```bash
python main.py
```

### Basic Operation

1. **Select Images**: Use the file browser to select one or multiple images
2. **Choose Processing Type**:
   - **Compress**: Reduce file size while maintaining quality
   - **Resize**: Change image dimensions
   - **Compress + Resize**: Combine both operations
3. **Configure Settings**: Adjust compression level, output format, and dimensions
4. **Set Output Directory**: Choose where to save processed images
5. **Process**: Click the process button and monitor progress

### Asset Cleaning

The included asset cleaner tool helps optimize images for game development:

```bash
cd tools/asset-cleaner-cocos
python main.py
```

## Architecture

```
ImageForge/
├── core/                    # Core business logic
│   ├── config.py           # Configuration management
│   ├── file_manager.py     # File operations
│   ├── image_processor.py  # Main processing logic
│   └── logger.py          # Logging system
├── gui/                    # User interface
│   ├── main_window.py     # Main application window
│   ├── asset_cleaner_panel.py  # Asset cleaning UI
│   └── managers/          # UI component managers
├── utils/                  # Utility modules
│   ├── pillow_wrapper.py  # Local image processing
│   ├── tinypng_client.py  # TinyPNG API client
│   └── asset_cleaner/     # Asset cleaning utilities
├── tools/                  # Additional tools
│   └── asset-cleaner-cocos/ # Cocos Creator asset cleaner
├── main.py                 # Application entry point
├── config.ini             # Configuration file
└── requirements.txt       # Python dependencies
```

### Core Components

- **ImageProcessor**: Main orchestrator for image processing operations
- **PillowWrapper**: Local image processing with fallback support
- **TinyPNGClient**: Cloud-based compression using TinyPNG API
- **FileManager**: File handling and directory operations
- **GUI Managers**: Modular UI components (MainView, ProcessControl, etc.)

## Supported Formats

- **Input**: JPEG, PNG, BMP, GIF, TIFF, WebP
- **Output**: JPEG, PNG, BMP, GIF, TIFF, WebP

## Dependencies

- **Pillow**: Image processing and manipulation
- **Wand**: ImageMagick wrapper for advanced processing
- **requests**: HTTP client for API communication
- **tkinter**: GUI framework (included with Python)
- **configparser**: Configuration file management

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release with batch image processing
- TinyPNG API integration
- Asset cleaning functionality
- GUI with real-time preview
- Support for multiple image formats

## Acknowledgments

- [TinyPNG](https://tinypng.com/) for providing the compression API
- [Pillow](https://python-pillow.org/) for image processing capabilities
- [Cocos Creator](https://www.cocos.com/creator) for game development framework

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section in the documentation
- Review the [CLAUDE.md](CLAUDE.md) file for development guidance