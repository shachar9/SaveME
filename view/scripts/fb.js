$(document).ready(function() {
	console.log('jQuery works !!');
	
	$.ajaxSetup({ cache: true });
	$.getScript('//connect.facebook.net/en_UK/all.js', function(){
	FB.init({
	 appId      : '977141175653638',
	 cookie     : true,  // enable cookies to allow the server to access 
	                     // the session
	 xfbml      : true,  // parse social plugins on this page
	 version    : 'v2.2' // use version 2.2
	});     
	$('#loginbutton,#feedbutton').removeAttr('disabled');
	FB.getLoginStatus(statusChangeCallback);
  });
});

function checkLoginState() {
 FB.getLoginStatus(function(response) {
	statusChangeCallback(response);
 });
}

function statusChangeCallback(response) {
 	console.log('statusChangeCallback');
 	console.log(response);
 	// The response object is returned with a status field that lets the
 	// app know the current login status of the person.
 	// Full docs on the response object can be found in the documentation
 	// for FB.getLoginStatus().
 	if (response.status === 'connected') {
   // Logged into your app and Facebook.
   console.log(response.authResponse.accessToken);
   testAPI(response.authResponse.accessToken);
 	} else if (response.status === 'not_authorized') {
   	// The person is logged into Facebook, but not your app.
   	document.getElementById('status').innerHTML = 'Please log ' +
     	'into this app.';
	} else {
   	// The person is not logged into Facebook, so we're not sure if
   	// they are logged into this app or not.
   	document.getElementById('status').innerHTML = 'Please log ' +
     		'into Facebook.';
	}
}	

var auto_refresh = null;
function testAPI(accessToken) {
 	console.log('Welcome!  Fetching your information.... ');
 	FB.api('/me', function(response) {
   console.log('Successful login for: ' + response.name);
   document.getElementById('status').innerHTML =
     'Thanks for logging in, ' + response.name + '!';
 	});
	

	auto_refresh = setInterval((function() {
		return sample(accessToken);
	}), 5000);

}

function sample(accessToken) {
	$.ajax({
		type: 'POST',
		url: 'app/go',
		data: { fb_token : accessToken },
		dataType: 'json',
		success: function(data) {
			console.log(JSON.stringify(data));
			document.getElementById('status').innerHTML =  'Status ' + data.status
			if (data.images) {
				buildAlbum(data.images)
				loadPolaroid()
			}
			if (data.status >= 5) {
				clearInterval(auto_refresh)
			}
		}
  });
}

function buildAlbum(images) {
	var myAlbum = $('#pp_thumbContainer div.album')
	myAlbum.empty()

	for(image_id in images) {
		contentTag = $('<div>')
		contentTag.attr('class', 'content')
		image = images[image_id]
		imgTag = $('<img>')
		imgTag.attr('alt', image)
		imgTag.attr('src', image)
		contentTag.append(imgTag)
		spanTag = $('<span>')
		spanTag.append(image_id)
		contentTag.append(spanTag)
		myAlbum.append(contentTag)
	};

	descrTag = $('<div>')
	descrTag.attr('class', 'descr')
	descrTag.append('Wedding Pics')
	myAlbum.append(descrTag)
	
}
