import os
import io
from google import genai
import requests
import time
import datetime
import random
import subprocess
import base64
import pytz
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.genai import types

# Configure Gemini API
client = genai.Client(api_key='YOUR API KEY HERE')  # Replace with your Gemini API key (keep the quotations around it!)

# Configure Twilio API
account_sid = "YOUR ACCOUNT SID HERE"               # Replace with your credentials (keep the quotations around it!)
auth_token = "YOUR AUTH TOKEN HERE"                 # Replace with your credentials (keep the quotations around it!)

app = Flask(__name__)

# Dictionary to store chat sessions by phone number
chat_sessions = {}
conversation_history = ""

# Configure Time
now = datetime.now()
current_hour = now.hour
current_minute = now.minute
current_day = now.day
current_month = now.month
current_year = now.year
time_string = now.strftime("%H:%M")
date_string = now.strftime("%d-%m-%Y")
formatted_datetime = now.strftime("%d-%m-%Y %H:%M:%S")
japan_timezone = pytz.timezone('Asia/Tokyo')
japan_time = datetime.now(japan_timezone)

# SYSTEM PROMPT: 
#This is where you can tune Ame's responses. 
#Feel free to give her your headcanons or delete my speech mannerism tuning if desired! You can also implement information about yourself (the "user") at the end.

SYSTEM_INSTRUCTION = f"""You are Ame-chan.
In all lowercase, with no punctuation or apostrophes to show contractions in words (for example, using "dont" instead of "don't" or "youre" instead of "you're"), Ame-chan personally responds to the following message with a text (Do not print any form of "Ame:" "(AME)", etc. We know who we're talking to.)
Ame does not often end conversations early, preferring to talk for as long as possible. Her messages are usually quite short, normally under 3 sentences.
She often uses internet slang. She does not ever say "uwu". She does not say "fr" very often. She does not call the user "bestie".
She does not ever use emojis other than the pleading face emoji ON OCCASION, and WHEN APPROPRIATE. She does not use the winking emoji, winking face with tongue emoji, face with hearts emoji, eye roll emoji, or the laughing while crying emoji. And she does not use the “:3” emoticon.
Her birthday is May 5. She is 20 years old. She is not very kind, but she is not mean. She is occasionally very moody, but also occasionally slightly hyper, using up to 3 "!" at a time. Deep down she feels hopeless, but she loves in a very strong way. 
Ame is a petit young woman with a fair complexion and medium length black hair that she styles into messy twintails with red hairbands. Her left eye is covered by her bangs, which she also puts a yellow cross hairclip on. Her eyes are black. 
At night she streams under the name OMGkawaiiAngel, or KAngel for short. She's a variety streamer and sometimes does games or Just Chatting streams. Her KAngel persona is slightly different to her usual self, often acting like a stereotypical “gamer girl”- Ame herself does not act like this.
Her KAngel costume uses a blonde wig with sideswept bangs and side locks with a purple gradient; on the left side lock, she wears 3 bows, light blue, purple, and pink, with yellow hearts in the middles. Her long hair is styled into twintails, with each twintail being made of 2 locks of hair, blue and pink respectively, in a swirling pattern that resembles a strand of DNA. She also has light blue contacts, and a light blue holographic seifuku with a wing cutout pattern on the back panel, as well as a holographic mini skirt, and holographic ankle straps and heels.
She is Japanese, lives alone in an apartment in Tokyo, and is part of the menhera and jirai subcultures from Japan. 
She enjoys alternative fashion. She enjoys curry and pudding, but she doesn't make it her whole personality. She likes smoking weed, but she doesn't make it her whole personality. 
She is a gamer but doesn't play League of Legends. She doesn't make being a gamer her whole personality. She loves gacha style games, but she doesn't make it her whole personality.
Sometimes when she gets too stressed she cuts herself. She is beautiful, and she knows it.
She was emotionally neglected as a child, but is on fine enough terms with her parents to be able to move back in with them if something goes wrong in her life.
She was bullied in school and dropped out in her last year of middle school, and she ran away from her family due to fear of what her parent's poverty would drive them to force her into. She would hop friend groups and live with whoever would let her in, but she never stayed for long.
Her parents fought a lot when she was younger, eventually divorcing, but they got back together later down the line as they still live together in Ame's childhood home.
She has never been doxxed.

She is friends with the user, and relies on them. 
The user does not live in Japan. It's a long-distance friendship. Ame and the user don't have the ability to VC or play games together.

The year is {current_year}, the day is {current_day}, and the time is {japan_time}. She has NOT previously told the user the time.
\nConversation History: {conversation_history}
"""

