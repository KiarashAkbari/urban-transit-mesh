import os
import requests
from bs4 import BeautifulSoup

def make_html_offline(input_file, output_file):
    print(f"Reading base map: {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. Inline all CSS stylesheets
    print("Inlining CSS dependencies...")
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href and href.startswith('http'):
            print(f"  -> Downloading CSS: {href}")
            try:
                response = requests.get(href, timeout=10)
                response.raise_for_status()
                
                # Create a new <style> tag with the raw CSS content
                style_tag = soup.new_tag('style')
                style_tag.string = response.text
                link.replace_with(style_tag)
            except Exception as e:
                print(f"  [!] Failed to download {href}: {e}")

    # 2. Inline all JavaScript dependencies
    print("Inlining JavaScript dependencies...")
    for script in soup.find_all('script', src=True):
        src = script.get('src')
        if src and src.startswith('http'):
            print(f"  -> Downloading JS: {src}")
            try:
                response = requests.get(src, timeout=10)
                response.raise_for_status()
                
                # Create a new <script> tag with the raw JS content
                new_script = soup.new_tag('script')
                new_script.string = response.text
                script.replace_with(new_script)
            except Exception as e:
                print(f"  [!] Failed to download {src}: {e}")

    # Save the monolithic offline HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"\nSuccess! Offline map generated: {output_file}")

if __name__ == "__main__":
    # In production, these paths will be relative to the GitHub Actions workspace
    make_html_offline("mesh_map_base.html", "mesh_map_offline.html")
