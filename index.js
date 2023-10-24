const express = require('express');
const app = express();

const mongose = require('mongoose');


connectDB().catch(err => console.log(err));

async function connectDB() {
  await mongose.connect('mongodb://magangitg:bWFnYW5naXRn@database2.pptik.id:27017/?authMechanism=DEFAULT&authSource=magangitg');
  console.log("Database connected");
}

app.get('/', function(req, res){
   res.send("Hello world!");
});



app.listen(3000);