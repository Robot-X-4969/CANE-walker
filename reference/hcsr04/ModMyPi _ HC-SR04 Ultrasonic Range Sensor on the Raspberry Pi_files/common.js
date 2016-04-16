(function ($) {
	$.fn.listHeights = function (options) {
		var _this = $(this);
		var defaults = {item: ".news", offset: 0};
		var settings = $.extend({}, defaults, options);
		var delay = 0;
		var length = $(_this).find(settings.item).length;

		function getHeight(animate) {
			$(_this).find(settings.item).css('height', '');
			var height = 0;
			var start = 0;
			$(_this).find(settings.item).each(function (i, e) {
				$(e).show();
				if ($(e).height() + settings.offset > height) {
					height = $(e).height() + settings.offset;
				}
				$(e).hide();
				if ($(e).nextUntil(settings.item, '.cb').is(':visible') || i == length - 1) {
					setHeight(start, i, height, animate);
					start = i + 1;
					height = 0;
				}
			});
		}

		function setHeight(start, end, height, animate) {
			$(_this).find(settings.item).each(function (i, e) {
				if (i >= start && end >= i) {
					if (animate) {
						$(e).css('visibility', 'visible').height(height).delay(delay).fadeIn();
						delay += 200;
					} else {
						$(e).height(height).show();
					}
				}
			});
		}

		getHeight(true);
		$(window).on("resize.listHeights", function () {
			getHeight(false);
		});
	}
})(jQuery);

/* functions */
function tbFocus(obj, objval) {
	$(obj).removeClass('error');
	if (obj.value == objval) {
		obj.value = "";
	}
}

function tbBlur(obj, objval) {
	if (obj.value == "") {
		obj.value = objval;
	}
}

function validateEmail(elementValue) {
	var emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
	return emailPattern.test(elementValue);
}

var files;

function prepareUpload(event) {
	files = event.target.files;
}

