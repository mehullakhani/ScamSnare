// Initialize map centered on India
const map = L.map('map').setView([20.5937, 78.9629], 5);

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
}).addTo(map);

// Try GPS first, fallback to IP
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            // Success: Use precise GPS
            showLocation(
                pos.coords.latitude, 
                pos.coords.longitude, 
                "Your Exact Location (GPS)"
            );
        },
        (err) => {
            // Failed: Use IP-based
            fetchLocation();
        }
    );
} else {
    // No GPS support
    fetchLocation();
}

function fetchLocation() {
    fetch(`/track?device=${encodeURIComponent(JSON.stringify({
        os: navigator.platform,
        browser: navigator.userAgent,
        screen: `${screen.width}x${screen.height}`
    }))}`)
    .then(res => res.json())
    .then(data => {
        showLocation(
            parseFloat(data.latitude),
            parseFloat(data.longitude),
            `Your Network Location (${data.city || data.region || data.country || 'Unknown'})`
        );
    });
}

function showLocation(lat, lng, label) {
    L.marker([lat, lng]).addTo(map)
        .bindPopup(`<b>${label}</b>`)
        .openPopup();
    map.setView([lat, lng], 13);
}