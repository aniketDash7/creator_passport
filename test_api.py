import requests
import os

API_URL = "http://127.0.0.1:8080/api"

def run_test():
    print("--- Starting Integration Test ---")
    
    # 0. Ensure a test image exists
    if not os.path.exists("test_source.jpg"):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save('test_source.jpg')

    # 1. Register
    print("[1] Registering Identity...")
    res = requests.post(f"{API_URL}/identity/register", json={"username": "TestBot"})
    if res.status_code != 200:
        print(f"[-] Registration Failed: {res.text}")
        return
    print(f"[+] Registration OK: {res.json()}")

    # 2. Sign
    print("[2] Signing Content...")
    files = {'file': open('test_source.jpg', 'rb')}
    data = {'username': 'TestBot'}
    res = requests.post(f"{API_URL}/content/sign", files=files, data=data)
    
    if res.status_code != 200:
        print(f"[-] Signing Failed: {res.text}")
        return
    
    with open("test_signed.jpg", "wb") as f:
        f.write(res.content)
    print(f"[+] Signing OK. Saved to test_signed.jpg (Size: {len(res.content)} bytes)")

    # 3. Verify
    print("[3] Verifying Content...")
    files = {'file': open('test_signed.jpg', 'rb')}
    res = requests.post(f"{API_URL}/content/verify", files=files)
    
    if res.status_code != 200:
        print(f"[-] Verification Request Failed: {res.text}")
        return
    
    verify_data = res.json()
    print(f"[+] Verification Result: {verify_data}")
    
    if verify_data.get("valid") == False and "ManifestNotFound" in str(verify_data):
        print("[-] TEST FAILED: Manifest Missing in Signed File!")
    elif verify_data.get("active_manifest"):
         print("[+] TEST PASSED: Manifest Found!")
    else:
         print("[?] TEST INCONCLUSIVE: Check output above.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Test Error: {e}")
