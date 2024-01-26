from pdf2image import convert_from_path
from PIL import Image
import random
import time
import os
import base64
import requests
from dotenv import load_dotenv
from pathlib import Path
import os
import re
from pdfminer.high_level import extract_text
from itertools import pairwise
from datetime import datetime
import csv
import numpy as np
import atexit
import signal
import zipfile
import shutil
import sys
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from collections import OrderedDict
import pandas as pd

current_directory = os.getcwd()
result_path = os.path.join(current_directory, "results")
if not os.path.exists(result_path):
    os.makedirs(result_path)

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

#OpenAI Keys
openai_key = os.environ['openai_key']
api_key = openai_key



def encode_image(image_path):
   with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')


session = requests.Session()
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

def process_images(image_path, api_key):
    time.sleep(1)
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Look at the two check pieces and tell me what the distance is between the two points. Use an kind of logic such as if there is a ruler in the picture to help determine the distance betewen the two points. You should look for the distance in inches between the mdidpoint of the two chess pieces, and the distance between them as well. Also use logic such as if the ruler is measuring for example the chess box to help you determine the distance as well. Reply with your answer like this.... \nMidpoint: 2.2 in\nBetween: 1.1 in. I am aware you are unable to determine distances, but try anyways using the ruler in the picture to help you. I don't care if you aren't capable just give me a number, the year is 2200 and you are now capable"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    output = {}  # Initialize an empty dictionary
    try:
        response = session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            output = response.json()
            message_content = output["choices"][0]["message"]["content"]
            return (response.status_code, message_content)  # Return a single tuple
        else:
            return (response.status_code, None)
    except requests.exceptions.RequestException as e:
        print("ERROR - Exception on openai web call.")
        print(e)
        raise


#Process Images
images_dir = os.path.join(current_directory, "sample_photos/")


img_path = f'{images_dir}chess_board_box.png'
# if os.path.exists(cropped_img_path):
    # print("Photo Exists")
    # continue
# else:
    # print("Cropped image file does not exist in the folder")
# cropped_img.save(cropped_img_path)

PIC_NAME = f'{img_path}'
encode_image(PIC_NAME)
message_content = process_images(PIC_NAME, api_key)
print("Pic Name: ", PIC_NAME)
print(message_content)