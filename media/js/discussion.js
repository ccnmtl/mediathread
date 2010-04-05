addLoadEvent(function discussion_init() {
    var next_response_loc = false;
    forEach($$('.respond_prompt'), function(elt) {
        connect(elt,'onclick', function (evt) {
            var respond = evt.src();
            var frm = $('comment-form');
            frm.elements['parent'].value = respond.getAttribute("data-comment");
            if (!next_response_loc) {
		next_response_loc = respond;
                respond.nextSibling.appendChild(frm);
                showElement(frm);
                $('id_comment').focus();
                tinyMCE.execCommand("mceAddControl", false, "id_comment");
            } else {
		if (next_response_loc == respond) {
		    next_response_loc = false;
		} else {
                    next_response_loc = respond;
		}
                tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
                tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
            }
        });
    });

    tinyMCE.onRemoveEditor.add(function(manager, ed) {
        //logDebug("third focus");
	if (next_response_loc) {
            next_response_loc.nextSibling.appendChild(document.forms[0]);
            tinyMCE.execCommand("mceAddControl", false, "id_comment");
	} else {
            hideElement('comment-form');
	}
    });
    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
        });
    });

});

