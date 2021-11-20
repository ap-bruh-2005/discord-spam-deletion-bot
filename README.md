# Discord spam deletion bot

This bot deletes spam messages on discord. These spam messages can be added to the database using a discord bot command. The bot also deletes messages similar to those added to the database and messages that are constantly repeated. People who spam are tagged as spammers and all the messages that are repeated by them are deleted until they are untagged after a certain amount of messages. 
Note : If you find any bugs please let me know, since i am a novice. Thanks.


## How to run the bot 

First check if you have the required packages in requirements.txt. If you don't then install all the required packages. This can be done using pip. 

After installation go to discord developer portal (The link is given below) and login to your account:
https://discord.com/developers/docs/intro

When you are in the portal create a new Application and click on that application. Then click on Bot under settings and copy the token. Paste that token in the tokens.txt file. When you want to run the bot, run the file spambot.py after pasting that token. Add the bot to all the server you want it in.
``` 
cd <Path to the directory all the files are in> (for example : cd Desktop)
python spambot.py

```

## Usage

To check the bot for help in discord do :
```
!bot_help 
```
To add a spam message to the database do :
```
!spam_add <message u need to mark as spam >
# for example : !spam_add hello 

```

To add a non spam message to make sure that it isnt deleted do:

```
!not_spam_add <message you need to mark as not spam>
# for example : !not_spam_add hello
```
## Contributing

Pull requests to solve issues and make changes are more than welcome. 
