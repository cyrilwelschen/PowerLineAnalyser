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

function measureVoltage() {
	console.log("start measureing voltages")
	console.log("measure AC")
	eel.sample_voltage_ac()(sampleVoltageAc)
	console.log("measure DC")
	eel.sample_voltage_dc()(sampleVoltageDc)
}

function sampleVoltageAc(e) {
	console.log("sampleVoltage");
	console.log("Return was " + e);
	document.getElementById("voltage_ac_a_gnd").innerHTML = e[0];
	document.getElementById("voltage_ac_b_gnd").innerHTML = e[1];
	document.getElementById("voltage_ac_a_b").innerHTML = e[2];
}

function sampleVoltageDc(r) {
	console.log("sampleVolgateDc")
	console.log("Return VDC was " + r)
	document.getElementById("voltage_dc_a_gnd").innerHTML = r[0];
	document.getElementById("voltage_dc_b_gnd").innerHTML = r[1];
	document.getElementById("voltage_dc_a_b").innerHTML = r[2];
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