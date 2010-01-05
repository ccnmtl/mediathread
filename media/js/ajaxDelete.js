/* requires MochiKit.Visual */

    function ajaxDelete(link, container) {
      var doReplaceForm = function (req) {
        if( req.status == 200 ) {
          fade(container);
        };
      };
    
      var doReplaceErrorForm = function (req) {
        alert("Error!");
      };

      if( confirm("Are you sure?") ) {
        var res = doXHR(link.href, {method:"POST"});
        res.addCallbacks(doReplaceForm,doReplaceErrorForm);
      };
      return false;
    }
