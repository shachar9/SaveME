function loadPolaroid() {
	var ie 			= false;

	if ($.browser.msie) {
		ie = true;
	}

	//current album/image displayed
	var current		= -1;
	var album		= -1;
	//windows width
	var w_width 	= $(window).width();
	//caching
	var $album 	= $('#pp_thumbContainer div.album').first();
	var $loader		= $('#pp_loading');
	var $next		= $('#pp_next');
	var $prev		= $('#pp_prev');
	var $images		= $('#pp_thumbContainer div.content img');
	var $back		= $('#pp_back');

	//var nmb_albums	= $albums.length;
	//var spaces 		= w_width/(nmb_albums+1);
	var cnt			= 0;
	//preload all the images (thumbs)
	var nmb_images	= $images.length;
	var loaded  	= 0;
	$images.each(function(i){
		var $image = $(this);
		$('<img />').load(function(){
			//++loaded;
			//if(loaded == nmb_images){
				//let's spread the albums evenly at the bottom of the page
				/*
				$albums.each(function(){
					var $this 	= $(this);
					++cnt;
					var left	= spaces*cnt - $this.width()/2;
					$this.css('left',left+'px');
					$this.stop().animate({'bottom':'0px'},500);
				}).unbind('click').bind('click',spreadPictures);
				*/
				//also rotate each picture of an album with a random number of degrees
				$images.each(function(){
					var $this = $(this);
					var r = Math.floor(Math.random()*41)-20;
					$this.transform({'rotate'	: r + 'deg'});
				});
			//}
		}).attr('src', $image.attr('src'));
	});

	function spreadPictures(){
		//var $album = $(this);
		//track which album is opened
		album = $album.index();
		//hide all the other albums
//		$albums.not($album).stop().animate({'bottom':'-90px'},300);
			$album.unbind('click');
			//now move the current album to the left
			//and at the same time spread its images throughout
			//the window, rotating them randomly, hide the description of the album

		//store the current left for the reverse operation
		$album.data('left',$album.css('left'))
			  .stop()
			  .animate({'left':'0px'},500)
			  .find('.descr')
			  .stop()
			  .animate({'bottom':'-30px'},200);
			var total_pic 	= $album.find('.content').length;
			var cnt			= 0;
			//each picture
			$album.find('.content')
				  .each(function(){
				var $content = $(this);
				++cnt;
				//window width
				var w_width 	= $(window).width();
				var spaces 		= w_width/(total_pic+1);
				var left		= (spaces*cnt) - (140/2);
				var r 			= Math.floor(Math.random()*41)-20;
				//var r = Math.floor(Math.random()*81)-40;
			$content.stop().animate({'left':left+'px'},500,function(){
				$(this).unbind('click')
							.bind('click',showImage)
							.unbind('mouseenter')
							.bind('mouseenter',upImage)
							.unbind('mouseleave')
							.bind('mouseleave',downImage);
			}).find('img')
			  .stop()
			  .animate({'rotate': r+'deg'},300);
			$back.stop().animate({'left':'0px'},300);
				});
	}

	$back.bind('click',function(){
		$back.stop().animate({'left':'-100px'},300);
		hideNavigation();
		//there's a picture being displayed
		//lets slide the current one up
		if(current != -1){
			hideCurrentPicture();
		}

		var $current_album = $('#pp_thumbContainer div.album:nth-child('+parseInt(album+1)+')');
		$current_album.stop()
					  .animate({'left':$current_album.data('left')},500)
					  .find('.descr')
					  .stop()
					  .animate({'bottom':'0px'},500);

		$current_album.unbind('click')
					  .bind('click',spreadPictures);

		$current_album.find('.content')
				  .each(function(){
					var $content = $(this);
					$content.unbind('mouseenter mouseleave click');
					$content.stop().animate({'left':'0px'},500);
			});

		//$albums.not($current_album).stop().animate({'bottom':'0px'},500);
		});

	function showImage(nav){
		if(nav == 1){
			//reached the first one
			if(current==0){
				return;
			}
			var $content = //$('#pp_thumbContainer div.album:nth-child('+parseInt(album+1)+')')
								$album
							.find('.content:nth-child('+parseInt(current)+')');
			//reached the last one
			if($content.length==0){
				current-=2;
				return;
			}
		}
		else
		var $content 	= $(this);

		//show ajax loading image
		$loader.show();

		//there's a picture being displayed
		//lets slide the current one up
		if(current != -1){
			hideCurrentPicture();
		}

		current 				= $content.index();
		var $thumb				= $content.find('img');
		var imgL_source 	 	= $thumb.attr('alt');
		var imgL_description 	= $thumb.next().html();
		//preload the large image to show
		$('<img style=""/>').load(function(){
			var $imgL 	= $(this);
			//resize the image based on the windows size
			resize($imgL);
			//create an element to include the large image
			//and its description
			var $preview = $('<div />',{
				'id'		: 'pp_preview',
				'className'	: 'pp_preview',
				'html'     	: '<div class="pp_descr"><span>'+imgL_description+'</span></div>',
				'style'		: 'visibility:hidden;'
		});
			$preview.prepend($imgL);
			$('#pp_gallery').prepend($preview);
			var largeW 	= $imgL.width()+20;
			var largeH 	= $imgL.height()+10+45;
			//change the properties of the wrapping div
			//to fit the large image sizes
			$preview.css({
				'width'			:largeW+'px',
				'height'		:largeH+'px',
				'marginTop'		:-largeH/2-20+'px',
				'marginLeft'	:-largeW/2+'px',
				'visibility'	:'visible'
			});
			Cufon.replace('.pp_descr');
			//show navigation
			showNavigation();

			//hide the ajax image loading
			$loader.hide();

			//slide up (also rotating) the large image
			var r 			= Math.floor(Math.random()*41)-20;
			if(ie)
				var param = {
					'top':'50%'
				};
			else
				var param = {
					'top':'50%',
					'rotate': r+'deg'
				};
			$preview.stop().animate(param,500);
		}).error(function(){
			//error loading image.
			//Maybe show a message : 'no preview available'
		}).attr('src',imgL_source);
	}

	//click next image
	$next.bind('click',function(){
		current+=2;
		showImage(1);
	});

	//click previous image
	$prev.bind('click',function(){
		showImage(1);
	});

	//slides up the current picture
	function hideCurrentPicture(){
		current = -1;
		var r 	= Math.floor(Math.random()*41)-20;
		if(ie)
			var param = {
				'left':'-100%'
			};
		else
			var param = {
				'left':'-100%',
				'rotate': r+'deg'
			};
		$('#pp_preview').stop()
						.animate(param,500,function(){
							$(this).remove();
						});
	}

	//shows the navigation buttons
	function showNavigation(){
		$next.stop().animate({'right':'0px'},100);
		$prev.stop().animate({'left':'0px'},100);
	}

	//hides the navigation buttons
	function hideNavigation(){
		$next.stop().animate({'right':'-40px'},300);
		$prev.stop().animate({'left':'-40px'},300);
	}

	function upImage(){
		var $content 	= $(this);
		$content.stop().animate({
			'marginTop'		: '-70px'
		},400).find('img')
			  .stop()
			  .animate({'rotate': '0deg'},400);
	}

	function downImage(){
		var $content 	= $(this);
		var r 			= Math.floor(Math.random()*41)-20;
		$content.stop().animate({
			'marginTop'		: '0px'
		},400).find('img').stop().animate({'rotate': r + 'deg'},400);
	}

	function resize($image){
		var widthMargin		= 50
		var heightMargin 	= 200;

		var windowH      = $(window).height()-heightMargin;
		var windowW      = $(window).width()-widthMargin;
		var theImage     = new Image();
		theImage.src     = $image.attr("src");
		var imgwidth     = theImage.width;
		var imgheight    = theImage.height;

		if((imgwidth > windowW)||(imgheight > windowH)){
			if(imgwidth > imgheight){
				var newwidth = windowW;
				var ratio = imgwidth / windowW;
				var newheight = imgheight / ratio;
				theImage.height = newheight;
				theImage.width= newwidth;
				if(newheight>windowH){
					var newnewheight = windowH;
					var newratio = newheight/windowH;
					var newnewwidth =newwidth/newratio;
					theImage.width = newnewwidth;
					theImage.height= newnewheight;
				}
			}
			else{
				var newheight = windowH;
				var ratio = imgheight / windowH;
				var newwidth = imgwidth / ratio;
				theImage.height = newheight;
				theImage.width= newwidth;
				if(newwidth>windowW){
					var newnewwidth = windowW;
					var newratio = newwidth/windowW;
					var newnewheight =newheight/newratio;
					theImage.height = newnewheight;
					theImage.width= newnewwidth;
				}
			}
		}
		$image.css({'width':theImage.width+'px','height':theImage.height+'px'});
	}

	$('#pp_thumbContainer').hide()
	spreadPictures()
	current = 1
	showImage(1)
}