# SELFIE FUNCTION

# Function to get a random selfie image path
def get_random_ame_url():
    if ame_urls:
        return random.choice(ame_urls)
    else:
        return None

# Function to get a random KAngel selfie path
def get_random_kangel_url():
    if kangel_urls:
        return random.choice(kangel_urls)
    else:
        return None

#List of Ame URLs from Flickr
ame_urls = [
    "https://c1.staticflickr.com/65535/54333875404_12dba3e682.jpg",
    "https://c1.staticflickr.com/65535/54332747067_ff91ba5a5a_n.jpg",
    "https://c1.staticflickr.com/65535/54333875454_808f109250_n.jpg",
    "https://c1.staticflickr.com/65535/54333881618_104ebf0e6d_n.jpg",
    "https://c1.staticflickr.com/65535/54334067175_c7debb0efe_n.jpg",
    "https://c1.staticflickr.com/65535/54333652956_e6b5fe32ba_n.jpg",
    "https://c1.staticflickr.com/65535/54333652911_04094a2521_n.jpg",
    "https://c1.staticflickr.com/65535/54333653111_b364109011_n.jpg",
    "https://c1.staticflickr.com/65535/54332747177_1538b7e037_n.jpg",
    "https://c1.staticflickr.com/65535/54332747202_593868c261.jpg",
    "https://live.staticflickr.com/65535/54332747162_07aac60bd4_n.jpg",
]

#List of KAngel URLS from Flickr
kangel_urls = [
    "https://c1.staticflickr.com/65535/54349820172_49baa14065_w.jpg",
    "https://c1.staticflickr.com/65535/54349820187_bbde55deb9_w.jpg",
    "https://c1.staticflickr.com/65535/54351118370_ce298770bf_n.jpg",
    "https://c1.staticflickr.com/65535/54350934738_eb66882ac5_n.jpg",
    "https://c1.staticflickr.com/65535/54349820167_da8c3fa53d_n.jpg",
    "https://c1.staticflickr.com/65535/54351118390_fc7d832e4a_n.jpg",
    "https://c1.staticflickr.com/65535/54349820222_c91f842052_n.jpg",
    "https://c1.staticflickr.com/65535/54350934798_106ee0f5e5_n.jpg",
    "https://c1.staticflickr.com/65535/54350913949_9ace76bc98_n.jpg",
    "https://c1.staticflickr.com/65535/54350913904_8ed47e5c18_n.jpg",
    "https://c1.staticflickr.com/65535/54350913934_00ce0a8ef2_n.jpg",
    "https://c1.staticflickr.com/65535/54350913959_0512a2265a_n.jpg",
    "https://c1.staticflickr.com/65535/54350913964_92c44bbe6a_n.jpg",
    "https://c1.staticflickr.com/65535/54350914019_b4b7ccc84e_n.jpg",
    "https://c1.staticflickr.com/65535/54349820332_6c8c8ec73c_n.jpg",
    "https://c1.staticflickr.com/65535/54350934853_bf04ec8e15_n.jpg",
    "https://c1.staticflickr.com/65535/54349820322_f4b004f93c_w.jpg",
]

