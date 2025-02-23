
˚ʚ♡ɞ˚  This is the source code for a WhatsApp chatbot that emulates Ame-chan from the game Needy Streamer Overload (available on Steam). 

NOTE: Ame is still in developmental stages, meaning YOU need to run her locally, on YOUR PC with YOUR accounts.
			
˚ʚ♡ɞ˚  Big thank-you to lutfi (https://amiritefellas.tumblr.com/) for helping me start this project right, and for occasional corrections. This could not be possible without lutfi!

˚ʚ♡ɞ˚  Current features:
ability to chat in-character
ability to send a picture of herself (from 10 options) with the prompt "send me a selfie"

NOTE: Ame does not see images yet. If you send her an image you will get no response. It can also BREAK the following responses and you will need to restart the program.

˚ʚ♡ɞ˚ How to use (ALL FREE): 
Download ngrok (https://ngrok.com/) 
Download Python (https://www.python.org) 
Create a Twilio account (https://www.twilio.com/en-us) 
Run ame.py
Run ngrok and type in “ngrok http 5000”
Copy the link next to “Forwarding” (it should look like, for example, “https://f79b-91-166-41-200.ngrok-free.app”)
Navigate to the Twilio Console’s “Messaging” tab, then Try it out > Send a WhatsApp message
Follow the directions to connect to the sandbox.
Navigate to Sandbox Settings and paste your ngrok link into “When a message comes in”, then add “/whatsapp” to the end of your link. Make sure the method is set to POST. 
Don’t worry about “Status callback URL”.
Click Save.
Send a message!
