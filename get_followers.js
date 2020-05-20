// Not the most ethical ways but a workaround for the rate limits on the API

function customScroll() {
	console.count('called')
	window.scrollTo(0, document.body.scrollHeight)
}

setInterval(customScroll, 1000)
