import sys
import json
import argparse
from process_indentation import process_azure_ocr_json, print_before_after, save_corrected_code

def main():
    parser = argparse.ArgumentParser(
        description='C++ Handwritten Code OCR - Indentation Recognition Pipeline'
    )
    parser.add_argument(
        '--input-json',
        required=True,
        help='Path to Azure OCR JSON file (output from test_ocr.py)'
    )
    parser.add_argument(
        '--output-file',
        default='corrected_code.cpp',
        help='Output file for corrected C++ code (default: corrected_code.cpp)'
    )
    parser.add_argument(
        '--bandwidth',
        type=float,
        default=None,
        help='Bandwidth for Mean Shift clustering (auto-estimated if not provided)'
    )
    parser.add_argument(
        '--show-comparison',
        action='store_true',
        help='Print before/after comparison'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("C++ Handwritten Code OCR - Indentation Recognition")
    print("=" * 80)
    print(f"\n📖 Processing: {args.input_json}")
    
    # Process OCR and apply indentation
    result = process_azure_ocr_json(args.input_json, bandwidth=args.bandwidth)
    
    if result is None:
        print("\n❌ Failed to process file")
        return 1
    
    corrected_code = result['code']
    raw_ocr = result['raw_ocr']
    metadata = result['metadata']
    
    # Print results (safely handle None values)
    print(f"\n📊 Indentation Recognition Results:")
    print(f"   Algorithm: {metadata.get('algorithm', 'N/A')}")
    if metadata.get('bandwidth') is not None:
        print(f"   Bandwidth: {metadata['bandwidth']:.2f}")
    print(f"   Number of indentation clusters: {metadata.get('num_clusters', 0)}")
    if metadata.get('cluster_to_indent_mapping'):
        print(f"   Cluster to indent mapping: {metadata['cluster_to_indent_mapping']}")
    
    # Show before/after if requested
    if args.show_comparison:
        print_before_after(raw_ocr, corrected_code)
    
    # Save output
    save_corrected_code(corrected_code, args.output_file)
    
    # Also save metadata as JSON
    metadata_file = args.output_file.replace('.cpp', '_metadata.json')
    with open(metadata_file, 'w') as f:
        json.dump({
            'input_file': args.input_json,
            'output_file': args.output_file,
            'corrected_code': corrected_code,
            'raw_ocr': raw_ocr,
            'metadata': metadata
        }, f, indent=2)
    print(f"✓ Metadata saved to: {metadata_file}")
    
    print("\n✅ Pipeline completed successfully!")
    return 0

if __name__ == '__main__':
    sys.exit(main())