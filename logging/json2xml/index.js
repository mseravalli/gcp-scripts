var converter = require('xml-js');
var auth = require('basic-auth')

function convert(req,res) {
  json = req.body
  console.log(json);
  var options = {compact: true, ignoreComment: true, spaces: 4};
  var result = converter.json2xml(json, options);
  console.log(result);
  res.send(result);
}

exports.json2xml = (req, res) => {
  var credentials = auth(req);
  if (!credentials || credentials.name !== 'john' || credentials.pass !== 'secret') {
    res.statusCode = 401;
    res.setHeader('WWW-Authenticate', 'Basic realm="example"');
    console.log('Access denied');
    res.end('Access denied');
  } else {
    convert(req, res);
  }
};

