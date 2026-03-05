import json
import os
import sys

def convert_json_to_netscape(json_file, output_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        cookies = data.get('cookies', [])
        
        with open(output_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# http://curl.haxx.se/rfc/cookie_spec.html\n")
            f.write("# This is a generated file!  Do not edit.\n\n")
            
            for cookie in cookies:
                # domain, flag, path, secure, expiration, name, value
                domain = cookie.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = cookie.get('path', '/')
                secure = "TRUE" if cookie.get('secure', False) else "FALSE"
                expiration = int(cookie.get('expirationDate', 0))
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
        
        print(f"Successfully converted {json_file} to {output_file}")
    except Exception as e:
        print(f"Error converting cookies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Find the JSON file provided by the user
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'youtube' in f.lower()]
    if not json_files:
        print("No YouTube cookie JSON file found.")
        sys.exit(1)
    
    # Use the most recent one if multiple (though likely only one)
    json_file = json_files[0]
    convert_json_to_netscape(json_file, 'cookies.txt')
