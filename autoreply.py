import requests, pickle, sys, time, random
from bs4 import BeautifulSoup
import dateparser
from datetime import datetime
import logging
from fb_login_config import *
import argparse

def sendreply(url, name):
  #go to message page
  response = s.get('https://mbasic.facebook.com{}'.format(url), headers=headers)
  #skip if already had auto reply
  if check_text in response.text: 
    logger.warning("{} already had autoreply".format(name))
    replies.append(url)
    with open('replied.pickle', 'wb') as f:
      pickle.dump(replies, f)
  else: #send reply
    soup = BeautifulSoup(response.text, features="html.parser")
    data = {}
    form = soup.find("form", id="composer_form")
    for h in form.findAll("input"):
      if h.attrs['type']=="hidden":
        try:
          data[h.attrs['name']] = h.attrs['value']
        except:
          pass
    data.update({
      'body': reply_message,
      'send': 'Send',
      'referrer': '',
      'ctype': '',
    })
    #post reply
    response = s.post('https://mbasic.facebook.com{}'.format(form.attrs['action']), headers=headers, data=data)
    replies.append(url)
    with open('replied.pickle', 'wb') as f:
      pickle.dump(replies, f)
    logger.warning("Sent message to {}".format(name))
  return

def login():
  ls = requests.Session() 
  response = ls.get('https://mbasic.facebook.com/', headers=headers)
  soup = BeautifulSoup(response.text, features="html.parser")
  form = soup.find("form")
  data = {}
  for h in form.findAll("input"):#load hidden fields for login
    if h.attrs['type']=="hidden":
      for n in ['lsd', 'jazoest', 'm_ts', 'li']:
        if h.attrs['name']==n: data[n] = h.attrs['value']
  data.update({
    'try_number': '0',
    'unrecognized_tries': '0',
    'email': username,
    'pass': password,
    'login': 'Log In'
  })
  resp = ls.post('https://mbasic.facebook.com{}'.format(form.attrs['action']), headers=headers, data=data)
  if "Search Facebook" in resp.text:
    logger.warning("Logged in OK")
    s.cookies.clear() #clear all existing cookies
    s.cookies.update(ls.cookies) #update main script client with new cookie
    with open('fbcookie.pickle', 'wb') as f:
      pickle.dump(ls.cookies, f)     
  else:
    logger.warning("Cannot log in - try logging in at https://mbasic.facebook.com/ to see if account blocked")
  return


if __name__ == "__main__":
  #parse swtiches
  parser = argparse.ArgumentParser()
  parser.add_argument("--debug", action="store_true")
  args = parser.parse_args()
    
  
  # create logger
  logger = logging.getLogger("logging")
  if args.debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.WARNING)
  # create console handler and set level to debug
  ch = logging.StreamHandler()
  ch.setLevel(logging.DEBUG)
  # create formatter
  formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
  # add formatter to ch
  ch.setFormatter(formatter)
  # add ch to logger
  logger.addHandler(ch)

  s = requests.Session() 
  #load cookies
  try:
    with open('fbcookie.pickle', 'rb') as f:
      s.cookies.update(pickle.load(f))
  except:
    pass
  
  #load reply file
  try:
    with open('replied.pickle', 'rb') as f:
      replies = pickle.load(f)
  except:
    replies = []


  headers = {
      'authority': 'mbasic.facebook.com',
      'pragma': 'no-cache',
      'cache-control': 'no-cache',
      'dnt': '1',
      'upgrade-insecure-requests': '1',
      'user-agent': random.choice(user_agents),
      'sec-fetch-dest': 'document',
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'sec-fetch-site': 'none',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-user': '?1',
      'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  }
  while True:
    #get list of messages every 5 minutes
    murl = 'https://mbasic.facebook.com/messages/'
    if random.randint(1,10) == 1: #1 in 10 chance of checking filtered mailbox (help bot detection avoidance)
      murl += '?folder=pending'
    logger.debug("Retrieving {}".format(murl))
    response = s.get(murl, headers=headers)
    #get message requests
    if "Phone number or email address" in response.text:#not logged in
      logger.warning("Not logged in")
      #login again
      login()
    else:
      if 'Search for messages' in response.text:
        logger.debug("Checking messages")
        soup = BeautifulSoup(response.text, features="html.parser")
        tables = soup.findAll("table")
        for t in tables: #loop through each message in messenger home page
          try:
            user = t.find("h3").find("a")
            #user.attrs['href'] 
            #/messages/read/?tid=cid.c.[friendid]:[myid] or
            #/messages/read/?tid=cid.c.[myid]:[friendid]
          except: #not a message table so loop to next message
            continue
          
          #find time last message sent
          abbr = t.find("abbr")
          time_diff = (datetime.now() - dateparser.parse(abbr.text)).total_seconds()
          #only send replies if in last hour, not in ignore list and not already sent message
          if time_diff < (1*3600):
            logger.debug("Message found that needs reply {}".format(user.attrs['href']))
            if user.text not in ignore_list:
              if user.attrs['href'] not in replies:
                logger.debug("Sending reply")
                sendreply(user.attrs['href'], user.text)
              else:
                logger.debug("Already replied to {}".format(user.attrs['href']))
            else:
              logger.debug("Ignoring user {} as in ignore list".format(user.text))
      else:
        logger.warning("Cannot retrieve messages page- relogging in")
        #login again
        login()
            
      
    sleeptime = random.randint(250, 400)
    logger.debug("Sleeping for {}s".format(sleeptime))
    time.sleep(sleeptime)
