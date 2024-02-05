var interval;


function startTimer() {

    var startTime = Date.now();
    //console.log('startTime: ', startTime)

    interval = setInterval(function() {
        var elapsedTime = Date.now() - startTime;
        document.getElementById("msHiddenTimer").value = (elapsedTime / 1000).toFixed(3);
        document.getElementById("timer").innerHTML = msToTime(elapsedTime); //elapsedTime의 단위는 밀리초이다. 이걸 hh:mm:ss 형식으로 바꿔줌
    }, 100);

}

function restartTimer() {

    var startTime = Date.now();
    //console.log('startTime: ', startTime)

    var previousTime = parseFloat(document.getElementById("msHiddenTimer").value); //정수형으로 변환
    //console.log('previousTime: ' + previousTime);
    previousTime *= 1000; //밀리초단위로 만들어줌
    //console.log('previousTime: ' + previousTime);

    interval = setInterval(function() {

        var elapsedTime = Date.now() - startTime;
        elapsedTime += previousTime; //왜안될까...(parseFloat로했어야하는데 parseInt로 해서 정수값만 뜯어서 안됐었던 것임)
        //console.log('previousTime: ' + previousTime);

        document.getElementById("msHiddenTimer").value = (elapsedTime/1000).toFixed(3);
        document.getElementById("timer").innerHTML = msToTime(elapsedTime);
        //console.log(elapsedTime);
    }, 100);

}

function pauseTimer() {
    document.getElementById("hiddenTimer").value = document.getElementById("msHiddenTimer").value
    clearInterval(interval);
}


function stopTimer() {
    clearInterval(interval);
}


//밀리초를 hh:mm:ss (또는 hh:mm:ss:S) 형식으로 만들어줌
function msToTime(duration) {
    //var milliseconds = parseInt((duration%1000)/100);
    var seconds = parseInt((duration/1000)%60);
    var minutes = parseInt((duration/(1000*60))%60);
    var hours = parseInt((duration/(1000*60*60))%24);

    hours = (hours < 10) ? "0" + hours : hours;
    minutes = (minutes < 10) ? "0" + minutes : minutes;
    seconds = (seconds < 10) ? "0" + seconds : seconds;

    //return hours + ":" + minutes + ":" + seconds + "." + milliseconds;
    return hours + ":" + minutes + ":" + seconds;
}


