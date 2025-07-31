# py_src/asset_size_analyzer.py - Analyzes asset sizes in a directory
import os
from collections import defaultdict
from . import file_helper
from . import utils

class AssetSizeAnalyzer:
    def __init__(self):
        self.file_map = defaultdict(list)

    def start(self, source_dir: str, dest_file: str):
        """Starts the asset size analysis."""
        if not source_dir or not dest_file:
            print("Error: Invalid source or destination.")
            return

        source_dir = file_helper.get_full_path(source_dir)
        dest_file = file_helper.get_full_path(dest_file)

        self._lookup_asset_dir(source_dir)
        output_str = self._get_sorted_result(source_dir)
        file_helper.write_file(dest_file, output_str)

    def _lookup_asset_dir(self, src_dir: str):
        """Recursively looks up assets in a directory."""
        if not os.path.isdir(src_dir):
            print(f"Error: Invalid source directory = {src_dir}")
            return

        for file in os.listdir(src_dir):
            cur_path = os.path.join(src_dir, file)
            if os.path.isdir(cur_path):
                self._lookup_asset_dir(cur_path)
                continue

            try:
                stats = os.stat(cur_path)
                _, ext = os.path.splitext(cur_path)
                # The original JS version had a memory calculation that is commented out.
                # We will omit it for now unless required.
                self.file_map[ext].append({'path': cur_path, 'size': stats.st_size})
            except FileNotFoundError:
                print(f"Warning: Could not stat file {cur_path}, it may have been deleted.")

    def _get_sorted_result(self, src_dir: str) -> str:
        """Gets the sorted result of the analysis."""
        all_types = []
        total_project_size = 0

        for ext, files in self.file_map.items():
            total_size = sum(f['size'] for f in files)
            total_project_size += total_size
            
            # Sort files by size descending
            files.sort(key=lambda x: x['size'], reverse=True)
            
            all_types.append({
                'ext': ext if ext else 'no_extension',
                'count': len(files),
                'total_size': total_size,
                'files': files
            })

        # Sort types by total size descending
        all_types.sort(key=lambda x: x['total_size'], reverse=True)

        # Build the output string
        summary_lines = [f"总空间: {utils.byte_to_mb_str(total_project_size)} MB, 目录: {src_dir}\n"]
        for t in all_types:
            summary_lines.append(
                f"类型: {t['ext']}, 个数: {t['count']}, "
                f"占用空间: {utils.byte_to_mb_str(t['total_size'])} MB"
            )
        
        detail_lines = []
        for t in all_types:
            detail_lines.append(f"\n--- {t['ext']} 类型详情 ---")
            for f in t['files']:
                detail_lines.append(f"空间: {utils.byte_to_kb_str(f['size'])} KB, 文件: {f['path']}")

        return "\n".join(summary_lines) + "\n" + "\n".join(detail_lines)

def start(source_dir: str, dest_file: str):
    analyzer = AssetSizeAnalyzer()
    analyzer.start(source_dir, dest_file)