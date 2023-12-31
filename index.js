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


//  Menambahkan data
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

// Cari data berdasarkan id
app.get("/cari-mahasiswa", async function (req, res) {
  const { mahasiswa } = req.query;

  const dataMahasiswa = await MahasiswaModel.find({
    nama: mahasiswa,
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

// Delete data
app.delete("/delete-mahasiswa/:id", async function (req, res) {
  const data = await MahasiswaModel.findByIdAndDelete(req.params.id);
  res.send({
    status: true,
    message: "Data berhasil dihapus",
    data: data,
  });
});

//  Update data 
app.put("/update-mahasiswa/:id", async function (req, res) {
    const dataMahasiswa = await MahasiswaModel.findByIdAndUpdate(req.params.id, {
        nama: req.body.nama,
        jurusan: req.body.jurusan,
    });
    res.send({
        status: true,
        message: "Data berhasil diupdate",
        data: dataMahasiswa,
    });
});


app.listen(5000, () => {
  console.log("Server is running on port 5000");
});