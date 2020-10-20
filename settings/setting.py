from dotenv import load_dotenv
import os

load_dotenv()

PUSH_API_TOKEN = os.environ.get("PUSH_API_TOKEN")
RECEIVER_NO = os.environ.get("RECIEVER_NO")
SENDER_NO = os.environ.get("SENDER_NO")
DEVICE_ID = os.environ.get("DEVICE_ID")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
RECEIVER_EMAIL = os.environ.get("RECIEVER_EMAIL")
RECEIVER_EMAIL2 = os.environ.get("RECIEVER_EMAIL2")

