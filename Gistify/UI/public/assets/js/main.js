function main() {
  // $('.skillset').hide();
  // $('.skillset').fadeIn(1000);
  //
  // $('.projects').hide();

  $('.textgist').on('click', function() {
		// $(this).toggleClass('active')
    // $(this).text('Projects viewed')
    // $(this).next().slideToggle(400)
    $(this).next().toggle();
	});
}

$(document).ready(main);
