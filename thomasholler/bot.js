
var Discord = require('discord.io');
var logger = require('winston');
var auth = require('./auth.json');
var fs = require("fs");
// Configure logger settings
logger.remove(logger.transports.Console);
logger.add(new logger.transports.Console, {
    colorize: true
});
logger.level = 'debug';

var data = {};
var saveData = () => {
    const _d = {};
    for (let p in data){
        _d[p] = Array.from(data[p])
    }
    fs.writeFile("data.json", JSON.stringify(_d), (err, _) => {
        if (err){ 
            console.log("Error Writing File.");
            return;
        }
        console.log("Data Saved: data.json")
    });
};
var loadData = () => {
    fs.readFile( "data.json", "utf-8", (err, contents) => {
        if (err){
            console.log("Base data Not found. Creating empty");
        }
        try{
            r = err ? {} : JSON.parse(contents);
            for (let p in r){
                data[p] = new Set(r[p])
            }
        }catch(e){
            data = {}
        }
    })
};

// Initialize Discord Bot
var bot = new Discord.Client({
    token: auth.token,
    autorun: true
});
bot.on('ready', function (evt) {
    logger.info('Connected');
    logger.info('Logged in as: ');
    logger.info(bot.username + ' - (' + bot.id + ')');
    loadData()
});
bot.on('message', function (user, userID, channelID, message, evt) {
    console.log("Data", evt)
    console.log("Bot", Object.values(bot.servers[evt.d.guild_id].roles))
    var roles = Object.values(bot.servers[evt.d.guild_id].roles)
    var adminRoles = roles.filter(r => r._permissions & 0x8 === 0x8)
    var isAdmin = evt.d.member.roles.map(roleId => bot.servers[evt.d.guild_id].roles[roleId]).filter(r => r._permissions & 0x8 === 0x8).length > 0
    console.log(`All Roles: ${roles.map(r => r.name)}\nAdmin Roles: ${adminRoles.map(r => r.name)}`)
    if (evt.d.author.bot) return;
    if (! message.toLowerCase().startsWith("!fc")) return;
    console.log("Hello")
    var args = message.substring(4).split(' ');
    var cmd = args[0].toLowerCase();
    args = args.splice(1).map( i => i.toLowerCase())
    console.log("Command", cmd, "Args", args)

    const guild_id = evt.d.guild_id;
    switch (cmd) {
        case "help": 
            cmds = [
                "help: info", 
                "add: preserves arguments", 
                "set: preserves arguments", 
                "delete: removes arguments", 
                "remove removes arguments", 
                "remove-all: clears channel", 
                "delete-all: clears channel", 
                "reset: clears channel",
                "list: shows all items in memeory", 
                "list-all: shows all items in memeory", 
                "whoami: Gives you insight as to who you are"
            ];
            const message = `Commands:\n${cmds.join("\n - ")}`;
            bot.sendMessage({
                to: channelID,
                message
            });
            break;
        case "whoami":
            bot.sendMessage({
                to: channelID,
                message: `${userID}: ${user}`
            })
            break;
        case "add":
        case "set":
            if (!data[guild_id]){
                data[guild_id] = new Set([])
            }
            args.forEach( item => {
                data[guild_id].add(item)
            });
            bot.sendMessage({
                to: channelID,
                message: `Added: \n${args.join("\n- ")}`
            })
            saveData()
            break;
        case "delete-all":
        case "remove-all":
            if (!isAdmin) return;
            data[guild_id].clear();

            bot.sendMessage({
                to: channelID,
                message: `Reset Guild`
            })
            saveData()
            break;
        case "delete":
        case "remove":
            if (!isAdmin) return;
            args.forEach( item => {
                data[guild_id].delete(item)
            });

            bot.sendMessage({
                to: channelID,
                message: `Removed: \n${args.join("\n- ")}`
            })
            saveData()
            break;
        case "list-all":
        case "list":
            bot.sendMessage({
                to: channelID, 
                message: Array.from(data[guild_id]).join("\n- ")})
            break;
    }
});

