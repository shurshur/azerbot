#!/usr/bin/env python
import sys
import re
import json
import telebot
import requests
from time import time, localtime, strftime, sleep
import nltk
from stemmer.stemmer import Stemmer
import config

assert sys.version_info > (3,6)

stemmer = Stemmer()

bot = telebot.TeleBot(config.bot_token, skip_pending=True, threaded=False)

wordmap = {}
with open("data.json","r") as f:
  data = json.load(f)
for r in data:
  for w in r["triggers"]:
    wordmap[w] = r["suggests"]

# python 3.6+ required to preserve order of list items
def unique(l):
  return list(dict.fromkeys(l))

@bot.message_handler(commands=['help','start'])
def welcome_message(message):
  if message.chat.type != 'private': return
  msg = """Salam. Bu bot dilimizin varlığını qorumaq üçündür. Bu botu söhbət qruplara salıb, bəzi alınma sözlərinin doğma qarşılığı öyrənə bilərsiniz. Bot alınma sözləri görüb, öz sözlərimizi işlətməyə təklif edəcək. Bunun üçün botu admin eyləmək gərək deyil, sadəcə qrupa qoşun.

Botdakı qarşılıqlar @azerbaycan_turki kanalın #azerbaycan_purizm həştəqli paylaşımlar əsasındadır."""
  bot.send_message(message.chat.id, msg)

@bot.message_handler(content_types=['text'])
def trigger_message(message):
  msg = message.text
  print ("%s|%s|%s|%s <%s %s> %s" % (message.chat.type, str(message.chat.id), message.chat.title, strftime("%Y-%m-%d %H:%M:%S", localtime(message.date)), message.from_user.first_name, message.from_user.last_name, msg))
  if time() > message.date+config.max_timediff:
    print (" message time too old :(")
    return
  words = unique(nltk.word_tokenize(msg, 'turkish'))
  suggests = {}
  for w in words:
    try:
      # stemmer.stem_word is useless for us :(
      try:
        sw = stemmer.stem_words([w])[0].lower()
      except RecursionError:
        print ("Stemmer throws RecursionError, skip message")
        return
      word_suggests = wordmap[sw]
    except KeyError:
      continue
    suggests[sw] = word_suggests
  if len(suggests) > 0:
    suggest_text_arr = []
    for w, suggest_arr in suggests.items():
      single_suggest_text_arr = []
      for ss in suggest_arr:
        single_suggest_text_arr.append(f"[{ss['text']}]({ss['link']})")
      single_suggest_text = "; ".join(single_suggest_text_arr)
      suggest_text_arr.append(f"*{w}* yerinə {single_suggest_text} demək olar")
    suggest_msg = "\n\n".join(suggest_text_arr)
    suggest_msg_out = suggest_msg.replace('\n','\n      ').replace('\n      \n','\n\n')
    print (f" `--> {suggest_msg_out}")
    bot.send_message(message.chat.id, suggest_msg, reply_to_message_id=message.message_id, parse_mode="Markdown", disable_web_page_preview=True)

while True:
  try:
    bot.polling(none_stop=True)
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
