const express = require('express');
const app = express();
const mongoose = require('mongoose');
const MahasiswaModel = require('./models/mahasiswa_model');
const dotenv = require('dotenv');

dotenv.config();

mongoose.connect(process.env.DB_Connect, { useNewUrlParser: true, useUnifiedTopology: true });
app.use(express.json());

// Route to create data

app.post('/create-mahasiswa', async function (req,res) {
    console.log(req.body)
    const NewMahasiswa = new MahasiswaModel({
        nama: req.body.nama,
        jurusan: req.body.jurusan 
    });
    const saveData = await NewMahasiswa.save();
    res.send({
        status: true,
        message: 'Data berhasil dibuat',
        data:saveData
    })
})


app.listen(5000, () => {
    console.log('Server is running on port 5000');
});