function parseTime(elapsedTime) {
	let minutes = String(Math.floor(elapsedTime / 60 % 60));
	minutes = (minutes.length > 1) ? minutes : '0' + minutes;
	let seconds = String(Math.floor(elapsedTime % 60));
	seconds = (seconds.length > 1) ? seconds : '0' + seconds;
	let hours = String(Math.floor(elapsedTime / 60 / 60));

	let time = (hours != '0') ? hours + ':' : '';
	time += minutes + ":" + seconds;

	return time;
}

function genFileList(files) {
	html = `<tr class="bordered"><td>📁 ..<hr></td></tr>`
	for (file in files) {
		html += `<tr class="bordered"><td>${(files[file]) ? '📁' : ''} ${file}<hr></td></tr>`
	}
	$('table').html(html);

	$('tr').on('click', function (e) {
		e.preventDefault();
		if ($(this).text().trim().startsWith('📁')) {
			if ($(this).text().trim() == '📁 ..') {
				path = path.substring(0, path.slice(0, -1).lastIndexOf('/') + 1)
			} else {
				path += $(this).text().trim().substring(3) + '/'
			}

			sock.send(`files_in:${path}`)
		} else {
			if (confirm(`Are you sure you want to watch ${$(this).text().trim()}?`)) {
				sock.send(`play:${path + $(this).text().trim()}`)
				setTimeout(() => sock.send('tracks'), 1000)
			}
		}
	});
}

let path = '/media/shared/Shows/'
let sock = null;
let data = {};
$(() => {
	let slider = document.getElementById('range');
	sock = new WebSocket("ws://nas.local:8901/");
	sock.onopen = () => {
		sock.send(`files_in:${path}`)
		sock.send(`tracks`)
	}

	sock.onmessage = (msg) => {
		const resp = JSON.parse(msg.data);
		if (JSON.stringify(data) === msg.data) return;
		data = resp;
		const { type } = resp;

		if (type === "vlc") {
			const { title, length, time, playing } = resp;

			// TITLE
			if (title) $('h1#header').html(`Playing: ${title}`);

			// SLIDER
			if (length) slider.max = resp.length;
			if (time) {
				slider.value = resp.time;
				$('span.time').html(parseTime(resp.time));
			}

			// PLAY BUTTON
			if (playing) {
				$('a#playback').html('<button name="playback" class="flex-inline"><i class="fas fa-pause fa-6x"></i></button>')
				$('a#playback').removeClass('paused')
			} else {
				$('a#playback').html('<button name="playback" class="flex-inline"><i class="fas fa-play fa-6x"></i></button>')
				$('a#playback').addClass('paused')
			}
		} else if (type === "fs") {
			const { f_dir, f_resp } = resp;
			genFileList(f_resp);
		} else if (type === "tracks") {
			const subs = new Map(JSON.parse(resp.subs))
			const audio = new Map(JSON.parse(resp.audio))

			let html = `<option value="default">Default Subtitles</option>`
			subs.forEach((v, k) => {
				html += `<option value="${k}">${v}</option>`
			})
			$("select#sub-select").html(html)

			html = `<option value="default">Default Audio</option>`
			audio.forEach((v, k) => {
				html += `<option value="${k}">${v}</option>`
			})
			$("select#audio-select").html(html)
		}
	}

	// PLAY BUTTON
	$('a#playback').on('click', e => {
		e.preventDefault();
		sock.send(data.playing ? 'pause' : 'resume');
	});

	// SLIDER
	let lastUpdate = Date.now();
	slider.oninput = () => {
		$('span.time').html(parseTime(slider.value));
		if (lastUpdate < Date.now() - 100) {
			sock.send(`seek:${slider.value}`)
			lastUpdate = Date.now();
		}
	}

	// SKIP FORWARD
	$('a#forward').on('click', (e) => {
		e.preventDefault()
		sock.send(`seek_by:${$('input[id="forward-amt"]').val()}`)
	})

	// SKIP BACKWARD
	$('a#backward').on('click', (e) => {
		e.preventDefault()
		sock.send(`seek_by:-${$('input[id="backward-amt"]').val()}`)
	})

	// SETTINGS
	let settings = document.getElementById("settings-ico");
	settings.onclick = function () {
		modal.style.display = "block";
	}

	let modal = document.getElementById("settings-modal");
	window.onclick = function (event) {
		if (event.target == modal) {
			modal.style.display = "none";
		}
	}

	// SUBS/AUDIO SELECT
	$('button#submit-modal').on('click', function (e) {
		e.preventDefault()
		modal.style.display = "none"
		sock.send(`set_tracks:${$("select#sub-select option:selected").val()};#;${$("select#audio-select option:selected").val()}`)
	});
})