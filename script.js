async function generate(){

let data = {

event_type: document.getElementById("event").value,
severity:"medium",
flight_no: document.getElementById("flight").value,
origin: document.getElementById("origin").value,
destination: document.getElementById("destination").value,
eta_change: parseInt(document.getElementById("delay").value),
gate:"A7",
runway:"09R",
notes:""

}

await fetch("/generate",{

method:"POST",
headers:{ "Content-Type":"application/json"},
body:JSON.stringify(data)

})

loadBoard()

}