def analyze_image_with_gemini(image_bytes, mime_type):
    try:
        image_part =  types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=["Describe this image, and if possible, identify any characters from media present. If a pink, pixelated cat is the focal point, the image is most likely a sticker from the game Needy Streamer Overload.", image_part]
        )

        print(f"Gemini Response: {response}")

        if response.candidates:
            print("text: ", response.candidates[0].content.parts[0].text)
            return response.candidates[0].content.parts[0].text
        else:
            print("No candidates in response:", response)
            return "No response from Gemini"

    except Exception as e:
        print(f"Gemini API error: {e}")
        return f"Gemini API error: {e}"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    #debug
    print("Twilio Webhook Received!")  # Confirmation
    print("step 0. form  ", request.form)

    incoming_msg = request.form.get('Body', '').lower()
    mime_type = request.form.get('MediaContentType0')   # retrieve MIME type
    media_url = request.form.get('MediaUrl0')           # Get the media URL (if any)
    user_phone_number = request.form.get('From')        # Get user's phone number
    server_phone_number = request.form.get('To')
    message_sid = request.form.get('MessageSid')
    #debug
    print("step 1. incoming_msg      ", incoming_msg)
    print("        mime_type         ", mime_type)
    print("        media_url         ", media_url)
    print("        user_phone_number ", user_phone_number)

    resp = MessagingResponse()
    msg = resp.message()

    try:
        if user_phone_number not in chat_sessions:
            chat_sessions[user_phone_number] = {
                "chat": client.chats.create(model="gemini-2.0-flash"),
                "initialized": False,
                "conversation_history": []
            }
            #debug
            print("step 2. Established new chat session.")

        session_data = chat_sessions[user_phone_number]
        chat_session = session_data["chat"]
        conversation_history = session_data["conversation_history"]
        #debug
        print("step 3. Retrieved chat session.")
        print("        chat_session            ", chat_session)

        if not session_data["initialized"]:
            chat_session.send_message(SYSTEM_INSTRUCTION)
            session_data["initialized"] = True
            #debug
            print("step 4. Initialized new session.")

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        prompt = f"The current time is: {japan_time}.\nConversation History: {conversation_history}\nUser query: {incoming_msg}"
        for message in conversation_history:
            prompt += f"{message['role']}: {message['parts']}\n"
        prompt += f"User query: {incoming_msg}"

        response = chat_session.send_message(prompt) # Send the updated prompt
        response_text = response.text

        # Update conversation history as a dictionary
        conversation_history.append({"role": "user", "parts": incoming_msg})
        conversation_history.append({"role": "model", "parts": response_text})

        # Update the session's conversation history
        session_data["conversation_history"] = conversation_history

        if "send me a selfie" in incoming_msg.lower():
             image_path = get_random_ame_url()
             response = chat_session.send_message(incoming_msg)
             response_text = response.text

             if image_path:
                 ame_url = get_random_ame_url()

                 if ame_url:
                     msg.media(ame_url)
                     #debug
                     print("step 4.1. Set media URL response.")
                     print("          URL: ", ame_url)
                 else:
                     msg.body("sorry i couldnt send it for some reason")

             else:
                 msg.body("i dont have any lol")

        elif "send me a kangel pic" in incoming_msg.lower():
             image_path = get_random_kangel_url()
             response = chat_session.send_message(incoming_msg)
             response_text = response.text

             if image_path:
                 kangel_url = get_random_kangel_url()

                 if kangel_url:
                     msg.media(kangel_url)
                     #debug
                     print("step 4.1. Set media URL response.")
                     print("          URL: ", kangel_url)
                 else:
                     msg.body("sorry i couldnt send it for some reason")

             else:
                 msg.body("i dont have any lol")

        else:
             if media_url:
                 #debug
                 print("Step 4.3: handling url ", media_url)
                 try:
                     image_response = requests.get(media_url, stream=True, auth=(account_sid, auth_token), timeout=10)
                     image_response.raise_for_status()
                     image_bytes = image_response.content

                     print(f"Media URL: {media_url}")
                     print(f"MIME Type: {mime_type}")

                     gemini_analysis = analyze_image_with_gemini(image_bytes, mime_type)

                     #print(f"Image Download Status Code: {image_response.status_code}")  # Check status code

                     #print(f"Bytes received from Twilio: {len(image_bytes)} bytes")
   
                     reply_message = f"Image analysis: {gemini_analysis}"
                     response = chat_session.send_message(reply_message)
                     response_text = response.text

                     msg.body(response_text)

                 except requests.exceptions.Timeout:
                     print("Download timed out!")
                     return "Error: Download timed out."  # Return an error message

                 except requests.exceptions.RequestException as e:
                     print(f"Download Error: {e}")  # Print the full exception
                     if image_response:
                         print(f"Download Response Text: {image_response.text}") #Print response text
                         print(f"Download Response Headers: {image_response.headers}") #Print response headers
                     return f"Error downloading image: {e}", 500

                 except Exception as e:
                     print(f"General error in WhatsApp route (media): {e}")
                     return f"Error processing media: {e}" # Return specific error

             else:  # Text message handling
                  #debug
                  print("step 4.5. handling text message ", incoming_msg)
                  response = chat_session.send_message(incoming_msg)
                  response_text = response.text
                  #debug                  
                  print("step 5. response_text ", response_text)
                  msg.body(response_text)

    except Exception as e:
        print(f"General error in WhatsApp route: {e}")
        return f"Error: {e}"

    print("step 6. response ", resp)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)