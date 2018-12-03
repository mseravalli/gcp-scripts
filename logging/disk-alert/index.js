const request = require("request");
const auth = require('basic-auth')
const Compute = require('@google-cloud/compute');

const compute = new Compute();
const zone = compute.zone('europe-west1-b');
const disk = zone.disk('disk1');

function getDisks(res) {
  options = {
    autoPaginate: false
  };
  compute.getDisks(options, (err, disks) => {
    if (err) {
      console.log(err);
    }
    console.log('disks:', disks);
    res.statusCode = 200;
    res.end(JSON.stringify(disks));
  });
}

exports.disk_alert = (req, res) => {
  var credentials = auth(req);
  if (!credentials || credentials.name !== 'john' || credentials.pass !== 'secret') {
    res.statusCode = 401;
    res.setHeader('WWW-Authenticate', 'Basic realm="example"');
    console.log('Access denied');
    res.end('Access denied');
  } else {
    console.log(req.body);
    getDisks(res);
  }
};

