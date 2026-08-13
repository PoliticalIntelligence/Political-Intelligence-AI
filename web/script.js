// --------------------------------------------------
// MAP
// --------------------------------------------------

const map = L.map('map').setView([26.8,83.3],9);

L.tileLayer(

'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',

{

    attribution:'© OpenStreetMap'

}

).addTo(map);


// --------------------------------------------------
// LOAD JSON
// --------------------------------------------------

fetch("locations.json")

.then(response=>response.json())

.then(data=>{

    data.forEach(location=>{

        const marker =

        L.marker(

            [

                location.lat,

                location.lng

            ]

        ).addTo(map);

        marker.bindPopup(

            `

            <b>${location.place}</b>

            <br><br>

            ${location.category}

            <br><br>

            ${location.summary}

            `

        );

    });

});