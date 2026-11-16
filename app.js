const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Include router module (Blueprint)
const osCommandRouter = require('./vulnerable_endpoints/os_command_injection');

// Launch the application and use the router for the '/os-cmd' endpoint
app.use('/os-cmd', osCommandRouter);

app.get('/', (req, res) => {
    res.send('Vulnerable Node.js is running');
});

app.listen(PORT, () => {
    console.log(`Node.js server is running at http://localhost:${PORT}`);
});