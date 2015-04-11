function rebuildApp(images) {
	$('div.flipbook-viewport').hide()
	buildAlbum(images)
	loadApp((Object.keys(images).length * 2) + 2)
	$('div.flipbook-viewport').show()	
}

function buildAlbum(images) {
	$('div.container').empty()
	var myAlbum = $('<div class="flipbook">')
	var backCover = $('#back_cover_part').clone()
	backCover.attr('id', 'back_cover')
	backCover.attr('class', 'hard')	
	myAlbum.append(backCover)

	if(Object.keys(images).length > 0) {
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

	//myAlbum.append(frontCover)
	var frontCover = $('#front_cover_part').clone()
	frontCover.attr('id', 'front_cover')
	frontCover.attr('class', 'hard')	
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
	complete: function() { return rebuildApp({}) }
});

