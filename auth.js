const express = require("express");
const app = express();
const path = require("path");
const hbs = require("hbs");
const collection = require("./models/users_auth");
const viewPath = path.join(__dirname, "./views");

app.use(express.json());
app.set("view engine", "hbs");
app.set("views", viewPath);
app.use(express.urlencoded({ extended: false }));

// get login
app.get("/", (req, res) => {
  res.render("login");
});

// get signup
app.get("/signup", (req, res) => {
  res.render("signup");
});

app.post("/signup", async (req, res) => {
  const data = {
    email: req.body.email,
    password: req.body.password,
  };

  await collection.insertMany([data]);
  res.render("home");
});

app.post("/login", async (req, res) => {
  try {
    const check = await collection.findOne({ email: req.body.email });
    if (check.password === req.body.password) {
      res.render("home");
    } else {
      res.send("Wrong password");
    }
  } catch (error) {
    res.send("Wrong details");
  }
});

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
