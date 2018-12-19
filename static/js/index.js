 $('#processing')[0].style.display = "none";
 $('#msg')[0].style.display = "none" ;

 var socket = io.connect('https://mpesatestapp.herokuapp.com/');
 socket.on('connect', function() {
    socket.emit('connection', {data: 'I\'m connected!'});
 });

socket.on('completed', function(message) {
    $('#processing')[0].style.display = "none";
    $('#msg')[0].style.display = "block" ;
    $('#msg')[0].innerHTML = message ;
});

socket.on('processing', function(message) {
    $('#processing')[0].style.display = "block"; ;
});

$("#form").submit(function(e) {
    $('#msg')[0].style.display = "none" ;
    e.preventDefault();
    values = $(this);
    json= JSON.stringify({"phone_number" : values[0][0].value, "amount": values[0][1].value });
    socket.emit('submission', json);
});