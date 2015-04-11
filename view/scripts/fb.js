
$(document).ready(function() {
	console.log('jQuery works !!');
	
	$.ajaxSetup({ cache: true });
	$.getScript('//connect.facebook.net/en_UK/all.js', function(){
	FB.init({
	 appId      : '977141175653638',
	 cookie     : true,  // enable cookies to allow the server to access 
	                     // the session
	 status  : true, // check login status
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
   	sample(accessToken, 
   		function() { 
   			console.log('Done');
   			return true 
   		},
   		function() {
   			auto_refresh = setInterval((function() {
					return sample(accessToken,
						function() { 
							clearInterval(auto_refresh) 
							console.log('Done');
						},
						function() { return false }
					);
				}), 5000);
			}
   	)
   	
 	});
}

function sample(accessToken, finishFunc, unfinishedFunc) {
	console.log('About to sample status.');
	$.ajax({
		type: 'POST',
		url: '../app/go',
		data: { fb_token : accessToken },
		dataType: 'json',
		success: function(data) {
			console.log(JSON.stringify(data));
			if (data.images) {
				rebuildApp(data.images)		
			}
			if (data.status >= 5) {
				return finishFunc()
			} else {
				return unfinishedFunc()
			}
		}
  });
}

