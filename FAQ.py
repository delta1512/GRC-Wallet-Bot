import discord

links = [
'https://boinc.berkeley.edu/', #0
'https://boinc.berkeley.edu/projects.php', #1
'https://gridcoinstats.eu/project', #2
'http://www.gridcoin.us/', #3
'https://www.grcpool.com/', #4
'https://boinc.berkeley.edu/download.php', #5
'https://t.me/gridcoin', #6
'https://grcinvite.herokuapp.com', #7
'https://www.reddit.com/r/gridcoin/', #8
'https://cryptocurrencytalk.com/forum/464-gridcoin-grc/', #9
'https://github.com/gridcoin/Gridcoin-Research', #10
'https://discord.me/gridcoin', #11
'http://gridcoin.us/Guides/gridcoin-install.htm', #12
'http://download.gridcoin.us/download/downloadstake/signed/snapshot.zip', #13
'http://wiki.gridcoin.us/FAQ#Sync', #14
'http://gridcoin.ch/', #15
'https://www.gridcoin.science/', #16
'https://www.whatisgridcoin.com/', #17
'https://coinmarketcap.com/currencies/gridcoin/', #18
'http://wiki.gridcoin.us/Main_Page', #19
'https://gridcoinstats.eu/index.php', #20
'https://gridcoin.network/', #21
'https://grcexplorer.neuralminer.io', #22
'https://www.nuad.de', #23
'https://grctnexplorer.neuralminer.io/', #24
'https://delta1512.github.io/BOINCOS/', #25
'http://www.boincitaly.org/supporto/boinc-distro.html', #26
'https://boinc.berkeley.edu/wiki/User_manual', #27
'https://forums.overclockers.co.uk/threads/the-greatest-official-boinc-faq.17347384/', #28
'https://www.facebook.com/gridcoins/', #29
'https://twitter.com/GridcoinNetwork', #30
'https://steemit.com/trending/gridcoin', #31
'https://www.grcpool.com/account', #32
'https://youtu.be/jm2E6pQ-Ifw', #33
'https://github.com/gridcoin/Gridcoin-Research/issues' #34
]

# What is Gridcoin?
what_is_grc = discord.Embed(title='What is Gridcoin?', colour=discord.Colour.purple(),
description='''
[Gridcoin]({}) is an open source cryptocurrency (Ticker: GRC) which securely rewards volunteer computing performed upon the [BOINC]({}) platform in a decentralized manner on top of Proof Of Stake (POS) and a new protocol known as Proof Of Research (POR).

Unlike typical currencies that compute (arguably) useless mathematics to produce hashes and secure their own chain, the Gridcoin ecosystem uses the environmentally friendly POS protocol in addition to incentivising the computing of real-world problems that help solve humanity’s greatest struggles such as cancer, protein fabrication, prime factoring and even searching for alien life.
'''.format(links[3], links[0]))

# What is BOINC?
what_is_boinc = discord.Embed(title='What is BOINC?', colour=discord.Colour.purple(),
description='''
[BOINC]({}) is an open-source volunteer computing network which combines the processing power of all individual users for the purposes of scientific research. It's free, production ready and many projects already harness volunteered computing power to attempt to cure cancer/AIDS/Ebola/malaria, map the Milky Way galaxy, search for extraterrestrial signals and [much more]({}).
'''.format(links[0], links[1]))

# How is GRC staked/mined?
how_to_stake = discord.Embed(title='How is GRC mined/staked?', colour=discord.Colour.purple(),
description='''
Stakers are people that hold Gridcoin and earn 1.5% annual interest (stake) on their mature reserve (coins not moved for at least 16hr). Likelihood of gaining these rewards (by definition of POSv2) is dependent on your balance.

Crunchers (AKA Miners) are individuals that participate in [BOINC]({}) computing and earn rewards from Gridcoin through Proof Of Research (POR). To be eligible for GRC rewards, miners must have a minimum of 100 Recent Average Credit (RAC) from BOINC for any [whitelisted project]({}) and an existing GRC balance.
'''.format(links[0], links[2]))

# How much GRC is enough to start staking?
how_much_grc = discord.Embed(title='How much GRC is enough to start staking?', colour=discord.Colour.purple(),
description='''
A good amount of GRC to hold in your wallet is at least 2000 GRC and will allow you to stake on a regular basis. Time to get rewards depends on network difficulty (the collective amount of coins online and trying to stake) and whether you have reached the minimum threshold to retrieve your rewards.
''')

# Where can I report issues and where can I get help?
additional_help = discord.Embed(title='Where can I report issues and where can I get help?', colour=discord.Colour.purple(),
description='''
The following links are various Gridcoin community locations and you will surely find someone that can help:
- [Telegram]({})
- [Slack]({})
- [Reddit]({})
- [Cryptocurrency Talk]({})
- [Github]({})
- [Discord]({})
'''.format(links[6], links[7], links[8], links[9], links[34], links[11]))

# How do I get started with pool mining?
pool_mining = discord.Embed(title='How do I get started with pool mining?', colour=discord.Colour.purple(),
description='''
1. Visit [the GRC pool]({}) and create a new account

2. Download and install the [BOINC software]({})

3. In your BOINC manager click View > Advanced View...

4. Navigate to Tools > Use Account Manager…

5. In the “Account Manager URL” section type: https://www.grcpool.com/ and press next

6. Type in the credentials you used for step 1 and click continue, then finish

7. Click Tools > Synchronise with grcpool.com

8. On your [pool account]({}) click your account name in the top-right and then click hosts

9. Click on your computer name and select a project in the drop-down menu below, then click the save button at the very bottom

10. Repeat step 7 in your BOINC manager and then move to the projects tab to see the new project

The official pool guide can be found [here]({})'''.format(links[4], links[5], links[32], links[33]))

