async function loadBoard(){

let res = await fetch("/incidents")
let data = await res.json()

let table = document.getElementById("table")

table.innerHTML=""

data.forEach(f => {

let row = document.createElement("tr")

row.innerHTML = `
<td>${f.flight}</td>
<td>${f.origin} → ${f.destination}</td>
<td>${f.status}</td>
<td>${f.delay}</td>
`

table.appendChild(row)

})

updateChart(data)

}

loadBoard()