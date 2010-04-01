var tinyMCEmode = true;

function toggleEditor(id) {
    //logDebug('toggleEditor',id);
    if (!tinyMCE.get(id)) {
        tinyMCE.execCommand('mceAddControl', false, id);
    } else {
        tinyMCE.execCommand('mceRemoveControl', false, id);
    }
}


function toggleVisible(elem) {
    toggleElementClass("invisible", elem);
}

function makeVisible(elem) {
    removeElementClass(elem, "invisible");
}

function makeInvisible(elem) {
    addElementClass(elem, "invisible");
}



function connect_respond_prompt(a) {
    connect (a, 'onclick', connect_respond_clicked);
}

function discussion_init() {
    var next_response_loc = false;
    forEach ($$('div.respond_to_comment_form_div ul'), makeInvisible);
    
    forEach($$('.respond_prompt'), function(elt) {
        connect(elt,'onclick', function (evt) {
            var respond = evt.src();
            var frm = $('comment-form');
            //console.log(tinyMCE.editors);
            frm.elements['parent'].value = respond.getAttribute("data-comment");
            if (tinyMCE.activeEditor == null) {
                respond.nextSibling.appendChild(frm);
                showElement(frm);
                $('id_comment').focus();
                tinyMCE.execCommand("mceAddControl", false, "id_comment");
            } else {
                next_response_loc = respond.nextSibling;
                tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
                tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
                
                //logDebug("second focus");
            }
        });
    });

    tinyMCE.onRemoveEditor.add(function(manager, ed) {
        //logDebug("third focus");
        next_response_loc.appendChild(document.forms[0]);
        tinyMCE.execCommand("mceAddControl", false, "id_comment");
    });
    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
            //console.log(editor);
        });
    });

}
addLoadEvent(discussion_init);
