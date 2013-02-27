$(function(){

	var cmEditor = CodeMirror(document.getElementById('content'), {
		theme: "monokai"
		, lineNumbers: true
		, gutter: true
		, autoFocus: true
	});

	$('#language').change(function(){
		setMode(this.value);
	})


	//Toggle CodeMirror editor between different language modes
	var setMode = function(mode) {

		//For some reason JSON is just javascript with an argument...
		if ( mode === 'json'){
			mode = { name: "javascript", json: true};
		}

		//Backwards compatiblity support for older plaintext pastes
		if ( mode === ''){
			mode = 'text';
		}

		CodeMirror.modeURL = "/static/js/codemirror-2.34/mode/%N/%N.js";
		cmEditor.setOption("mode", mode);
		CodeMirror.autoLoadMode(cmEditor, mode);
	}

	//Retrieve the past as indicated in the URL hash
	var getPaste  = function(){
		var hash = window.location.hash.replace(/^#/, '');
		$.ajax({
			url: '/v1/get/' + hash
		}).done(function(res){
			var parsedRes;

			//Parse JSON response if need be
			try{
				parsedRes = JSON.parse(res);
			}catch(err){
				parsedRes = res;
			}

			parsedRes.language = parsedRes.language || 'text';

			//change the dropdown box to parsedData.language
			$('#language').val(parsedRes.language);

			//set the language mode to parsedData.language
			setMode(parsedRes.language);

			//set the editor value to parsedData.paste_data
			cmEditor.setValue(parsedRes.paste_data);

			setShortUrl(hash);

		}).fail(function(res){
			console.log(res);
			alert('Ack something went wrong!')
		});
	}

	//Set the contents of the URL display field
	var setShortUrl = function(hash){
		$('#short_url').val('http://'+window.location.host + '/#' + hash );
		window.location.hash = "#" + hash;
	}

	var savePaste = function(){
		var language = $('#language').val();
		var paste_data = cmEditor.getValue();
		var payload = {
			"paste_data": paste_data
			,"language": language
		}

		$.ajax({
			url:'/v1/save'
			, type: 'POST'
			, data: {"data":JSON.stringify(payload)}
		}).done(function(res){
			setShortUrl(res)
		});
	}

	$('#save-button').click(function(){
		savePaste();
	});

	if (window.location.hash){
		getPaste();
	}

	//Override ctrl+s in the browser and save a new paste
	document.addEventListener("keydown", function(e) {
		if (e.keyCode == 83 && (navigator.platform.match("Mac") ? e.metaKey : e.ctrlKey)) {
			e.preventDefault();
			savePaste()
		}
	}, false);

	window.onhashchange = getPaste;

});