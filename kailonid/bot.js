
// var Discord = require('discord.io');
// var auth = require('./auth.json');
// var fs = require("fs");
// const { exit } = require('process');

// const { REST, Routes } = require('discord.js');

// const commands = [
//   {
//     name: 'init',
//     description: 'Sets selected channel as broadcast target for the server',
//   },
//   {
//     name: "whoami",
//     description: "Replies with who you are."
//   },
//   {
//     name: "delete",
//     description: "Removes the server from the system."
//   },
//   {
//     name: "help",
//     description: "Lists help commands."
//   }
// ];

// const rest = new REST({ version: '10' }).setToken(TOKEN);

// (async () => {
//   try {
//     console.log('Started refreshing application (/) commands.');

//     await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });

//     console.log('Successfully reloaded application (/) commands.');
//   } catch (error) {
//     console.error(error);
//   }
// })();


const filename = "save.txt"
const BROADCAST_SERVERS = {}
function loadLinkedServers() {
    const rawData = fs.readFileSync(filename)
    try {
        BROADCAST_SERVERS = JSON.parse(rawData)
    }catch(e){ 
        console.error("Failed to Load File.")
        exit(1)
    }
}
function updateServer(server, channel, deleteServer=false) {
    if (deleteServer) {
        delete BROADCAST_SERVERS[server]
    } else {
        BROADCAST_SERVERS[server] = channel
    }
    try {
        fs.writeFileSync(filename, JSON.stringify(BROADCAST_SERVERS))
    } catch(e){
        console.error(e)
    }
}

// Initialize Discord Bot
// var bot = new Discord.Client({
//     token: auth.token,
//     autorun: true
// });
// bot.on('ready', function (evt) {
//     loadLinkedServers()
// });
// bot.on('message', function (user, userID, channelID, message, evt) {
//     console.log("Data", evt)
//     console.log("Bot", Object.values(bot.servers[evt.d.guild_id].roles))
//     var roles = Object.values(bot.servers[evt.d.guild_id].roles)
//     var adminRoles = roles.filter(r => r._permissions & 0x8 === 0x8)
//     var isAdmin = evt.d.member.roles.map(roleId => bot.servers[evt.d.guild_id].roles[roleId]).filter(r => r._permissions & 0x8 === 0x8).length > 0
//     console.log(`All Roles: ${roles.map(r => r.name)}\nAdmin Roles: ${adminRoles.map(r => r.name)}`)
//     if (evt.d.author.bot) return;
//     if (! message.toLowerCase().startsWith("!fc")) return;
//     console.log("Hello")
//     var args = message.substring(4).split(' ');
//     var cmd = args[0].toLowerCase();
//     args = args.splice(1).map( i => i.toLowerCase())
//     console.log("Command", cmd, "Args", args)

//     const guild_id = evt.d.guild_id;
//     switch (cmd) {
//         case "init": break;
//         case "delete": break;
//         case "help": 
//             cmds = [
//                 "help: info", 
//                 "init: initialized channel into broadcasting.  Only 1 channel per server",
//                 "delete:  Deletes server from Broadcasting",
//                 "whoami: Gives you insight as to who you are"
//             ];
//             const message = `Commands:\n${cmds.join("\n - ")}`;
//             bot.sendMessage({
//                 to: channelID,
//                 message
//             });
//             break;
//         case "whoami":
//             bot.sendMessage({
//                 to: channelID,
//                 message: `${userID}: ${user}`
//             })
//             break;
//     }
// });



// const { Client, GatewayIntentBits } = require('discord.js');
// const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// client.on('ready', () => {
//   console.log(`Logged in as ${client.user.tag}!`);
// });

// client.on('interactionCreate', async interaction => {
//   if (!interaction.isChatInputCommand()) return;

//   if (interaction.commandName === 'ping') {
//     await interaction.reply('Pong!');
//   }
// });
// TOKEN = "NzYzMTQzNjA0OTg5NDYwNTEx.GT2TNg.SQa-iIPk1v91lexSpVHjBBbEgoqBeOnpgSfpeA"
// client.login(TOKEN);


const { Client, Intents } = require("discord.js");
const client = new Client({
  intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES]
});

client.on("ready", () => {
  console.log("I am ready!");
});

client.on("messageCreate", (message) => {
  if (message.content.startsWith("ping")) {
    message.channel.send("pong!");
  }
});
TOKEN = "NzYzMTQzNjA0OTg5NDYwNTEx.GT2TNg.SQa-iIPk1v91lexSpVHjBBbEgoqBeOnpgSfpeA"

client.login(TOKEN);