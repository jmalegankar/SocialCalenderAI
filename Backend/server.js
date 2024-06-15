//To Run a server -> node server.js
//If errors come that say app requires middleware -> npm i nodemon -g; Add "start":"nodemon server.js" to scripts section in 'package-json' file
//'sudo' keyword in front overthrows all Access errors

const app = require("./app");
const dotenv = require("dotenv")
const http = require("http");
const mongoose = require("mongoose")
const {Server} = require("socket.io");
const path = require("path");


dotenv.config({path:"./config.env"}) //Connecting to config.env file for critical info


process.on("uncaughtException",(err)=>{ //Event listener to catch errors
    console.log(err);
    process.exit(1);
})

const server = http.createServer(app);

const io = new Server(server,{
    cors:{
        origin:"*",
        methods:["GET","POST"]
    }
});

const DB = process.env.DBURI.replace("<password>",process.env.DBPASSWORD)
mongoose.connect(DB,{dbName:'SocialCalenderAI',
    //useNewUrlParser:true, // The underlying MongoDB driver has deprecated their current connection string parser. Because this is a major change, they added the useNewUrlParser flag to allow users to fall back to the old parser if they find a bug in the new parser.
    //useCreateIndex:true,// Again previously MongoDB used an ensureIndex function call to ensure that Indexes exist and, if they didn't, to create one. This too was deprecated in favour of createIndex . the useCreateIndex option ensures that you are using the new function calls.
    // useFindAndModify: false, // findAndModify is deprecated. Use findOneAndUpdate, findOneAndReplace or findOneAndDelete instead.
    //useUnifiedToplogy:true, // Set to true to opt in to using the MongoDB driver's new connection management engine. You should set this option to true , except for the unlikely case that it prevents you from maintaining a stable connection.
}).then((con)=>{
    console.log("DB 'SocialCalenderAI' connection is successful");
}).catch((err)=>{
    console.log(err)
})

process.on("unhandledRejection",(err)=>{
    console.log(err);
    server.close(()=>{
        process.exit(1);
    })
})

//ports available on computer 3000,5000
const port = process.env.PORT || 8000

server.listen(port,()=>{
    console.log(`App running on port ${port}`);
})