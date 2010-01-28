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

function updateVerticalHeight() {
    ///350 is sadly a magical number with assumptions about header/footer
    ///ideally we'd measure those things at startup.
    ///probably worth doing once we have a different style or two
    var pixels_free = getViewportDimensions().h-350;

    $('materials').style.height = pixels_free +'px';
    if (tinyMCE.activeEditor) {
        tinyMCE.activeEditor.theme.resizeTo(0,pixels_free-40);
    }
}

addLoadEvent(function(){
    //PROJECT PARTICIPANT UPDATES
    
    
    connect('participants_close','onclick',updateParticipantList);
    //connect(document.forms['editproject'].participants,'onchange', updateParticipantList);

    //RESIZING (vertical)
    connect(window,'onresize',updateVerticalHeight);
    updateVerticalHeight();

});
