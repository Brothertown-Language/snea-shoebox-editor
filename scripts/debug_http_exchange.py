# Copyright (c) 2026 Brothertown Language
import os
import json
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

API_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen3-Embedding-0.6B/pipeline/feature-extraction"
headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}",
}

def monkey_patch_requests():
    original_post = requests.post
    
    def patched_post(url, **kwargs):
        print(f"\n--- HTTP Request ---")
        print(f"URL: {url}")
        print(f"Method: POST")
        if 'headers' in kwargs:
            # Mask the token for safety in output
            safe_headers = kwargs['headers'].copy()
            if 'Authorization' in safe_headers:
                safe_headers['Authorization'] = "Bearer [MASKED]"
            print(f"Headers: {json.dumps(safe_headers, indent=2)}")
        if 'json' in kwargs:
            print(f"Body (JSON): {json.dumps(kwargs['json'], indent=2)}")
        elif 'data' in kwargs:
            print(f"Body (Data): {kwargs['data']}")
        print(f"--------------------\n")
        
        try:
            response = original_post(url, **kwargs)
            
            print(f"\n--- HTTP Response ---")
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
            try:
                print(f"Body: {json.dumps(response.json(), indent=2)}")
            except:
                print(f"Body: {response.text}")
            print(f"---------------------\n")
            
            return response
        except Exception as e:
            print(f"\n--- HTTP Error ---")
            print(f"Exception: {e}")
            print(f"------------------\n")
            raise

    requests.post = patched_post
    print("Monkey patched requests.post")

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"Error: API returned status code {response.status_code} for URL: {API_URL}")
        print("Aborting.")
        response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    monkey_patch_requests()
    output = query({
        "inputs": "Today is a sunny day and I will get some ice cream.",
    })
    # print(output)
