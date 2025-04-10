from waitress import serve
from app import app
import socket

# קבלת כתובת ה-IP של המחשב
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print(f"שרת האפליקציה פועל בכתובת: http://{local_ip}:8080")
print("לחץ Ctrl+C לסגירת השרת")

# הפעלת השרת עם waitress במקום שרת הפיתוח של Flask
serve(app, host='0.0.0.0', port=8080)
