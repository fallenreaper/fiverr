
const TOKEN = "NzYzMTQzNjA0OTg5NDYwNTEx.GT2TNg.SQa-iIPk1v91lexSpVHjBBbEgoqBeOnpgSfpeA"
const CLIENT_ID="763143604989460511"
const GUILD_ID="692523780622385196"

const { Client, GatewayIntentBits, Events, REST, Routes } = require('discord.js');
const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const { updateServer, loadLinkedServers, getBroadcastTargets } = require('./loadingdata');

const commands = [
  {
    name: 'message',
    description: 'sends a message',
    options: [
      {
        name: "message", 
        description: "Transmitted Message",
        type: 3,
        required: true
      }
    ]
  },
  {
    name: 'init',
    description: 'Sets selected channel as broadcast target for the server',
  },
  {
    name: "delete",
    description: "Removes the server from the system."
  },
  {
    name: "help",
    description: "Lists help commands."
  }
];

const rest = new REST({ version: '10' }).setToken(TOKEN);

(async () => {
  try {
    console.log('Started refreshing application (/) commands.');

    await rest.put(Routes.applicationCommands(CLIENT_ID, GUILD_ID), { body: commands });

    console.log('Successfully reloaded application (/) commands.');
  } catch (error) {
    console.error(error);
  }
})();

client.on(Events.ClientReady, () => {
  console.log(`Logged in as ${client.user.tag}!`);
  loadLinkedServers()
});

client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;
  switch ( interaction.commandName) {
    case 'message':
      const message = interaction.options.get("message").value || ''
      await interaction.reply(`Sent Message: ${message}}`)
      let broadcastList = getBroadcastTargets()
      let s = new Set(client.guilds.cache.keys())
      Object.entries(broadcastList).forEach( ([server,channel]) => {
        if (!s.has(server)) {
          console.log("Server not Being monitored")
          return;
        }
        const channels = client.guilds.cache.get(server).channels.cache
        console.log("Channel Cache", channels)

        channels.get(channel).send(message)
        // })
      })
      break
    case 'init':
      await interaction.reply('Initializing Channel for Broadcasting.')
      updateServer(interaction.guildId, interaction.channelId)
      break;
    case 'delete':
      await interaction.reply('Removing server from list.')
      updateServer(interaction.guildId, interaction.channelId, true)
      break
    case 'help':
      await interaction.reply(```These are Commands you can use to send messages to the server:
      init:  This will establish a server/channel relationship for broadcasting.
      delete: Removes a server from the broadcast.
      message: Transmits a messages to all the servers.  This is only usable by the admin.
      ```)
      break;
  }
  // if (interaction.commandName === 'message') {
  //   await interaction.reply(interaction);
  // } {
  // }
});

client.login(TOKEN);