function updateParticipantList() {
    var new_list = [];
    var participant_options = document.forms['editproject'].participants.options;
    for (var i=0;i<participant_options.length;i++) {
	if (participant_options[i].selected) {
	    new_list.push(participant_options[i].innerHTML);
	}
    }
    $('participants_chosen').innerHTML = new_list.join(', ');
    showElement("participant_update");
}

var resize_offsets = {};
function updateVerticalHeight(evt,offsets) {
    ///350 is sadly a magical number with assumptions about header/footer
    ///ideally we'd measure those things at startup.
    ///probably worth doing once we have a different style or two
    if (typeof offsets == 'object') {
        for (a in offsets) {
            resize_offsets[a] = offsets[a];
        }
    }
    var pixels_free = getViewportDimensions().h-220;
    forEach($$('.resize-height'),function(elt) {
        var offset = pixels_free;
        if (elt.id && elt.id in resize_offsets) {
            offset -= resize_offsets[elt.id];
        }
        elt.style.height = offset +'px';
    });
    if (tinyMCE.get('project-content')) {
     tinyMCE.activeEditor.theme.resizeTo(0,pixels_free-40);
    }
}

addLoadEvent(function(){
    //RESIZING (vertical)
    connect(window,'onresize',updateVerticalHeight);

    updateVerticalHeight();

    //PROJECT PARTICIPANT UPDATES
    if ($('participants_close')) {
        connect('participants_close','onclick',updateParticipantList);
    }
    //connect(document.forms['editproject'].participants,'onchange', updateParticipantList);

});
