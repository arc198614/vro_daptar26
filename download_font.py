import urllib.request
import ssl
import os

def download_font():
    urls = [
        ("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf", "NotoSansDevanagari-Regular.ttf"),
        ("https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf", "NotoSansDevanagari-Regular.ttf")
    ]
    
    context = ssl._create_unverified_context()
    
    for url, filename in urls:
        print(f"Trying {url}...")
        try:
            with urllib.request.urlopen(url, context=context) as response, open(filename, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            print(f"Success! Saved to {filename}")
            return filename
        except Exception as e:
            print(f"Failed: {e}")
            if os.path.exists(filename):
                os.remove(filename)
    return None

if __name__ == "__main__":
    download_font()
