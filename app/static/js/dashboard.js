'use strict'

const userName = document.getElementById("userName")
const userAvatar = document.getElementById("userAvatar")
const milesThisWeek = document.getElementById("distanceThisWeek")
const goalDistance = document.getElementById("goalDistance")
const statusCard = document.getElementById("statusCard")
const statusEmoji = document.getElementById("statusEmoji")
const statusTitle = document.getElementById("statusTitle")
const statusSubtitle = document.getElementById("statusSubtitle")
const progressFill = document.getElementById("progressFill")
const progressText = document.getElementById("progressText")
const logoutBtn = document.querySelector(".logout")

async function getUser(){
    try{
        const response = await fetch("http://127.0.0.1:8000/user")
        if(!response.ok){
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        const userData = await response.json() 
        
        const firstName = userData['firstname']
        const lastName = userData['lastname']
        const fullName = firstName + " " + lastName
        
        // Update user name
        userName.textContent = fullName
        
        // Update avatar with initials
        const initials = firstName.charAt(0) + lastName.charAt(0)
        userAvatar.textContent = initials.toUpperCase()
        
    }catch (error){
        console.log("Error fetching user:", error)
    }
}

async function getMilesThisWeek() {
    try{
        const response = await fetch("http://127.0.0.1:8000/check-goal")
        if(!response.ok){
            throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        
        // Update miles display
        milesThisWeek.textContent = data.actual_miles.toFixed(1)
        goalDistance.textContent = data.goal_miles.toFixed(1)
        
        // Update progress bar
        const percentage = Math.min(data.percentage, 100) // Cap at 100%
        progressFill.style.width = percentage + '%'
        progressText.textContent = `${percentage.toFixed(0)}% complete`
        
        // Update status card based on goal
        if (data.goal_met) {
            statusCard.className = 'status-card allowed'
            statusEmoji.textContent = '🎮'
            statusTitle.textContent = 'Steam Unlocked!'
            statusSubtitle.textContent = `Great job! You ran ${data.actual_miles.toFixed(1)} miles this week`
        } else {
            statusCard.className = 'status-card blocked'
            statusEmoji.textContent = '🔒'
            statusTitle.textContent = 'Steam Blocked'
            statusSubtitle.textContent = `Run ${data.remaining_miles.toFixed(1)} more miles to unlock gaming`
        }
        
    } catch(error){
        console.log("Error getting miles:", error)
    }
}

function refreshStatus() {
    getMilesThisWeek()
}

function editGoal() {
    const goalInput = document.getElementById("goalInput")
    const currentGoal = document.getElementById("goalDistance").textContent
    
    goalInput.value = currentGoal
    document.getElementById("goalDisplay").classList.add("hidden")
    document.getElementById("goalEdit").classList.remove("hidden")
    goalInput.focus()
}

function cancelEdit() {
    document.getElementById("goalDisplay").classList.remove("hidden")
    document.getElementById("goalEdit").classList.add("hidden")
}

async function saveGoal() {
    const newGoal = parseFloat(document.getElementById("goalInput").value)
    
    if (isNaN(newGoal) || newGoal <= 0) {
        alert("Please enter a valid goal")
        return
    }
    
    try {
        // TODO: Add endpoint to update goal in backend
        // For now, just update the display
        document.getElementById("goalDistance").textContent = newGoal.toFixed(1)
        cancelEdit()
        
        // Refresh to recalculate percentages
        await getMilesThisWeek()
        
    } catch(error) {
        console.log("Error updating goal:", error)
        alert("Failed to update goal")
    }
}

function openStrava() {
    window.open('https://www.strava.com/athlete/training', '_blank')
}

document.addEventListener('DOMContentLoaded', async function() {
    await getUser()
    await getMilesThisWeek()
})

logoutBtn.addEventListener('click', async function(e){
    e.preventDefault()
    try{
        const response = await fetch('http://127.0.0.1:8000/logout', {
            method: 'POST'
        })
        if(response.ok){
            window.location.href = '/'
        }
    } catch(e){
        console.log("Logout failed", e)
    }
})