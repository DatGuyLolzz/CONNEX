const express = require('express');
const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

// Serve static files
app.use('/images', express.static(path.join(__dirname, '../images')));
app.use(express.static(path.join(__dirname, '../')));

// Serve HTML files from the templates directory
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../templates/login.html'));
});

app.get('/signup', (req, res) => {
  res.sendFile(path.join(__dirname, '../templates/signup.html'));
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
