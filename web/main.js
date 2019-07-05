function generateQRCode() {
	var data = document.getElementById("data").value
	eel.generate_qr(data)(setImage)
}

function setImage(base64) {
	document.getElementById("qr").src = base64
}

function browseResult(e) {
	var fileselector = document.getElementById('fileselector');
	console.log(fileselector.value);
}

function saveEmail() {
	var mail = document.getElementById('email_input').value;
	if (mail != "") {
		console.log("Entered Email")
		window.location.pathname = '/web/measurement_main.html'
	} else {
		alert("please Enter valid mail")
	}
}