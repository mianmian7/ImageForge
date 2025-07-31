# main.py - Entry point for the Asset Cleaner tool
import argparse
from . import asset_cleaner
from . import asset_size_analyzer

def main():
    """Main function to parse arguments and run the tool."""
    parser = argparse.ArgumentParser(
        description="A tool to clean unused assets and analyze asset sizes for Cocos Creator projects (Python Version)."
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Clean command ---
    parser_clean = subparsers.add_parser('clean', help='Find unused assets.')
    parser_clean.add_argument('source_dir', type=str, help='The assets directory of the Cocos Creator project.')
    parser_clean.add_argument('dest_file', type=str, help='The output file for the report.')
    parser_clean.add_argument('-d', '--delete', action='store_true', help='Automatically delete unused assets.')
    parser_clean.add_argument('-e', '--excludes', type=str, help='Regex pattern for files/paths to exclude from deletion.')

    # --- Size command ---
    parser_size = subparsers.add_parser('size', help='Analyze asset sizes.')
    parser_size.add_argument('source_dir', type=str, help='The directory to analyze.')
    parser_size.add_argument('dest_file', type=str, help='The output file for the report.')

    args = parser.parse_args()

    if args.command == 'clean':
        print(f"Running 'clean' on {args.source_dir}...")
        asset_cleaner.start(
            args.source_dir,
            args.dest_file,
            delete_unused=args.delete,
            excludes=args.excludes
        )
    elif args.command == 'size':
        print(f"Running 'size' on {args.source_dir}...")
        asset_size_analyzer.start(args.source_dir, args.dest_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