# How do I get started with solo mining?
solo_mining = discord.Embed(title='How do I get started with solo mining?', colour=discord.Colour.purple(),
description='''
1. Download and install [BOINC]({}) and choose a project in the [whitelist]({}) to begin crunching from.

2. In your BOINC manager click View > Advanced View..., then click the projects tab.

3. Go to the site for your associated project, login and set “Gridcoin” as your team, then select the project in the BOINC manager and click update.

4. Download and install the [GRC client]({}) or [compile it from source]({})

5. Configure the client according to the prompts or follow the [guide]({})

6. After configuration, close the client completely and then open your configuration folder (Windows: C:\[User]\Appdata\Roaming\Gridcoinresearch) (Linux: ~/.GridcoinResearch/)

7. Delete everything in this folder apart from the wallet.dat, gridcoinresearch.conf and the walletbackups folder.

8. Download the [snapshot]({}) (warning, file over 1.5GB) and extract it directly into the configuration folder (official instructions [here]({}))

9. Re-open the GRC client and wait for it to synchronise with the rest of the chain.

10. Click the “Receive” tab to find your GRC address and get some coins to stake and beacon with.

11. Once you have some coins and your client is fully synchronised, in the GRC client go to Help > Debug Window > Console and type “execute advertisebeacon”.

12. If the return message says “SUCCESS”, then you must wait about a day for your client to be recognised for your crunching. If it says “FAIL” Then make sure you have over 100 RAC and a small GRC balance before contacting a Gridcoin community member to help you troubleshoot issues.
'''.format(links[5], links[2], links[3], links[10], links[12], links[13], links[14]))

# Useful links
useful_links = discord.Embed(title='Useful links', colour=discord.Colour.purple(),
description='''
Information:
- [Gridcoin Official Site]({})
- [Gridcoin Swizerland]({})
- [Gridcoin.Science]({})
- [What Is Gridcoin]({})
- [Coinmarketcap]({})
- [Wiki]({})
- [Github]({})

Block Explorers:
- [Gridcoin Stats]({})
- [Gridcoin.Network]({})
- [GRCExplorer.Neuralminer]({})
- [Nuad.de]({})
- [GRC Testnet]({})

BOINC Related:
- [Boinc.Berkeley]({})
- [BoincOS]({})
- [Boinc Italy Linux Distro]({})
- [Boinc Wiki Manual]({})
- [Overclockers Boinc FAQ]({})

Media and community:
- [Discord]({})
- [Facebook]({})
- [Twitter]({})
- [Slack]({})
- [Reddit]({})
- [Steem]({})
- [Cryptocurrencytalk]({})
'''.format(links[3], links[15], links[16], links[17], links[18], links[19],
            links[10], links[20], links[21], links[22], links[23], links[24],
            links[0], links[25], links[26], links[27], links[28], links[11],
            links[29], links[30], links[7], links[8], links[31], links[9]))

# Do I need to put the GRC client on all computers running BOINC?
client_on_many_pc = discord.Embed(title='Do I need to put the GRC client on all computers running BOINC?', colour=discord.Colour.purple(),
description='''
No, you simply need to ensure that all your BOINC computers use the same email and are crunching for the Gridcoin team. Doing so may get you temporarily banned by the network and could have implications on the integrity of your wallet.
''')

# Example GRC config windows
example_windows = discord.Embed(description='''```
email=YOUREMAIL@example.com
boincdatadir=C:\ProgramData\BOINC\
boincappdir=C:\Program Files\BOINC\
addnode=la.grcnode.co.uk
addnode=london.grcnode.co.uk
addnode=miami.grcnode.co.uk
addnode=node.gridcoin.network
addnode=node.gridcoin.us
addnode=node.gridcoinapp.xyz
addnode=toronto01.gridcoin.ifoggz-network.xyz
addnode=vancouver01.gridcoin.ifoggz-network.xyz
addnode=www.grcpool.com
addnode=is.gridcoin.pl # Iceland
addnode=nl.gridcoin.pl # Netherlands
addnode=de.gridcoin.pl # Germany
```''')

# Example GRC config linux
example_linux = discord.Embed(description='''```
email=YOUREMAIL@example.com
boincdatadir=/var/lib/boinc/
addnode=la.grcnode.co.uk
addnode=london.grcnode.co.uk
addnode=miami.grcnode.co.uk
addnode=node.gridcoin.network
addnode=node.gridcoin.us
addnode=node.gridcoinapp.xyz
addnode=toronto01.gridcoin.ifoggz-network.xyz
addnode=vancouver01.gridcoin.ifoggz-network.xyz
addnode=www.grcpool.com
addnode=is.gridcoin.pl # Iceland
addnode=nl.gridcoin.pl # Netherlands
addnode=de.gridcoin.pl # Germany
```''')

index = [{'What is Gridcoin?': what_is_grc},
        {'What is BOINC?' : what_is_boinc},
        {'How is GRC staked/mined?' : how_to_stake},
        {'How much GRC is enough to start staking?' : how_much_grc},
        {'How do I get started with pool mining?' : pool_mining},
        {'How do I get started with solo mining?' : solo_mining},
        {'Do I need to put the GRC client on all computers running BOINC?' : client_on_many_pc},
        {'Example GRC config windows' : example_windows},
        {'Example GRC config linux' : example_linux},
        {'Where can I report issues and where can I get help?' : additional_help},
        {'Useful links' : useful_links}]
