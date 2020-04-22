import requests, pickle, sys, time, random
from bs4 import BeautifulSoup
import dateparser
from datetime import datetime
import logging

#pip install dateparser pickle requests bs4

username = 'FACEBOOK USER NAME'
password = 'FACEBOOK PASSWORD'
reply_message = 'Autoreply: Thanks for getting in touch. I'll get back to you asap'
#will check previous messages - if finds this text will not reply (set to None without quotes to ignore)
check_text = 'Thanks for getting in touch'
#check_text = None
#list of names of people not to auto reply to
ignore_list = [
  'John Smith',
  ]

#will select a randowm user agent to use - adjust as necessary; comment to only leave 1 device agent if Fb keeps blocking
user_agents = [
  #'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
  #'Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; SCH-I535 Build/KOT49H) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
  #'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36',
  #'Mozilla/5.0 (Linux; Android 7.0; SM-A310F Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36 OPR/42.7.2246.114996',
  #'Opera/9.80 (Android 4.1.2; Linux; Opera Mobi/ADR-1305251841) Presto/2.11.355 Version/12.10',
  #'Opera/9.80 (J2ME/MIDP; Opera Mini/5.1.21214/28.2725; U; ru) Presto/2.8.119 Version/11.10',
  #'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) OPiOS/10.2.0.93022 Mobile/11D257 Safari/9537.53',
  #'Mozilla/5.0 (Android 7.0; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0',
  #'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) FxiOS/7.5b3349 Mobile/14F89 Safari/603.2.4',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
  ]

### alter below this line at your own risk ###

def sendreply(url, name):
  #go to message page
  response = s.get('https://mbasic.facebook.com{}'.format(url), headers=headers)
  #skip if already had auto reply
  if check_text in response.text: 
    logger.debug("{} already had autoreply".format(name))
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
    logger.debug("Sent message to {}".format(name))
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
    logger.debug("Logged in OK")
    with open('fbcookie.pickle', 'wb') as f:
      pickle.dump(ls.cookies, f)     
  else:
    logger.debug("Cannot log in - try logging in at https://mbasic.facebook.com/ to see if account blocked")
  return


if __name__ == "__main__":
  # create logger
  logger = logging.getLogger("logging")
  logger.setLevel(logging.DEBUG)
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
    for murl in ['https://mbasic.facebook.com/messages/','https://mbasic.facebook.com/messages/?folder=pending']:
      logger.debug("Retrieving {}".format(murl))
      response = s.get(murl, headers=headers)
      #get message requests
      if "Phone number or email address" in response.text:#not logged in
        logger.debug("Not logged in")
        #login again
        login()
        break
      else:
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
          if time_diff < 3600 and user.text not in ignore_list and user.attrs['href'] not in replies:
            sendreply(user.attrs['href'], user.text)
            
      time.sleep(random.randint(5, 20))
      
    sleeptime = random.randint(250, 400)
    logger.debug("Sleeping for {}s".format(sleeptime))
    time.sleep(sleeptime)
