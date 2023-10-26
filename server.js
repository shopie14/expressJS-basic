const express = require("express");
const multer = require("multer");
const uuid = require("uuid");
const amqp = require("amqplib");
const fs = require("fs");
const ftp = require("basic-ftp");
const MongoClient = require("mongodb").MongoClient;

const app = express();
const port = 3000;

// RabbitMQ configurations
const RABBITMQ_HOST = "localhost";
const RABBITMQ_QUEUE = "face_lskk";

// FTP configurations
const FTP_SERVER = "ftp5.pptik.id";
const FTP_PORT = 2121;
const FTP_USERNAME = "magangitg";
const FTP_PASSWORD = "bWFnYW5naXRn";
const FTP_UPLOAD_DIR = "./face_reports/report_lskk/";

// MongoDB configurations
const mongo_url =
  "mongodb://magangitg:bWFnYW5naXRn@database2.pptik.id:27017/magangitg";
const mongo_db = "magangitg";
const mongo_collection_name = "face_lskk";

let mongo_collection;

async function createMongoConnection() {
  const client = await MongoClient.connect(mongo_url, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });
  const db = client.db(mongo_db);
  mongo_collection = db.collection(mongo_collection_name);
}

createMongoConnection();

// RabbitMQ connection setup
async function sendToQueue(filename, receipt) {
  const connection = await amqp.connect(`amqp://${RABBITMQ_HOST}`);
  const channel = await connection.createChannel();

  try {
    await channel.assertQueue(RABBITMQ_QUEUE, { durable: false });
  } catch (error) {
    if (error.code !== 406) {
      throw error;
    }
  }

  channel.sendToQueue(RABBITMQ_QUEUE, Buffer.from(filename), {
    appId: receipt,
  });

  await channel.close();
  await connection.close();
}

// FTP connection setup
async function uploadToFTP(filename) {
  const client = new ftp.Client();
  client.ftp.verbose = true;
  try {
    await client.access({
      host: FTP_SERVER,
      port: FTP_PORT,
      user: FTP_USERNAME,
      password: FTP_PASSWORD,
    });
    await client.cd(FTP_UPLOAD_DIR);
    console.log(`Uploading ${filename} to FTP server.`);
    await client.uploadFrom(filename, filename);
    console.log(`Upload ${filename} complete.`);
  } catch (error) {
    console.log(error);
  }
  client.close();
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Multer setup
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

app.post("/upload", upload.single("file"), async (req, res) => {
  try {
    const iamge_file = req.file;
    if (iamge_file) {
      const file_uuid = uuid.v4();

      const new_filename = `${file_uuid}.jpg`;

      const receipt = new_filename;

      const temp_path = `uploads/${new_filename}`;

      fs.writeFileSync(temp_path, iamge_file.buffer);

      await uploadToFTP(temp_path);
      await sendToQueue(new_filename, receipt);

      await mongo_collection.insertOne({
        receipt: receipt,
        status: "uploaded",
      });

      res.json({
        receipt: receipt,
        status: "file uploaded successfully",
      });
    } else {
      const error_message = "No image uploaded.";
      res.json({ error: error_message });
    }
  } catch (error) {
    const error_message = error.message || "An error occurred.";
    res.json({ error: error_message });
  }
});

app.get("/check/:filename", async (req, res) => {
  try {
    const filename = req.params.filename;
    const result = await mongo_collection.findOne({ receipt: filename });

    if (result) {
      const receipt = result.receipt || "unknown";
      const status = result.status || "unknown";

      res.json({ receipt, status, filename });
    } else {
      req.json({ error: "File not found in the database." });
    }
  } catch (error) {
    req.json({ error: `An error occurred: ${error.message || "unknown"}` });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
