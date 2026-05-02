let chart;

function updateChart(data){

let delays = data.map(d=>d.delay)
let flights = data.map(d=>d.flight)

if(chart) chart.destroy()

chart = new Chart(document.getElementById("chart"),{

type:"bar",

data:{
labels:flights,
datasets:[{
data:delays,
backgroundColor:"#3b82f6"
}]
},

options:{
plugins:{legend:{display:false}},
scales:{
x:{display:false},
y:{display:false}
}

}

})

}