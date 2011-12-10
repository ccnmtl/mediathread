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

