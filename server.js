// link penjelasan https://stackabuse.com/handling-authentication-in-express-js/

// server.js
const express = require("express");
const exphbs = require("express-handlebars");
const cookieParser = require("cookie-parser");
const crypto = require("crypto");
const mongoose = require("mongoose");
const dotenv = require("dotenv");
const app = express();
dotenv.config();

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(cookieParser());

// Connect to MongoDB
mongoose.connect(process.env.DB_Connect, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});
console.log("Database connected");

// Create a mongoose model for users
const Users = require("./models/users_auth");

// Set up Handlebars
const hbs = exphbs.create({ extname: ".hbs" });
app.engine("hbs", hbs.engine);
app.set("view engine", "hbs");

// Route to render the home page
app.get("/", (req, res) => {
  res.render("home");
});

// Route to render the registration page
app.get("/register", (req, res) => {
  res.render("register");
});

// Hash the password
const getHashedPassword = (password) => {
  const sha256 = crypto.createHash("sha256");
  const hash = sha256.update(password).digest("base64");
  return hash;
};

// Register a new user
app.post("/register", async (req, res) => {
  const { email, firstName, lastName, password, confirmPassword } = req.body;

  if (password === confirmPassword) {
    try {
      const existingUser = await Users.findOne({ email });

      if (existingUser) {
        return res.render("register", {
          message: "User already registered.",
          messageClass: "alert-danger",
        });
      }

      const hashedPassword = getHashedPassword(password);
      const newUser = new Users({
        firstName,
        lastName,
        email,
        password: hashedPassword,
      });

      await newUser.save();

      res.render("login", {
        message: "Registration Complete. Please login to continue.",
        messageClass: "alert-success",
      });
    } catch (error) {
      console.error(error);
      res.render("register", {
        message: "An error occurred during registration.",
        messageClass: "alert-danger",
      });
    }
  } else {
    res.render("register", {
      message: "Password does not match.",
      messageClass: "alert-danger",
    });
  }
});

// Login a user
app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const hashedPassword = getHashedPassword(password);

  try {
    const user = await Users.findOne({ email, password: hashedPassword });

    if (user) {
      const authToken = generateAuthToken();
      authTokens[authToken] = user;
      res.cookie("AuthToken", authToken);
      res.redirect("/protected");
    } else {
      res.render("login", {
        message: "Invalid username or password",
        messageClass: "alert-danger",
      });
    }
  } catch (error) {
    console.error(error);
    res.render("login", {
      message: "An error occurred during login.",
      messageClass: "alert-danger",
    });
  }
});

// Generate an authentication token
const generateAuthToken = () => {
  return crypto.randomBytes(30).toString("hex");
};

// Check authentication before accessing protected route
app.use((req, res, next) => {
  const authToken = req.cookies["AuthToken"];
  req.user = authTokens[authToken];
  next();
});

// Protected route
app.get("/protected", (req, res) => {
  if (req.user) {
    res.render("protected");
  } else {
    res.render("login", {
      message: "Please login to continue",
      messageClass: "alert-danger",
    });
  }
});

app.listen(3000, () => {
  console.log("Server is running on port 3000");
});
