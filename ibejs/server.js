const express = require('express');
const app = express();
const ibe = require('./ibe_extract');

app.get('/secret/:id', function (req, res) {
   res.send(ibe(req.params.id));
})

var server = app.listen(8081, function () {

})
