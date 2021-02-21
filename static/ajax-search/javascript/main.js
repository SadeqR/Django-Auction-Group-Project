const usrInput = $("#usrInput")
const searchIcon = $('#searchIcon')
const auctionsDiv = $('#filterableAuctions')
const endpoint = '/'
const delay_ms = 600

// Fade out the div then show the filtered html given
let ajax_call = function (endpoint, req_params) {
	$.getJSON(endpoint, req_params)
		.done(response => {
			auctionsDiv.fadeTo('fast', 0).promise().then(() => {
				auctionsDiv.html(response['the_html_v'])
				auctionsDiv.fadeTo('slow', 1)
				searchIcon.removeClass('blink')
			})
		})
}

let sfc = false
usrInput.on('keyup', function () {
	const req_params = {
		q: $(this).val()
	}
	searchIcon.addClass('blink')
	if (sfc) {
		clearTimeout(sfc)
	}
	sfc = setTimeout(ajax_call, delay_ms, endpoint, req_params)
})