function uploadFiles($form) {
	var data = new FormData();

	console.log("processing files!");

	$.each(files, function (key, value) {
		data.append(key, value);
	});

	$.ajax({
		url: '/contact-us?files',
		type: 'POST',
		data: data,
		cache: false,
		processData: false,
		contentType: false,
		success: function (data, textStatus, jqXHR) {
			console.log(data);
			if (typeof data.error === 'undefined') {
				contactAjax($form);
			}
			else {
				console.log('ERRORS: ' + data.error);
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			console.log('ERRORS: ' + textStatus);
		}
	});

}

function contactAjax($form) {
	var data = "";
	$form.find("input, textarea").each(function (index, element) {
		if ($(this).attr('type') == "checkbox") {
			if ($(this).prop('checked')) {
				data = data + $(this).attr('name') + "=" + encodeURIComponent($(this).val()) + "&";
			} else {
				data = data + $(this).attr('name') + "=" + "false" + "&";
			}
		} else if ($(this).attr('type') != "radio") {
			if ($(this).attr('type') == "file") {
				if ($(element).closest('div').hasClass('contact_drop') && !$(element).parent().hasClass('hide')) {
					data = data + $(this).attr('name') + "=" + $(this).val().replace("C:\\fakepath\\", "") + "&";
				}

			} else {
				if ($(element).closest('div').hasClass('contact_drop') && !$(element).parent().hasClass('hide')) {
					data = data + $(this).attr('name') + "=" + encodeURIComponent($(this).val()) + "&";
				}
				if (!$(element).closest('div').hasClass('contact_drop')) {
					data = data + $(this).attr('name') + "=" + encodeURIComponent($(this).val()) + "&";
				}
			}
		}
	});

	$form.find("select").each(function (index, element) {
		$(element).find('option').each(function (ind, opt) {
			if ($(element).closest('div').hasClass('contact_drop') && !$(element).parent().hasClass('hide')) {
				if ($(opt).is(':selected') && $(opt).val() != "") {
					data = data + $(element).attr('name') + "=" + encodeURIComponent($(opt).val()) + "&";
				}
			}
			if (!$(element).closest('div').hasClass('contact_drop')) {
				if ($(opt).is(':selected') && $(opt).val() != "") {
					data = data + $(element).attr('name') + "=" + encodeURIComponent($(opt).val()) + "&";
				}
			}
		});
	});

	$.ajax({
		url: "/contact-us",
		type: 'POST',
		data: data,
		success: function (json) {
			console.log(json);
			var obj = $.parseJSON(json);
			if (obj.error != "") {
				alert(obj.error);
			} else {
				$('#contact_form').before(obj.yay);
				$form.slideUp();
			}
		},
		error: function (jqXHR, textStatus, errorThrown) {
			console.log('ERRORS: ' + textStatus);
		}
	});
}

function contactSubmit(form, ajax) {
	var $form = $('#' + form);
	var submitform = true;
	var hasfiles = false;
	$form.find("input, textarea").each(function (index, element) {
		$(element).removeClass('error');
		if ($(element).data('required') === true) {
			if ($(element).val() == "" || $(element).val() == $(element).data('value')) {
				$(element).addClass('error');
				submitform = false;
			}
		}
		if ($(element).attr('type') == "file") {
			if ($(element).closest('div').hasClass('contact_drop') && !$(element).parent().hasClass('hide')) {
				hasfiles = true;
			}
		}
		if ($(element).attr('type') == 'email') {
			var validemail = validateEmail($(element).val());
			if (!validemail) {
				$(element).addClass('error');
				submitform = false;
			}
		}
	});
	$form.find("select").each(function (index, element) {
		$(element).closest('.select').removeClass('error');
		if ($(element).data('required') === true) {
			var selected = false;
			$(element).find('option').each(function (ind, opt) {
				if ($(opt).is(':selected') && $(opt).val() != "") {
					selected = true;
				}
			});
			if (!selected) {
				$(element).closest('.select').addClass('error');
				submitform = false;
			}
		}
	});

	if (ajax) {
		if (submitform) {
			if (files) {
				uploadFiles($form);
			} else {
				contactAjax($form);
			}
		}
		return false;
	} else {
		return submitform;
	}
}

function getURLVar(key) {
	var value = [];
	var query = String(document.location).split('?');

	if (query[1]) {
		var part = query[1].split('&');
		for (var i = 0; i < part.length; i++) {
			var data = part[i].split('=');
			if (data[0] && data[1]) value[data[0]] = data[1];
		}
		return value[key] ? value[key] : "";
	}
}

function addToCart(product_id, quantity) {
	quantity = typeof(quantity) != 'undefined' ? quantity : 1;
	$.ajax({
		url: 'index.php?route=checkout/cart/add',
		type: 'post',
		data: 'product_id=' + product_id + '&quantity=' + quantity,
		dataType: 'json',
		success: function (json) {
			$('.success, .warning, .attention, .information, .error').remove();
			if (json['redirect']) window.location = json['redirect'];
			if (json['success']) {
				$('#notification').html('<div class="success">' + json['success'] + '<img src="catalog/view/theme/default/image/close.png" alt="" class="close" /></div>');
				$('#notification').fadeIn('slow');
				$('.cart-total').html(json['total']);
			}
		}
	});
	return false;
}

function addToWishList(product_id) {
	$.ajax({
		url: 'index.php?route=account/wishlist/add',
		type: 'post',
		data: 'product_id=' + product_id,
		dataType: 'json',
		success: function (json) {
			$('.success, .warning, .attention, .information').remove();
			if (json['success']) {
				$('#notification').html('<div class="success">' + json['success'] + '<img src="catalog/view/theme/default/image/close.png" alt="" class="close" /></div>');
				$('#notification').fadeIn('slow');
				$('.wishlist-total').html(json['total']);
			}
		}
	});
}

function addToCompare(product_id) {
	$.ajax({
		url: 'index.php?route=product/compare/add',
		type: 'post',
		data: 'product_id=' + product_id,
		dataType: 'json',
		success: function (json) {
			$('.success, .warning, .attention, .information').remove();
			if (json['success']) {
				$('#notification').html('<div class="success">' + json['success'] + '<img src="catalog/view/theme/default/image/close.png" alt="" class="close" /></div>');
				$('#notification').fadeIn('slow');
				$('#compare-total').html(json['total']);
			}
		}
	});
}

$(function () {

	/* Search */
	var showSearch = function () {
		$('#search .expand').stop(true, false).animate({width: 234, 'padding-right': 10}, 500);
	};

	var hideSearch = function () {
		$('#search .expand').delay(500).animate({width: 0, 'padding-right': 0}, 500);
		if ($('#search').width() > 50) {
			$('#search').delay(500).animate({width: 50}, 500);
		}
	};

	$('#search .show-search').on('mouseenter.search', showSearch);
	$('#search .show-search').on('mouseleave.search', hideSearch);
	$('#search input').focus(function () {
		$('#search .expand').stop(true, false).css({width: 234, 'padding-right': 10});
		$('#search .show-search').off('mouseleave.search');

	});

	$('#search input').blur(function () {
		$('#search .expand').delay(500).animate({width: 0, 'padding-right': 0}, 500);
		$('#search .show-search').on('mouseleave.search', hideSearch);
	});

	$('#search input').hover(
		function () {
			$('#search .expand').stop(true, false).css({width: 234, 'padding-right': 10});
			$('#search .show-search').off('mouseleave.search');
		},
		function () {
			$('#search .expand').delay(500).animate({width: 0, 'padding-right': 0}, 500);
			$('#search .show-search').on('mouseleave.search', hideSearch);
		}
	)

	$('.button-search').on('click', function () {
		var url = $('base').attr('href') + 'index.php?route=product/search';
		var search = $(this).siblings('input[name=\'search\']').attr('value');
		search = search.replace("+","%2B");
		if (search) url += '&search=' + encodeURIComponent(search);
		window.location = url;
	});

	$('#mobile-search-icon').click(function () {
		$('#mobile-search').slideToggle();
	});

	$('header input[name=\'search\']').on('keydown', function (e) {
		if (e.keyCode == 13) {
			var url = $('base').attr('href') + 'index.php?route=product/search';
			var search = $(this).attr('value');
			search = search.replace("+","%2B");
			if (search) url += '&search=' + encodeURIComponent(search);
			window.location = url;
		}
	});

	/* mobile nav */
	$('#nav-icon').click(function () {
		if ($(this).hasClass('open')) {
			$('#holdall').animate({'margin-left': 0}, function () {
				$(this).removeAttr('style');
				$('#mobile-nav').hide();
			});
			$(this).removeClass('open').find('img').attr('src', '/catalog/view/theme/modmypi/images/nav-icon.png');
		} else {
			$('#mobile-nav').show();
			$('#holdall').css({'position': 'fixed', 'top': 0}).animate({'margin-left': '-60%'});
			$(this).addClass('open').find('img').attr('src', '/catalog/view/theme/modmypi/images/nav-icon-close.png');
		}
	});

	/* currency drop down */
	$('#main-currency .header-currency').hover(
		function () {
			$(this).find('.expand').stop(true, false).slideDown();
			$(this).addClass('open');
		},
		function () {
			$(this).find('.expand').slideUp();
			$(this).removeClass('open');
		}
	);

	$('#mobile-currency .active').click(function (e) {
		e.preventDefault();

		$(this).parent().find('.expand').slideToggle();

		return false;
	});

	/* custom select */
	$(document).on('change', '.select select', function () {
		var text = $(this).find("option:selected").text();
		$(this).siblings('span').html(text);
	});

	$(document).on('focus', '.select select', function () {
		$(this).closest('.select').removeClass('error');
	});

	$('.select select').each(function (i, e) {
		var text = $(e).find("option:selected").text();
		$(e).siblings('span').html(text);
	});

	/* google select */
	var gt = setInterval(function () {
		if ($('.goog-te-combo').length > 0) {
			var text = $(this).find("option:selected").text();
			text = text == "" ? "Select Language" : text;
			//$(this).closest('.select').children('span').html(text);
			$('#google_translate_element').children('span').text(text);
			clearInterval(gt);
		}
	}, 200);

	/* product hover */
	$('#product-container .product').hover(
		function () {
			$(this).find('.hover').stop(true, false).fadeIn();
		},
		function () {
			$(this).find('.hover').fadeOut();
		}
	);

	/* notification close */
	$(document).on('click touchend', '#notification .close, .notification .close', function () {
		$('#notification').fadeOut('slow');
	});

	var cat_anim = false;
	$(document).on('click touchend', '.categories .heading', function () {
		if (!cat_anim) {
			cat_anim = true;
			$(this).siblings('ul').slideToggle(function () {
				cat_anim = false;
			});
			$(this).find('.arrow').toggleClass('open');
		}
	});

	$(window).resize(function () {
		if ($(document).width() < 641) {

		} else {
			$('#content-left .categories').children('ul').slideDown(function () {
				$(this).removeAttr('style');
			});
			$('#content-left .categories .arrow').removeClass('open');
		}
	});

});