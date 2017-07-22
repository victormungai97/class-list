function getLocation(){
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(showPosition, showError);
		} else {
			alert("Geolocation is not supported by this browser");
		}
	}
	
	/**
	* Method to get the coordinates of current position
	*/
	function showPosition(position){
		document.getElementById("latitude").value = position.coords.latitude;
		document.getElementById("longitude").value = position.coords.longitude;
		//alert("Latitude: " + position.coords.latitude + ", Longitude: " + position.coords.longitude);
	}
	
	/**
	* Method to handle errors and rejections
	*/
	function showError(error){
		switch (error.code){
			case error.PERMISSION_DENIED: alert("User denied permission for Geolocation."); ;break;
			case error.POSITION_UNAVAILABLE: alert("Location information is unavailable."); break;
			case error.TIMEOUT: alert("The request to get user location timed out."); break;
			case error.UNKNOWN_ERROR: alert("An unknown error occurred."); break;
		}
		
		document.getElementById("latitude").value = 0;
		document.getElementById("longitude").value = 0;
	}