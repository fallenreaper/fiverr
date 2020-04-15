### Log Bot.

## Set up
- Go to https://discordapp.com/developers/applications/
- Set up an Application.
- Give it a name which suits you.
- On the left hand side you will see a button called: BOT, click it.
- Give the Bot a name.
- You will see a token area.
- Click CORP by Token, and paste into auth.json > token's field.
- Detemine if you want your bot to be public.  ( it is created such that it can be.)
- Click on OAuth2 on the left.
- Under scopes click 'bot'
- Determine the privledges for your bot.
- - Admin: 8
- - Send Messages: 2048
- - Send and Manage Messages: 10240
- Enter URL generated into browser.

Now you have the bot added to your server.

Next is to turn on the bot. Ensure that you saved auth.json so token exists

- Install NodeJS if you do not have it.  nodejs.org
- from a Terminal, navigate to this file directory.
- run the command: `npm install`
- Run the command: `node bot.js`

If you dont want it to be linked to a terminal, you can run the following instead:  `node bot.js &`