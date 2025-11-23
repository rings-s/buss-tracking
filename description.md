| Role     | Allowed            |
| -------- | ------------------ |
| Admin    | إدارة كل شيء       |
| Driver   | إرسال GPS فقط      |
| Employee | تسجيل check-in فقط |



# driver
- start trip

# employee 
- enter the bus
- touch the nfc and read his card
- django send the nfc uid 
- django record the time

# end trip
- driver end the trip
- django record the time



# nfc 
- `NFC Card → USB NFC Reader → Tablet App → POST request → Django`

# tabet 
- python script or svelte app 





# driver gps in frontend 

send the gps from the driver every 5 minutes

setInterval(async () => {
    const pos = await getLocation();

    await fetch('/api/bus/update-location', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({
            bus_id: 1,
            latitude: pos.lat,
            longitude: pos.lng
        })
    });
}, 5000);
