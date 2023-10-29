const express = require("express");
const app = express();
const path = require("path");
const hbs = require("hbs");
const collection = require("./models/users_auth");
const viewPath = path.join(__dirname, "./views");
const cookieParser = require("cookie-parser");
const crypto = require("crypto");

app.use(express.json());
app.set("view engine", "hbs");
app.set("views", viewPath);
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

function getHashedPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto
    .pbkdf2Sync(password, salt, 1000, 64, "sha512")
    .toString("hex");
  return {
    salt,
    hash,
  };
}

app.get("/", (req, res) => {
  res.render("login");
});

app.get("/signup", (req, res) => {
  res.render("signup", {
    message: "Signup successful",
    messageClass: "alert-success",
  });
});

app.post("/signup", async (req, res) => {
  const { email, password } = req.body;

  const hashedPassword = getHashedPassword(password);

  const data = {
    email,
    password: hashedPassword.hash,
  };

  await collection.create(data);
  res.render("home");
});

app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  try {
    const check = await collection.findOne({ email });
    if (!check) {
      res.send("Wrong details");
      return;
    }

    const hashedPassword = getHashedPassword(password);

    if (check.hash === hashedPassword.hash) {
      res.render("login", {
        message: "Login successful",
        messageClass: "alert-success",
      });
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
