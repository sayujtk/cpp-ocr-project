import os
import json
import time
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

load_dotenv()

endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))

# Safety parameters (prevent infinite loops and excessive requests)
MAX_RETRIES = 3          # Max 3 polling attempts
POLLING_INTERVAL = 2     # Wait 2 seconds between polls
OPERATION_TIMEOUT = 60   # Give up after 60 seconds
REQUEST_DELAY = 5        # Wait 5 seconds between new image requests

def process_image(image_path):
    """Process image and extract text with safety limits."""
    
    print(f"Processing: {image_path}")
    time.sleep(REQUEST_DELAY)  # Wait before request
    
    # Submit image for OCR
    with open(image_path, "rb") as image_file:
        result = client.read_in_stream(image_file, raw=True)
    
    operation_location = result.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]
    
    # Poll for results with safety limits
    start_time = time.time()
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        # Check timeout
        if time.time() - start_time > OPERATION_TIMEOUT:
            print("⏱️ Timeout: Processing took too long")
            return None
        
        time.sleep(POLLING_INTERVAL)
        results = client.get_read_result(operation_id)
        retry_count += 1
        
        if results.status not in ['notStarted', 'running']:
            return results
    
    print("❌ Max retries exceeded")
    return None

def main():
    image_path = "cpp_code_images/test5.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    # Process image
    results = process_image(image_path)
    
    if results is None or results.status != OperationStatusCodes.succeeded:
        print("❌ OCR failed")
        return
    
    # Extract text
    print("\nRecognized Text:")
    print("-" * 80)
    for text_result in results.analyze_result.read_results:
        for line in text_result.lines:
            print(line.text)
    print("-" * 80)
    
    # Save results
    os.makedirs("ocr_outputs", exist_ok=True)
    image_name = os.path.splitext(image_path)[0].split('/')[-1]
    json_filename = f"ocr_outputs/OCR_output_{image_name}.json"
    
    with open(json_filename, "w") as f:
        json.dump(results.as_dict(), f, indent=2)
    
    print(f"✅ Saved to: {json_filename}")

if __name__ == "__main__":
    main()