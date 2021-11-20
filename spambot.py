
import discord
import os
import collections
from discord.ext import commands
import pandas as pd
from csv import DictWriter
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import sys



path = os.getcwd()

model = MultinomialNB(alpha=1)
stemmer = PorterStemmer()

cv = CountVectorizer()
current_guild = ''

try:
    spam =  pd.read_csv(path + "/spam.csv")
except IOError:
    sys.exit("Please run the bot file in the same directory as the spam.csv ")

bot = commands.Bot(command_prefix='!')

spam_db = pd.DataFrame({'v1': spam['v1']})
spam_db = spam_db.join(spam['v2'])
rows = len(spam_db.index)/1.5
spam_db = spam_db.drop(labels=range(0, int(rows)), axis=0)

retrain = False
buffer={}



display_buffer = {}
message_count = {}

l=0
n=0
spammers = []
display_spammer = []

#Finding file and creating if file not there
if(os.path.isfile('./messages.csv') == False):
       d = pd.DataFrame(columns = ['guild_id', 'ham_or_spam', 'message_content'])
       d.to_csv('messages.csv')

db = pd.read_csv('messages.csv')

try:
    with open('tokens.txt', "r") as f:
        token = f.readline()

except IOError:
    sys.exit("Please run the bot file in the same directory as the tokens.txt file")


def retrainer():
    global temporary_df
    global model
    global pred_model
    global retrain
    temporary_df = spam_db
    db = pd.read_csv('messages.csv') 
    for i in range(db.shape[0]):
        if(db.iloc[i]['guild_id']==guild):
            temporary_df = temporary_df.append({'v1':db.iloc[i]['ham_or_spam'], 'v2':db.iloc[i]['message_content']}, ignore_index=True)
            
                 
    temporary_df = temporary_df.replace({"spam": 1, "ham": 0})
    tokenization = [word_tokenize(i) for i in (temporary_df['v2'].values)]
    stemmed = [[stemmer.stem(z) for z in (i)] for i in tokenization]
    temp_final = [' '.join(i) for i in stemmed]
    X = cv.fit_transform(temp_final)
    X.toarray()
    retrain = False  
    pred_model = model.fit(X, temporary_df.v1.values)
    spam_checker(temporary_df['v2'].iloc[-1])
    ans = spam_checker.predict[0]
    if (temporary_df['v1'].iloc[-1] == 1 and ans == 0):
        with open('messages.csv', 'a') as f:
            do = DictWriter(f, ['index', 'guild_id', 'ham_or_spam', 'message_content'])
            do.writerow({'index': db.shape[0], 'guild_id':guild, 'ham_or_spam':'spam' , 'message_content': db['message_content'].iloc[-1]})
        retrainer()

   
    elif (temporary_df['v1'].iloc[-1] == 0 and ans == 1):
        with open('messages.csv', 'a') as f:
            do = DictWriter(f, ['index', 'guild_id', 'ham_or_spam', 'message_content'])
            do.writerow({'index': db.shape[0], 'guild_id':guild, 'ham_or_spam':'ham' , 'message_content': db['message_content'].iloc[-1]})
        retrainer()



    

def spam_checker(msg):
        pred_text = [word_tokenize(i) for i in [msg]]
        pred_text = [[stemmer.stem(z) for z in i] for i in pred_text]
        pred_text = [' '.join(i) for i in pred_text]
        pred_text = cv.transform(pred_text)
        spam_checker.predict = pred_model.predict(pred_text)
        
       

@bot.event
async def on_ready():
     print(f'{bot.user.name} has connected to Discord!')





