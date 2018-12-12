var express        =        require("express");
var bodyParser = xmlparser = require('express-xml-bodyparser');
var app            =        express();
const port = 8000;
app.use(bodyParser());

const echo = function(req, res) {
  console.log('received:');
  console.log(req.body);
  res.send('xml received');
};

app.route('/').post(echo);

app.listen(port);

console.log('server started on: ' + port);
