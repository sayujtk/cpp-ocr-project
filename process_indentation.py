import json
import os
from cpp_indentation_recognition import apply_mean_shift_indentation

def extract_ocr_output_from_azure(azure_json_data):
    """
    Convert Azure OCR JSON to internal ocr_output format.
    Handles the newer Azure API format with analyze_result.read_results
    """
    ocr_output = []
    image_width = 800
    image_height = 600
    
    try:
        # New Azure API format: analyze_result.read_results
        if 'analyze_result' in azure_json_data:
            analyze_result = azure_json_data['analyze_result']
            read_results = analyze_result.get('read_results', [])
            
            if read_results:
                # Get first page
                page_data = read_results[0]
                
                # Extract image dimensions
                image_width = page_data.get('width', 800)
                image_height = page_data.get('height', 600)
                
                # Extract lines
                lines = page_data.get('lines', [])
                
                for i, line in enumerate(lines):
                    line_dict = {}
                    line_dict['text'] = line.get('text', '').strip()
                    line_dict['line_num'] = i + 1
                    
                    # Get bounding box coordinates
                    # Format: [x1, y1, x2, y2, x3, y3, x4, y4]
                    bounding_box = line.get('bounding_box', [])
                    
                    if len(bounding_box) >= 8:
                        # Top-left x coordinate
                        line_dict['x'] = bounding_box[0]
                        line_dict['y'] = bounding_box[1]
                        # Width and height
                        line_dict['w'] = bounding_box[2] - bounding_box[0]
                        line_dict['h'] = bounding_box[5] - bounding_box[1]
                    else:
                        line_dict['x'] = 0
                        line_dict['y'] = 0
                        line_dict['w'] = 0
                        line_dict['h'] = 0
                    
                    ocr_output.append(line_dict)
        else:
            print("ERROR: Cannot find analyze_result in JSON")
            print(f"Available keys: {list(azure_json_data.keys())}")
        
    except Exception as e:
        print(f"ERROR parsing Azure JSON: {e}")
    
    return ocr_output, image_width, image_height


def process_azure_ocr_json(json_file_path, bandwidth=None):
    """Read Azure OCR JSON and apply indentation recognition."""
    
    if not os.path.exists(json_file_path):
        print(f"ERROR: File not found: {json_file_path}")
        return None
    
    with open(json_file_path, 'r') as f:
        azure_json_data = json.load(f)
    
    ocr_output, image_width, image_height = extract_ocr_output_from_azure(azure_json_data)
    
    print(f"✓ Extracted {len(ocr_output)} lines from OCR")
    print(f"✓ Image dimensions: {image_width}x{image_height}")
    
    if len(ocr_output) == 0:
        print("WARNING: No lines extracted. Check your JSON file.")
        return None
    
    result = apply_mean_shift_indentation(ocr_output, image_width, bandwidth=bandwidth)
    
    result['raw_ocr'] = ocr_output
    result['image_width'] = image_width
    result['image_height'] = image_height
    
    return result


def print_before_after(raw_ocr, corrected_code):
    """Print before/after comparison."""
    print("\n" + "="*80)
    print("BEFORE (Raw OCR - No Indentation Fix)")
    print("="*80)
    
    raw_text = '\n'.join([line['text'] for line in raw_ocr])
    print(raw_text if raw_text else "(No text extracted)")
    
    print("\n" + "="*80)
    print("AFTER (With Indentation Recognition Applied)")
    print("="*80)
    print(corrected_code if corrected_code else "(No code generated)")
    print("="*80 + "\n")


def save_corrected_code(corrected_code, output_file):
    """Save corrected code to file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(corrected_code)
    print(f"✓ Corrected code saved to: {output_file}")