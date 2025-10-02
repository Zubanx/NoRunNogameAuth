'use strict'

let loginBtn = document.querySelector(".strava-btn")


loginBtn.addEventListener('click', function(){
    window.location.href = "http://localhost:8000/login";
});