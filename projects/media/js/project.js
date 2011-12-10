var project_modified = false;
function updateParticipantsChosen() {
    var opts = document.forms['editproject'].participants.options;
    var participant_list = ""; 
    for (var i = 0; i < opts.length; i++) {
        if (participant_list.length > 0)
            participant_list += ", ";
        participant_list +=  opts[i].innerHTML;
    }
    jQuery("#participants_chosen").html(participant_list);
}

function updateParticipantList() {
    if (jQuery("#participant_list").is(":visible")) {
        var opts = document.forms['editproject'].participants.options;
        var old_list = jQuery('#participants_chosen').text().replace(/^\s*/,'').replace(/\s*$/,'').replace(/,\s+/g, ',').split(',');
        
        var matches = old_list.length == opts.length;
        for (var i = 0; i < opts.length && matches; i++) {
            matches = jQuery.inArray(opts[i].innerHTML, old_list) >= 0;
        }
        
        if (!matches) {
            updateParticipantsChosen();
            jQuery("#participant_update").show();
            project_modified = true;
        }
    }
    jQuery("#participant_list").toggle();
    updateVerticalHeight();
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
    var pixels_free = jQuery(window).height()-220;
    jQuery('.resize-height').each(function() {
        var offset = pixels_free;
        if (this.id && this.id in resize_offsets) {
            offset -= resize_offsets[this.id];
        }
        this.style.height = offset +'px';
    });
    var project_editor = tinyMCE.get('project-content');
    if (project_editor) {
        var container = project_editor.getContainer();
        if (container != null) {
            pixels_free -= jQuery('#participants_chosen').height()*2 || 0;
            project_editor.theme.resizeTo(
                parseInt(container.style.width,10)||container.offsetWidth||500,
                pixels_free-100
            );
        }
    }
}

function saveProject(evt) {
    tinyMCE.triggerSave();
    var frm = evt.target;
    if (/preview/.test(frm.target)) {
        return;
    }
    //else
    evt.preventDefault();
    
    // select all participants so they will be picked up when the form is serialized
    jQuery("select[name=participants] option").attr("selected","selected");  
    var data = jQuery(frm).serializeArray();
    
    jQuery.ajax({
        type: 'POST',
        url: frm.action,
        data: data,
        dataType: 'json',
        error: function(){alert('There was an error saving your project.');},
        success: function(json,textStatus,xhr){
            jQuery('#last-version-prefix').html('Saved: ')

            jQuery('#last-version-link')
            .html('Revision '+json.revision.id)
            .attr('href',json.revision.url);

            jQuery('#last-version-saved')
            .show()
            .colorBlend([{
                param:'background-color',
                strobe:false,
                colorList:['#fff100','#ffffff'],
                cycles:1
            }]);

            if (json.revision.public_url) {
                jQuery('#last-version-public').html('(<a href="'
                                                    +json.revision.public_url
                                                    +'">public url</a>)');
            } else {
                jQuery('#last-version-public').html('');
            }
            
            updateParticipantsChosen();
            jQuery("#participant_list").hide();
            jQuery("#participant_update").hide();
            project_modified = false;
        }
    });
}

function resizeProjectPage() {
    var visible = getVisibleContentHeight();
    jQuery('#collection').css('height', visible + "px");
  
    jQuery('#collection .media-column-container').css('height', (visible - 77) + "px");
}

function project_init() {
    if (document.forms['editproject']) {
        jQuery(document.forms['editproject']).bind('submit',saveProject);
        project_warnOnUnload();
    }
    jQuery(window).resize(updateVerticalHeight);

    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            updateVerticalHeight();
        }) 
    });

    //PROJECT PARTICIPANT UPDATES
    jQuery('a.participants_toggle').click(updateParticipantList);
}

function project_warnOnUnload() {
    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onChange.add(function(editor) {
            project_modified = true;
        }) 
    });
    
    jQuery(window).bind('beforeunload',function(evt) {
        if (project_modified) {
            return "Changes to your project have not been saved.";
        }
    })
}

