import grcconf as g
import emotes as e
import discord

def help_main():
    acc = 'Type %help [topic] for more detailed information about the following:\n'
    for topic in help_dict:
        acc += '- {}\n'.format(topic)
    return acc

new = discord.Embed(title='Create a new account: %new', colour=discord.Colour.yellow(),
description='''
An account is required to use the bot. (No personal details required)
Be sure to also read the %rules and %terms.''')

bal = discord.Embed(title='Check your balance: %bal %balance', colour=discord.Colour.yellow(),
description='''
Checks your current balance and shows your deposit address.
To get a clipboard friendly address, use %addr.
Deposits should arrive within 5 minutes of a transaction taking place.
If the bot is offline, you are still safe to make deposits.''')

wdr = discord.Embed(title='Withdraw your funds: %wdr %withdraw %send', colour=discord.Colour.yellow(),
description='''
**Format: %wdr [address to send to] [amount-GRC]**

Takes your GRC out of the bot's wallet.
Fee for withdraw is {} GRC and is automatically deducted.
If you wish to transfer to another user, use %give instead.'''.format(g.tx_fee))

donate = discord.Embed(title='Donate to someone: %donate', colour=discord.Colour.yellow(),
description='''
Format: %donate [selection no.] [amount-GRC]

Type just %donate to see a list of possible donation options.
Choose a number from the list of selections and then choose the amount to donate.
Fees here are regular network fees.''')

rdonate = discord.Embed(title='Donate to a random contributor: %rdonate', colour=discord.Colour.yellow(),
description='''
Format: %rdonate [amount-GRC]

Same as %donate but a random person on the bot's donation list is chosen for you.''')

give = discord.Embed(title='Give funds to another user: %give %tip', colour=discord.Colour.yellow(),
description='''
Format: %give [discord mention of user] [amount-GRC]

Give some GRC to another person within the server. (no fees apply)
Requires the mentioned user to also have an account with the bot through %new.''')

rain = discord.Embed(title='Rain on active users: %rain', colour=discord.Colour.yellow(),
description='''
Format: %rain [amount-GRC]

Typing %rain on its own will display the current rain balance and threshold.
Once the balance of the rainbot exceeds the threshold, it will rain on all **online** users.''')


faucet = discord.Embed(title='Get some free GRC: %faucet %get', colour=discord.Colour.yellow(),
description='''
Type this command to get some free Gridcoins.
Amounts are random and you can only request once per {} hours.
To help fund the faucet, you can type `%fgive [amount-GRC]`.'''.format(g.FCT_REQ_LIM))

qr = discord.Embed(title='Generate a QR code: %qr', colour=discord.Colour.yellow(),
description='''
Format: %qr [optional data]

Generates a qr code. If no data is given, it will send a QR code of your
wallet address. Any data given must contain no spaces.''')

faq = discord.Embed(title='Read answers to frequently asked questions: %faq', colour=discord.Colour.yellow(),
description='''
Format: %faq [selection no.]

All answers are formulated by Delta, Foxifi and LavRadis, and checked by
community members and developers.''')

block = discord.Embed(title='Explore blocks on the Gridcoin network: %block', colour=discord.Colour.yellow(),
description='''
Format: %block [height]

Fetches information about a particular block on the Gridcoin blockchain.''')

status = discord.Embed(title='Bot and network status: %status', colour=discord.Colour.yellow(),
description='''
Check the bot status to see whether it is online and observe some basic stats.''')

time = discord.Embed(title='Show your timeouts: %time', colour=discord.Colour.yellow(),
description='''
Shows faucet, withdrawal and donation availability and time until eligibility.''')

rules_help = discord.Embed(title='Show the bot rules: %rules', colour=discord.Colour.yellow(),
description='''
Rules about using the bot and what may result in a ban.''')

terms_help = discord.Embed(title='Show the bot terms: %terms', colour=discord.Colour.yellow(),
description='''
Terms and conditions for making an account with the bot that you automatically accept by typing %new.''')

info_help = discord.Embed(title='Information about the bot: %info', colour=discord.Colour.yellow(),
description='''
Shows information about authors and contributors.''')

info = discord.Embed(title='This bot is the original work of Delta and various contributors.', colour=discord.Colour.yellow(),
description='''
The source code for the bot can be found [here](https://github.com/delta1512/GRC-Wallet-Bot).

If there are any problems, glitches or crashes, please notify me or the contributors below as soon as possible. Any queries can be sent to `boincosdelta@gmail.com`.

Notable mentions:
- [Jorkermc](https://github.com/jorkermc)
- Nathanielcwm
- Foxifi
- [LavRadis](https://steemit.com/@lavradis)
''')

help_dict = {
    'new'       :   new,
    'balance'   :   bal,
    'withdraw'  :   wdr,
    'donate'    :   donate,
    'rdonate'   :   rdonate,
    'give'      :   give,
    'rain'      :   rain,
    'faucet'    :   faucet,
    'qr'        :   qr,
    'faq'       :   faq,
    'block'     :   block,
    'status'    :   status,
    'time'      :   time,
    'rules'     :   rules_help,
    'terms'     :   terms_help,
    'info'      :   info_help
}
