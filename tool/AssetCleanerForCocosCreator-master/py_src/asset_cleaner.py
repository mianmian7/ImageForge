# py_src/asset_cleaner.py - Finds and cleans unused assets
import os
import json
from collections import defaultdict
from . import file_helper
from . import utils

# Mapping resource extensions to their types, similar to the JS version
# We can represent ResType with an Enum for better readability
from enum import Enum, auto

class ResType(Enum):
    IMAGE = auto()
    IMAGE_ATLAS = auto()
    LABEL_ATLAS = auto()
    ANIM = auto()
    SPINE = auto()
    PREFAB = auto()
    FIRE = auto() # Scene files
    CODE = auto()
    FNT = auto()

RES_EXT_MAP = {
    '.plist': ResType.IMAGE_ATLAS,
    '.fnt': ResType.FNT,
    '.labelatlas': ResType.LABEL_ATLAS,
    '.json': ResType.SPINE,
}

class AssetCleaner:
    def __init__(self, source_dir: str, dest_file: str, delete_unused=False, excludes=None):
        self.source_dir = file_helper.get_full_path(source_dir)
        self.dest_file = file_helper.get_full_path(dest_file)
        self.delete_unused = delete_unused
        self.excludes = excludes # To be implemented

        self.source_map = {}  # Stores assets that could be potentially unused (key: path, value: data)
        self.dest_map = {}    # Stores assets that reference other assets (key: path, value: data)
        self.handle_map = set() # Stores paths of files that have been processed to avoid duplicates
        self.resources_dir_name = 'resources'

    def start(self):
        """Starts the asset cleaning process."""
        if not self.source_dir or not self.dest_file:
            print("Error: Invalid source or destination.")
            return

        print("Starting asset lookup...")
        self._lookup_asset_dir(self.source_dir)
        print(f"Lookup complete. Found {len(self.source_map)} source assets and {len(self.dest_map)} destination assets.")
        
        print("Comparing assets to find unused files...")
        no_bind_map, no_load_map = self._compare_assets()
        
        out_str1 = self._get_sorted_result('未引用文件', no_bind_map)
        out_str2 = self._get_sorted_result('非动态加载(可移出resources)的文件', no_load_map)
        
        final_output = f"{out_str1}\n{out_str2}"
        file_helper.write_file(self.dest_file, final_output)
        print(f"Analysis complete. Results written to {self.dest_file}")

    def _get_file_uuid(self, file_path: str, res_type: ResType) -> list:
        """Gets the UUID(s) from a .meta file."""
        meta_path = f"{file_path}.meta"
        if not os.path.exists(meta_path):
            return []

        meta_data = file_helper.get_object_from_file(meta_path)
        if not meta_data:
            return []

        uuids = []
        # Simplified logic for now, will be expanded
        if 'uuid' in meta_data:
            uuids.append(meta_data['uuid'])
        
        # For atlases, we need to extract sub-asset UUIDs
        if res_type == ResType.IMAGE_ATLAS and 'subMetas' in meta_data:
            for sub_meta in meta_data['subMetas'].values():
                if 'uuid' in sub_meta:
                    uuids.append(sub_meta['uuid'])
        
        return uuids

    def _lookup_asset_dir(self, current_dir: str):
        """Recursively looks up assets in a directory."""
        for item in os.listdir(current_dir):
            full_path = os.path.join(current_dir, item)

            if full_path in self.handle_map:
                continue
            
            if os.path.isdir(full_path):
                self._lookup_asset_dir(full_path)
                continue

            self.handle_map.add(full_path)
            stats = os.stat(full_path)
            path_obj = os.path.splitext(full_path)
            ext = path_obj[1]
            
            # This is a simplified version of the logic in AssetCleaner.js
            # It will be expanded to handle all resource types correctly.
            if ext in ['.js', '.ts']:
                content = file_helper.get_file_string(full_path)
                self.dest_map[full_path] = {'data': content, 'type': ResType.CODE}
            elif ext == '.prefab':
                uuids = self._get_file_uuid(full_path, ResType.PREFAB)
                self.source_map[full_path] = {'uuid': uuids, 'type': ResType.PREFAB, 'size': stats.st_size}
                content = file_helper.get_file_string(full_path)
                self.dest_map[full_path] = {'data': content, 'type': ResType.PREFAB}
            elif ext == '.fire':
                content = file_helper.get_file_string(full_path)
                self.dest_map[full_path] = {'data': content, 'type': ResType.FIRE}
            elif ext in ['.png', '.jpg', '.webp']:
                # Simplified image handling
                uuids = self._get_file_uuid(full_path, ResType.IMAGE)
                self.source_map[full_path] = {'uuid': uuids, 'type': ResType.IMAGE, 'size': stats.st_size}

    def _compare_assets(self) -> (dict, dict):
        """Compares source and destination assets to find unused ones."""
        no_bind_map = defaultdict(list)
        # no_load_map logic will be added later
        no_load_map = defaultdict(list) 

        all_dest_content = " ".join([d['data'] for d in self.dest_map.values() if d['type'] != ResType.CODE])
        
        for src_path, src_data in self.source_map.items():
            is_bind = False
            if 'uuid' in src_data:
                for uuid in src_data['uuid']:
                    if uuid in all_dest_content:
                        is_bind = True
                        break
            
            if not is_bind:
                no_bind_map[src_data['type']].append({'path': src_path, 'size': src_data['size']})

        return no_bind_map, no_load_map

    def _get_sorted_result(self, title: str, result_map: dict) -> str:
        """Formats the result map into a sorted string."""
        output_lines = []
        total_count = 0
        total_size = 0

        for res_type, files in result_map.items():
            if not files:
                continue
            
            files.sort(key=lambda x: x['size'], reverse=True)
            total_count += len(files)
            
            for file_info in files:
                total_size += file_info['size']
                output_lines.append(f"空间: {utils.byte_to_kb_str(file_info['size'])} KB, 文件: {file_info['path']}")

        header = (f"\n--- {title} ---\n"
                  f"总数: {total_count}, 总空间: {utils.byte_to_mb_str(total_size)} MB\n")
        
        return header + "\n".join(output_lines)


def start(source_dir: str, dest_file: str, delete_unused=False, excludes=None):
    cleaner = AssetCleaner(source_dir, dest_file, delete_unused, excludes)
    cleaner.start()