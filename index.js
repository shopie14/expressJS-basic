const express = require("express");
const app = express();
const mongoose = require("mongoose");
const MahasiswaModel = require("./models/mahasiswa_model");
const dotenv = require("dotenv");

dotenv.config();

mongoose.connect(process.env.DB_Connect, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});
app.use(express.json());

// Route to create data

app.post("/create-mahasiswa", async function (req, res) {
  console.log(req.body);

  const EditName = req.body.nama;
  const NewMahasiswa = new MahasiswaModel({
    nama: EditName,
    jurusan: req.body.jurusan,
  });
  const saveData = await NewMahasiswa.save();
  res.send({
    status: true,
    message: "Data berhasil dibuat",
    data: saveData,
  });
});

// data search by id
app.get("/cari-mahasiswa", async function (req, res) {
  const { nama } = req.query;

  const dataMahasiswa = await MahasiswaModel.find({
    nama: nama,
  });

  if (dataMahasiswa.length === 0) {
    res.send({
      status: false,
      message: "Data tidak ditemukan",
      data: "Koreksi data",
    });
  } else {
    res.send({
      status: true,
      message: "Data berhasil dicari",
      data: data,
    });
  }
});

app.delete("/delete-mahasiswa/:id", async function (req, res) {
  const data = await MahasiswaModel.findByIdAndDelete(req.params.id);
  res.send({
    status: true,
    message: "Data berhasil dihapus",
    data: data,
  });
});

app.listen(5000, () => {
  console.log("Server is running on port 5000");
});
