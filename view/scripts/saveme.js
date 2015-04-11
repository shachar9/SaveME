
$.fn.random = function()
{
    var ret = $();

    if(this.length > 0)
        ret = ret.add(this[Math.floor((Math.random() * this.length))]);

    return ret;
};


function updateInitialDetails(response) {
	$('#userFirstName').append(response.first_name)
}

/*
$(document).ready(function(){
	var controlButton = $('#controlButton').progressInitialize();
}
*/
/*
function setProgress(percentage) {
	var bar = $('#controlButton').find('span')
	bar.filter('.background-horizontal,.background-bar').width(percentage+'%');
	bar.filter('.background-vertical').height(percentage+'%');
}
*/

//var controlButton = $('#controlButton').progressInitialize();
function updateStatus(status) {
	//var controlButton = $('#controlButton')
	var statusText = $('#bakeStatusSpan')
	statusText.empty()
	if(status >= 5) {
		//controlButton.progressFinish();
	} else {
		//controlButton.progressSet(status * 20);
		var status = $('#bakingStatuses_' + status).find('span').random()
		statusText.append(status.text())
	}
}

function rebuildApp(images, bakeStep) {
	$('div.flipbook-viewport').hide()
	buildAlbum(images, bakeStep)
	//loadApp((Object.keys(images).length * 2) + 2)
	loadApp(1)
	$('div.flipbook-viewport').show()
}

function buildAlbum(images, bakeStep) {
	$('div.container').empty()
	var myAlbum = $('<div class="flipbook">')

	if(Object.keys(images).length > 0) {
		var backCover = $('#back_cover_part').clone()
		backCover.attr('id', 'back_cover')
		backCover.attr('class', 'hard')	
		myAlbum.append(backCover)
	
		scenes = $('#scenes_data').children()
		
		$(scenes.get().reverse()).each(function() {
	
			scene_id = this['id']
		
			image = images[scene_id]
			text = $(this).find('span.scene_text_data').text()
			desc = $(this).find('span.image_desc_data').text()

			imgPageTag = $('#scene_img_page_part').clone()
			imgPageTag.removeAttr('id')
			imgPageTag.attr('class', 'page img_page')
			imgPageTag.find('.myimg').attr('src', '../' + image)
			imgPageTag.find('.myimg').attr('alt', scene_id)
			imgPageTag.find('.pp_descr span').append(desc)
			
			myAlbum.append(imgPageTag)
		
			txtPageTag = $('#scene_text_page_part').clone()
			txtPageTag.removeAttr('id')
			txtPageTag.attr('class', 'page text_page')
			txtPageTag.find('span.phototext').append(text)
		
			myAlbum.append(txtPageTag)
		});
	}

	var frontCover = $('<div id="front_cover" class="hard">')
	frontCover.append($('#cover_header_pic_wrapper').clone())
	frontCover.append($('#cover_text_' + bakeStep).clone())
	myAlbum.append(frontCover)

	$('div.container').append(myAlbum)
}

function loadApp(pages) {

	// Create the flipbook

	$('.flipbook').turn({
			// Width

			width:1600,
			
			// Height

			height:600,

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
