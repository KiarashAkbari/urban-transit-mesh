import os
import requests
import sys

def broadcast_to_telegram():
    # In GitHub Actions, these will be pulled from environment variables (Secrets)
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        print("Error: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables.")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_path = os.path.join(base_dir, "alert_map.png")
    html_path = os.path.join(base_dir, "mesh_map_offline.html")

    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"

    # 1. Send the Snapshot Image
    print("Uploading visual snapshot to Telegram...")
    
    bilingual_image_caption = (
        "🔴 وضعیت شبکه ترانزیت ملی | National Transit Mesh Status\n\n"
        "نقشه تصویری با کیفیت بالا پیوست شده است. برای استفاده از نقشه تعاملی بدون نیاز به اینترنت، فایل HTML زیر را دانلود کنید.\n"
        "High-res visual attached. For the interactive offline map, download the HTML document below.\n\n"
        "🆔 @irantransitmesh"
    )

    try:
        with open(image_path, 'rb') as photo:
            response = requests.post(
                f"{base_url}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "caption": bilingual_image_caption
                },
                files={"photo": photo},
                timeout=30
            )
            response.raise_for_status()
            print("Snapshot uploaded successfully.")
    except Exception as e:
        print(f"Failed to send photo: {e}")

    # 2. Send the Offline HTML File
    print("Uploading offline HTML mesh...")
    
    bilingual_doc_caption = (
        "📥 نقشه آفلاین و تعاملی (بدون نیاز به اینترنت)\n"
        "فایل را دانلود کرده و در هر مرورگری باز کنید.\n\n"
        "📥 Interactive Offline Map (No Internet Required)\n"
        "Download the file and open it in any browser.\n\n"
        "🆔 @irantransitmesh"
    )

    try:
        with open(html_path, 'rb') as document:
            response = requests.post(
                f"{base_url}/sendDocument",
                data={
                    "chat_id": CHAT_ID,
                    "caption": bilingual_doc_caption
                },
                files={"document": document},
                timeout=30
            )
            response.raise_for_status()
            print("HTML Document uploaded successfully.")
    except Exception as e:
        print(f"Failed to send document: {e}")

if __name__ == "__main__":
    broadcast_to_telegram()
