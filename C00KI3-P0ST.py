import requests
import time
import json
import re
import threading
import http.server
import socketserver
import random

# File paths
COOKIES_FILE = "cookies.txt"
COMMENTS_FILE = "file.txt"
POST_ID_FILE = "post.txt"
NAME_FILE = "name.txt"
SPEED_FILE = "speed.txt"
PROXIES_FILE = "proxies.txt"

# Load proxies from file
def load_proxies():
    try:
        with open(PROXIES_FILE, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("[ERROR] Proxies file not found!")
        return []

# Get a random proxy from the list
def get_random_proxy():
    proxies = load_proxies()
    if proxies:
        proxy = random.choice(proxies)
        return {"http": proxy, "https": proxy}
    return None

# Server Handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Facebook Auto Comment Bot Running!")

def execute_server():
    PORT = 8000
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Server running on port {PORT}")
        httpd.serve_forever()

# Read cookies from file
def read_cookie():
    try:
        with open(COOKIES_FILE, "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("[ERROR] Cookies file not found!")
        return []

# Make a request to Facebook
def make_request(url, headers, cookies):
    try:
        proxy = get_random_proxy()  # Select random proxy
        response = requests.get(url, headers=headers, cookies={'cookie': cookies}, proxies=proxy)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None

# Extract Facebook Access Token
def extract_token(response):
    match = re.search(r"(EAAG\w+)", response)
    return match.group(1) if match else None

# Main function to post comments
def mafiya():
    cookies_list = read_cookie()
    valid_cookies = []
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 11; Mobile Safari/537.36)"}

    print("[INFO] Checking valid cookies...")
    for cookie in cookies_list:
        response = make_request("https://business.facebook.com/business_locations", headers, cookie)
        if response and "EAAG" in response:
            token = extract_token(response)
            if token:
                valid_cookies.append((cookie, token))

    if not valid_cookies:
        print("[!] No valid cookies found. Exiting...")
        return

    # Load required data
    with open(POST_ID_FILE, "r") as f:
        post_id = f.readline().strip()
    
    with open(NAME_FILE, "r") as f:
        commenter_name = f.readline().strip()

    with open(SPEED_FILE, "r") as f:
        delay = int(f.readline().strip())

    with open(COMMENTS_FILE, "r") as f:
        comments = f.readlines()

    x, y, cookie_index = 0, 0, 0

    while True:
        time.sleep(delay)
        comment_text = comments[x].strip()
        comment_with_name = f"{commenter_name}: {comment_text}"

        current_cookie, access_token = valid_cookies[cookie_index]
        data = {"message": comment_with_name, "access_token": access_token}

        # Post comment
        try:
            proxy = get_random_proxy()  # Select random proxy for every request
            response = requests.post(
                f"https://graph.facebook.com/{post_id}/comments/",
                data=data,
                headers={"Cookie": current_cookie},
                proxies=proxy
            ).json()

            current_time = time.strftime("%Y-%m-%d %I:%M:%S %p")

            if "id" in response:
                print(f"\033[1;32m[Success] Comment posted at {current_time}")
            else
