var tinyMCEmode = true;

function toggleEditor(id) {
    logDebug('toggleEditor',id);
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



function connect_respond_clicked (e) {
    //logDebug (e.src().parentNode.id);
    div_id = e.src().parentNode.id 
    logDebug('respond clicked',div_id);
    the_text_area =  $$('#' + div_id  + ' textarea')[0];
    the_div = $$('#' + div_id  + ' ul')[0]
    if (hasElementClass (the_div, 'invisible')) {
        makeVisible(the_div);
        tinyMCE.execCommand('mceAddControl', false, the_text_area);
    }
    else {
        tinyMCE.execCommand('mceRemoveControl', false, the_text_area);
        makeInvisible(the_div);
    }
}

function connect_respond_prompt(a) {
    connect (a, 'onclick', connect_respond_clicked);
}

function discussion_init() {
    forEach ($$('div.respond_to_comment_form_div ul'), makeInvisible);
    
    forEach($$('.respond_prompt'), connect_respond_prompt)
        //connect (
}
addLoadEvent(discussion_init);
