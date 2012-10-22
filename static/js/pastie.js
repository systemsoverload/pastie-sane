$(function(){
	var cmEditor = CodeMirror(document.getElementById('content'), {
		theme: "monokai"
		, lineNumbers: true
		, gutter: true
	});

	$('#language').change(function(){
		setMode(this.value);
	})


	//Toggle CodeMirror editor between different language modes
	var setMode = function(mode) {

		//For some reason JSON is just javascript with an argument...
		if ( mode === 'json'){
			mode = { name: "javascript", json: true};
		// This is simply for legacy pastes already saved with an explicit 'text' mode
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
			,success: function(res){
				var parsedRes = res;

				//Parse JSON response
				if ( typeof parsedRes !== 'object'){
					parsedRes = JSON.parse(res);
				}

				//change the dropdown box to parsedData.language
				$('#language').val(parsedRes.language);

				//set the language mode to parsedData.language
				setMode(parsedRes.language);

				//set the editor value to parsedData.paste_data
				cmEditor.setValue(parsedRes.paste_data);

				setShortUrl(hash);
			}
		})
	}

	//Set the contents of the URL display field
	var setShortUrl = function(hash){
		$('#short_url').val('http://'+window.location.host + '/#' + hash );
		window.location.hash = "#" + hash;
	}

	$('#save-button').click(function(){
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
			, success: function(res){
				setShortUrl(res)
			}
		})
	});

	if (window.location.hash){
		getPaste();
	}

	window.onhashchange = getPaste;

});