@bot.event
async def on_message(message):
    

    global l
    global new
    global guild
    global current_guild
    global retrain
    global n
    global temporary_df
    global message_count
  


    

    if(message.author.bot == False):
        guild = message.channel.guild.id

        if(message.content[0:9] != "!spam_add" and message.content[0:13] != "!not_spam_add" and message.content[0:9] != '!bot_help'):
            ''' Changing and retraining model for different guilds '''

            
            if(current_guild==''):
                current_guild = guild
                retrainer()

            if(retrain==True or current_guild!=guild):
                temporary_df = temporary_df[0:0]
                current_guild = guild
                retrainer()


            ''' Checking for any spam messages '''

            msg = message.content
            spam_checker(msg)
            if((spam_checker.predict)[0] == 1):
                try:
                    await message.delete()
                except discord.Forbidden:
                    print("No delete permissions recieved from server, pls give bot deletion permissions in guild {}".format(message.channel.guild))
  
               
        
        


        ''' 
        Repetition spam deletion, add people who spam the same sentence/word/phrase in a short span of messages to a spammer list
        Deletes repeated messages from people who have been marked as spammers
        '''


        total_sum = 0
        if(guild in message_count.keys()):
            message_count[guild] += 1
        else :
            message_count.update({guild : 1})

        for a,b in message_count.items():
            total_sum += b

            if(b >= 8):
                refresh = True
            else:
                refresh = False
                break


        if(refresh==True or total_sum>(len(message_count.keys()) * 8)):
            message_count.clear()
            spammers.clear()
            buffer.clear()
           
        
         

        

    
        if(guild in buffer.keys()):
            if(message.author.id in buffer[guild].keys()):
                buffer[guild][message.author.id].append(message.content)
            else:
                buffer[guild].update({message.author.id : [message.content]})
        else:
            buffer.update({guild : {message.author.id : [message.content]}})
           

        if(l>3):
            l=0
            for k,v in buffer.items():
                for z,y in v.items():
                    freq = collections.Counter(y)
                    max_freq = max(zip(freq.values(), freq.keys()))
                    mf = max_freq[0]
                    # checks if a same message has been repeated more than 3 times
                    if ((mf > 3 or len(set(y)) == 1)) or (len(set(y)) == 2 and len(v.keys())>1): 
                        spammers.append(z)
                        
                   
        else:
            l+=1
            
                        


        if(message.author.id in spammers and message.content in buffer[guild][message.author.id]):
            c = 0
            for i in range(len(buffer[guild][message.author.id])):
             if(buffer[guild][message.author.id][i] == message.content):
                 c+=1
            if(c > 2):
              try:
                await message.delete()
              except discord.Forbidden:
                print("No delete permissions recieved from server, pls give bot deletion permissions in guild : {}".format(message.channel.guild))

    await bot.process_commands(message)
    n +=1
   

'''Adding spam messages to the spam database'''
@bot.command()
async def spam_add(ctx, *,arg):
    global retrain
    name = ctx.guild.id
    with open('messages.csv', 'a') as f:
        do = DictWriter(f, ['index', 'guild_id', 'ham_or_spam', 'message_content'])
        do.writerow({'index': db.shape[0], 'guild_id':name, 'ham_or_spam':'spam' , 'message_content':arg})
    retrain = True
   


'''Adding non spam messages to the spam database'''
@bot.command()
async def not_spam_add(ctx, *,arg):
    global retrain
    name = ctx.guild.id
    with open('messages.csv', 'a') as f:
        do = DictWriter(f, ['index', 'guild_id', 'ham_or_spam', 'message_content'])
        do.writerow({'index': db.shape[0], 'guild_id':name, 'ham_or_spam':'ham', 'message_content':arg})
    retrain = True
    
     


@bot.command()
async def bot_help(ctx):
    embed = discord.Embed(title = 'Bot help', description="This embed shows u how to add spam and non spam mesages to the bot")
    embed.add_field(name='Adding spam messages', value='Use !spam_add to add messages u think are spam')
    embed.add_field(name='Adding non spam mesages', value='If u want to mark a message as not spam use !not_spam_add')
    embed.add_field(name="Warning", value = "Please refrain from adding common terms to the bot database as it will delete messages that are similar or contain those terms")
    await ctx.send(embed=embed)





bot.run(token)



