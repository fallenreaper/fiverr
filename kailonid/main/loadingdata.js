

const filename = "save.json"
let BROADCAST_SERVERS = {}
var fs = require("fs");

function loadLinkedServers() {
    try {
        const rawData = fs.readFileSync(filename)
        BROADCAST_SERVERS = JSON.parse(rawData)
    }catch(e){ 
        console.error("Failed to Load File.", e)
        
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

function getBroadcastTargets() {
  return BROADCAST_SERVERS
}

module.exports.getBroadcastTargets = getBroadcastTargets
module.exports.updateServer = updateServer
module.exports.loadLinkedServers = loadLinkedServers