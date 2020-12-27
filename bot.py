#!/usr/bin/env python
import sys
import re
import json
import telebot
import requests
from time import time, localtime, strftime, sleep
import nltk
import config

assert sys.version_info > (3,6)

bot = telebot.TeleBot(config.bot_token)

wordmap = {}
with open("data.json","r") as f:
  data = json.load(f)
for r in data:
  suggest = [r["suggest"], r["link"]]
  for w in r["triggers"]:
    wordmap[w] = suggest

# python 3.6+ required to preserve order of list items
def unique(l):
  return list(dict.fromkeys(l))

@bot.message_handler(content_types=['text'])
def trigger_message(message):
  msg = message.text
  print ("%s|%s <%s %s> %s" % (str(message.chat.id), strftime("%Y-%m-%d %H:%M:%S", localtime(message.date)), message.from_user.first_name, message.from_user.last_name, msg))
  if time() > message.date+config.max_timediff:
    print (" message time too old :(")
    return
  words = unique(nltk.word_tokenize(msg))
  print (words)
  suggests = []
  for w in words:
    try:
      suggest = wordmap[w.lower()]
    except KeyError:
      continue
    suggests.append([w,suggest[0],suggest[1]])
  if len(suggests) > 0:
    suggest_msg = "\n\n".join(map(lambda x:f"*{x[0]}* yerinə [{x[1]}]({x[2]}) demək olar", suggests))
    print (suggest_msg)
    bot.send_message(message.chat.id, suggest_msg, reply_to_message_id=message.message_id, parse_mode="Markdown", disable_web_page_preview=True)

while True:
  try:
    bot.polling()
  except requests.exceptions.ConnectionError:
    print (" ConnectionError exception occured while polling, restart in 1 second...")
    sleep(1)
    continue
  except telebot.apihelper.ApiException:
    print (" ApiException exception occured while polling, restart in 1 second...")
    sleep(1)
    continue
  except requests.exceptions.ReadTimeout:
    print (" ReadTimeout exception occured while polling, restart in 1 second...")
    sleep(1)
    continue
