const request = require("request");
const converter = require('xml-js');
const auth = require('basic-auth')

function convert(req,res) {
  json = req.body
  console.log(json);
  var options = {compact: true, ignoreComment: true, spaces: 4};
  var xml = converter.json2xml(json, options);
  console.log(xml);
  return xml;
}

function send(xml) {
  console.log('sending request');
  request.post({
      url:"http://www.example.com:8000",
      method:"POST",
      headers:{
          'Content-Type': 'application/xml',
      },
      body: xml
  },
  function(error, response, body){
      console.log(response.statusCode);
      console.log(body);
      console.log(error);
  });
}

exports.json2xml = (req, res) => {
  var credentials = auth(req);
  if (!credentials || credentials.name !== 'john' || credentials.pass !== 'secret') {
    res.statusCode = 401;
    res.setHeader('WWW-Authenticate', 'Basic realm="example"');
    console.log('Access denied');
    res.end('Access denied');
  } else {
    xml = convert(req, res);
    send(xml);
  }
};

