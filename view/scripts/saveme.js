
$.fn.random = function()
{
    var ret = $();

    if(this.length > 0)
        ret = ret.add(this[Math.floor((Math.random() * this.length))]);

    return ret;
};

$.fn.progressSet = function(precent)
{
	$(this).width(precent + '%')
};


function updateInitialDetails(response) {
	$('.userFirstName').append(response.first_name)
}

function updateStatus(status) {
	progressBar = $('#progressBar')
	var statusText = $('#bakeStatusSpan')
	statusText.empty()
	if(status >= 5) {
		progressBar.progressSet(100);
	} else {
		if(status < 0) { 
			$('.progress').hide()
		} else {
			progressBar.progressSet(status * 20);	
		}
		var status = $('#bakingStatuses_' + status).find('span').random()
		statusText.append(status)
	}
}


function rebuildApp(images, bakeStep) {
	$('div.flipbook-viewport').hide()
	buildAlbum(images, bakeStep)
	var firstPage = (Object.keys(images).length == 0) ? 1 : (Object.keys(images).length * 2) + 2
	loadApp(firstPage)
	$('div.flipbook-viewport').show()
}

function buildAlbum(images, bakeStep) {
	$('div.flipbook-container').empty()
	var myAlbum = $('<div class="flipbook">')

	if(Object.keys(images).length > 0) {
		var backCover = $('#back_cover_part').clone()
		backCover.attr('id', 'back_cover')
		backCover.attr('class', 'hard')	
		myAlbum.append(backCover)
	
		scenes = $('#scenes_data').children()
		
		$(scenes.get().reverse()).each(function(index) {
	
			scene_id = this['id']
		
			image = images[scene_id]
			text = $(this).find('span.scene_text_data').text()
			desc = $(this).find('span.image_desc_data').text()

			imgPageTag = $('#scene_img_page_part').clone()
			imgPageTag.removeAttr('id')
			if(index <= 0) {
				imgPageTag.attr('class', 'hard img_page')
			} else {			
				imgPageTag.attr('class', 'page img_page')
			}
			
			imgPageTag.find('.myimg').attr('src', image)
			imgPageTag.find('.myimg').attr('alt', scene_id)
			imgPageTag.find('.pp_descr span').append(desc)
			
			myAlbum.append(imgPageTag)
		
			txtPageTag = $('#scene_text_page_part').clone()
			txtPageTag.removeAttr('id')
			if(index >= scenes.length - 1) {
				txtPageTag.attr('class', 'hard text_page')
			} else {
				txtPageTag.attr('class', 'page text_page')
			}
			txtPageTag.find('span.phototext').append(text)
		
			myAlbum.append(txtPageTag)
		});
	}

	var frontCover = $('<div id="front_cover" class="hard">')
	frontCover.append($('#cover_header_pic_wrapper').clone())
	frontCover.append($('#cover_text_' + bakeStep).clone())
	if(bakeStep == 'done') {
		frontCover.append($('#front_cover_part .flipSymbol').clone())
	}
	myAlbum.append(frontCover)

	$('div.flipbook-container').append(myAlbum)
}

function loadApp(pages) {

	var w = 1600
	var h = 600
	var screenW = $( document ).width();
	
	if(screenW < 1200) {
		$('#fc_title').css('font-size','15px')
		$('#coverReadyText').css('font-size','17px')		
		$('#fc_remindme').css('font-size','6px')
		$('#connect_txt').css('font-size','10px')	
		$('#bake_status_words').css('font-size','12px')	
		w = 800
		h = 300
	} else if(screenW < 1600) {
		$('#fc_title').css('font-size','17px')
		$('#coverReadyText').css('font-size','19px')		
		$('#fc_remindme').css('font-size','8px')
		$('#connect_txt').css('font-size','12px')	
		$('#bake_status_words').css('font-size','14px')		
		w = 1000
		h = 375
	} else if(screenW < 1800)  {
		$('#fc_title').css('font-size','21px')
		$('#coverReadyText').css('font-size','23px')		
		$('#fc_remindme').css('font-size','12px')
		$('#connect_txt').css('font-size','16px')	
		$('#bake_status_words').css('font-size','18px')	
		w = 1200
		h = 450
	}
	
	if($( document ).width() < 1800) {
		$('.fb-login-button').attr('data-size', 'large')
		$('#connect').css('bottom','9%')				
		$('#connect_btn').css('bottom','')
	}
	
	console.log('book size :' + w + 'x' +h)

	// Create the flipbook

	$('.flipbook').turn({
			// Width

			width:w,
			
			// Height

			height:h,

			// Elevation

			elevation: 50,
			
			// Enable gradients

			gradients: true,
			
			// Auto center this flipbook

			autoCenter: true,

			page: pages
	});

}

// Load the HTML4 version if there's not CSS transform

yepnope({
	test : Modernizr.csstransforms,
	yep: ['scripts/turn.js'],
	nope: ['scripts/turn.html4.min.js'],
	both: ['css/basic.css'],
	complete: function() { return rebuildApp({}, 'login') }
});
