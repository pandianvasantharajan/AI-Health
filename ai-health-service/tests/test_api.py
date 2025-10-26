"""
Example usage of the AI Health Service API
"""

import requests
import os
from pathlib import Path

# Service URL
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_upload_pdf(file_path: str):
    """Test PDF upload endpoint"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as file:
        files = {
            'file': (os.path.basename(file_path), file, 'application/pdf')
        }
        data = {
            'folder': 'test-uploads'
        }
        
        response = requests.post(f"{BASE_URL}/upload/pdf", files=files, data=data)
        
    print(f"Upload status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def create_sample_pdf():
    """Create a sample PDF file for testing"""
    sample_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Hello, World!) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
0000000185 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
279
%%EOF"""
    
    sample_file = "sample_test.pdf"
    with open(sample_file, 'wb') as f:
        f.write(sample_content)
    
    return sample_file

def main():
    """Main test function"""
    print("=== AI Health Service API Test ===")
    
    # Test health check
    print("\n1. Testing health check...")
    if not test_health_check():
        print("Health check failed! Make sure the service is running.")
        return
    
    # Create a sample PDF for testing
    print("\n2. Creating sample PDF...")
    sample_file = create_sample_pdf()
    print(f"Created sample file: {sample_file}")
    
    # Test PDF upload
    print("\n3. Testing PDF upload...")
    success = test_upload_pdf(sample_file)
    
    # Cleanup
    if os.path.exists(sample_file):
        os.remove(sample_file)
        print(f"Cleaned up sample file: {sample_file}")
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")

if __name__ == "__main__":
    main()