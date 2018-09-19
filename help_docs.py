import grcconf as g
import emotes as e
import discord

def help_main():
    topics = '\n'.join(f'- {topic}' for topic in help_dict)
    return discord.Embed(
        title='GRC Wallet Bot Help',
        colour=discord.Colour.orange(),
        description=f'''
Type `%help [topic]` for more detailed information about the following:

{topics}
''')

new = discord.Embed(title='Create a new account: %new', colour=discord.Colour.orange(),
description='''
An account is required to use the bot. (No personal details required)
Be sure to also read the %rules and %terms.''')

bal = discord.Embed(title='Check your balance: %bal %balance', colour=discord.Colour.orange(),
description='''
Checks your current balance and shows your deposit address.
To get a clipboard friendly address, use %addr.
Deposits should arrive within 5 minutes of a transaction taking place.
If the bot is offline, you are still safe to make deposits.''')

wdr = discord.Embed(title='Withdraw your funds: %wdr %withdraw %send', colour=discord.Colour.orange(),
description=f'''
**Format: %wdr [address to send to] [amount-GRC]**

Takes your GRC out of the bot's wallet.
Fee for withdraw is {g.tx_fee} GRC and is automatically deducted.
If you wish to transfer to another user, use %give instead.''')

donate = discord.Embed(title='Donate to someone: %donate', colour=discord.Colour.orange(),
description='''
Format: %donate [selection no.] [amount-GRC]

Type just %donate to see a list of possible donation options.
Choose a number from the list of selections and then choose the amount to donate.
Fees here are regular network fees.''')

rdonate = discord.Embed(title='Donate to a random contributor: %rdonate', colour=discord.Colour.orange(),
description='''
Format: %rdonate [amount-GRC]

Same as %donate but a random person on the bot's donation list is chosen for you.''')

give = discord.Embed(title='Give funds to another user: %give %tip', colour=discord.Colour.orange(),
description='''
Format: %give [discord mention of user] [amount-GRC]

Give some GRC to another person within the server. (no fees apply)
Requires the mentioned user to also have an account with the bot through %new.''')

rain = discord.Embed(title='Rain on active users: %rain', colour=discord.Colour.orange(),
description='''
Format: %rain [amount-GRC]

Typing %rain on its own will display the current rain balance and threshold.
Once the balance of the rainbot exceeds the threshold, it will rain on all **online** users.''')

faucet = discord.Embed(title='Get some free GRC: %faucet %get %fct', colour=discord.Colour.orange(),
description=f'''
Type this command to get some free Gridcoins.
Amounts are random and you can only request once per {g.FCT_REQ_LIM} hours.
To help fund the faucet, you can type `%fgive [amount-GRC]`.''')

qr = discord.Embed(title='Generate a QR code: %qr', colour=discord.Colour.orange(),
description='''
Format: %qr [optional data]

Generates a qr code. If no data is given, it will send a QR code of your
wallet address. Any data given must contain no spaces.''')

faq = discord.Embed(title='Read answers to frequently asked questions: %faq', colour=discord.Colour.orange(),
description='''
Format: %faq [selection no.]

All answers are formulated by Delta, Foxifi and LavRadis, and checked by
community members and developers.''')

block = discord.Embed(title='Explore blocks on the Gridcoin network: %block', colour=discord.Colour.orange(),
description='''
Format: %block [height]

Fetches information about a particular block on the Gridcoin blockchain.''')

status = discord.Embed(title='Bot and network status: %status', colour=discord.Colour.orange(),
description='''
Check the bot status to see whether it is online and observe some basic stats.''')

time = discord.Embed(title='Show your timeouts: %time', colour=discord.Colour.orange(),
description='''
Shows faucet, withdrawal and donation availability and time until eligibility.''')

invite = discord.Embed(title='Get the link to the main server: %invite', colour=discord.Colour.orange(),
description='''Shows the invite link to the official Gridcoin server.''')

rules_help = discord.Embed(title='Show the bot rules: %rules', colour=discord.Colour.orange(),
description='''
Rules about using the bot and what may result in a ban.''')

terms_help = discord.Embed(title='Show the bot terms: %terms', colour=discord.Colour.orange(),
description='''
Terms and conditions for making an account with the bot that you automatically accept by typing %new.''')

info_help = discord.Embed(title='Information about the bot: %info', colour=discord.Colour.orange(),
description='''
Shows information about authors and contributors.''')

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
    'invite'    :   invite,
    'rules'     :   rules_help,
    'terms'     :   terms_help,
    'info'      :   info_help
}
