# Telegram News Chatbot

This telegram chatbot created as a final project for subject `CPE641 Natural Language Processing` course at KMUTT.

This chatbot allow users to query about news with the certain given topic. Then it returns news that similar to given keywords.

This bot's whole repository is created within 5 days, as a result, bare with me if code is really mess, buggy or really hard to understand.

For detail, [This report](NLP Report.pdf) explained about the methodology, architecture and implementation.

## Instruction (for now)
```sh
# git clone this project, then
$ npm install
$ pip install -r requirements.txt

# now, create another console for run two services

# first console, for the telegram connector service
$ node app.js

# second console, for news crawler and bot processor
$ python server.py
```

## Todo
- dockerize this project
- manage the dependencies for python part
