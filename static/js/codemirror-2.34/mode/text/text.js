CodeMirror.defineMode("mymode", function(config, parserConfig) {
  return {
    token: function(stream, state) {
      return null;
    }
  };
});

CodeMirror.defineMIME("text/plain", "text");