# facebook_messenger_autoreply
Python 3.x script to autoreply to personal Facebook messenger

## Requirements

Python 3.x

pip install dateparser pickle requests bs4

## Installation

Adjust autoreply message and log in details in fb_login_config.py
  
Run as python autoreply.py

## Mode of action

Will scan all messages in inbox and in "filtered" mailbox approx every 5mins.

Will send message defined in $reply_message to those people who have 
1. sent a message in previous hour and
2. have not had autoreply message and 
3. do not have keywords in conversation history (in $check_text string variable) and
4. whose name is not in ignore_list

## Troubleshooting

Make sure script can write facebook login cookie and replied file in same directory

Set logger.setLevel(logging.DEBUG) for more output

If it can't log in Facebook may be blocking as it's from a different location/ different user agent; sign in to Facebook on a PC and allow the login

Do not reduce the scan wait time- hammering the FB servers will definitely result in a block!
