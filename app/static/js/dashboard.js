`use strict`

const distance = document.getElementById("distanceToday")
const userName = document.getElementById("userName")
const milesThisWeek = document.getElementById("distanceThisWeek")
const logoutBtn = document.querySelector(".logout")


async function getUser(){
    try{
        const response = await fetch("http://127.0.0.1:8000/user")
        if(!response.ok){
            throw new Error(`Http error! status: ${response.status}`)
        }
        const userData = await response.json() 
        
        const firstName = userData['firstname']
        const lastName = userData['lastname']
        const fullName = firstName + " " + lastName
        userName.textContent = fullName
    }catch (error){
        console.log("Error fetching user:", error)
    }
}

async function getMilesThisWeek() {
    try{
        const response = await fetch("http://127.0.0.1:8000/activities")
        if(!response.ok){
            throw new Error(`Http error! status: ${response.status}`)
        }
        const milesRanMeters = await response.json()
        const milesRan = Math.round((milesRanMeters / 1609.344) * 100 ) / 100
        milesThisWeek.textContent = milesRan
    } catch(error){
        console.log("Error getting miles:", error)
    }
}

document.addEventListener('DOMContentLoaded', async function() {
    await getUser(); // Load user data when page is ready
    await getMilesThisWeek();
});

logoutBtn.addEventListener('click', async function(){
    try{
        const response = await fetch('http://127.0.0.1:8000/logout', {
            method: 'POST'
        });
        if(response.ok){
            window.location.href = '/';
        }
    } catch(e){
        console.log("Logout failed", e)
    }
})



