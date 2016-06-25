var watson = require('watson-developer-cloud');
var creds = require('./watsoncreds');

var speech_to_text = watson.speech_to_text({
  username: creds.username,
  password: creds.password,
  version: 'v1'
});

