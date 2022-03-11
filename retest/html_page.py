entryPageFile = open('entryPage.html')
entryPage = entryPageFile.read()
entryPageFile.close()

gamePageFile = open('gamePage.html')
gamePage = gamePageFile.read()
gamePageFile.close()


html = """
<html>
    <head>
        <title>Mi Big Flask Test</title>
        <script>
        
        </script>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>
        <script type="text/javascript" charset="utf-8">
            var socket = io();
            socket.on('connect', function() {
                socket.emit('message', {data: 'Im connected!'});
            });
            socket.on('update value', function(msg) {
                console.log(msg.data + 'skjlioioopiipio');
            });
            socket.on('message', function(msg) {
                console.log(msg.data + 'skjlioioopiipio');
            });
        </script>


    </head>
    <body>
        <h1>BigTest</h1>
        <p id="p1"></p>
    </body>
</html>
"""



html2 = """
<html>
    <head>
        <title>Mi Big Flask Test</title>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <script type="text/javascript">
            var x = 0;
            var intervalId1 = setInterval(getAndPost, 500);
            function getAndPost() {
                if (x >= 10) {
                    clearInterval(intervalId1);
                }
                if (x % 2 == 1) {
                    console.log("before get request");
                    $.get('/app', { 'data' : '1234' }, (data, textStatus, jqXHR) => {
                        document.getElementById('p1').innerHTML = data;
                    })
                    console.log("after get request");
                } else {
                    $.post('/app', { 'data' : '1234' }, (data, textStatus, jqXHR) => {
                        document.getElementById('p1').innerHTML = data;
                    })
                }
                x++;
            }
        </script>
    </head>
    <body>
        <h1>BigTest</h1>
        <p id="p1"></p>
    </body>
</html>
"""