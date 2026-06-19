const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const HTML_PATH = path.resolve(__dirname, '../canvas/organizerjarvis.html');

const server = http.createServer((req, res) => {
  if (req.url === '/organizerjarvis' || req.url === '/organizerjarvis.html' || req.url === '/') {
    fs.readFile(HTML_PATH, (err, data) => {
      if (err) {
        res.writeHead(500);
        res.end('Server error');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`JARVIS organizer running at http://127.0.0.1:${PORT}/organizerjarvis`);
});
