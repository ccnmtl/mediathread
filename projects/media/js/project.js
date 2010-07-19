function updateParticipantList() {
    var new_list = [];
    var participant_options = document.forms['editproject'].participants.options;
    for (var i=0;i<participant_options.length;i++) {
	if (participant_options[i].selected) {
	    new_list.push(participant_options[i].innerHTML);
	}
    }

    jQuery('#participants_chosen').text(new_list.join(', '));
    jQuery("#participant_update").show('pulsate'); 
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

function swapAssetColumn(asset_url) {
    var extra = (/\?/.test(asset_url)) ? '&' : '?';
    ///TODO: show hourglass icon so people know to wait for a large query (e.g. class collection)
    jQuery.ajax({
        url:asset_url+extra+'edit_mode=true',
        dataType:'html',
        success:function(html) {
            jQuery('#asset_browse_col').replaceWith(html);
            var new_assets = jQuery('#asset_browse_col').get(0);

            ///Ajaxify switcher links for swapping out asset_browse_col
            var url_path = asset_url.split('?')[0];
            jQuery('div.collection-filter a',new_assets).click(function(evt){
                var newquery = this.getAttribute('data-ajax') || this.getAttribute('href');
                if (newquery) {
                    swapAssetColumn(url_path+newquery);
                    evt.preventDefault();
                }
            });
            jQuery('div.collection-chooser a',new_assets).click(function(evt){
                var newurl = this.getAttribute('data-ajax') || this.getAttribute('href');
                if (newurl) {
                    swapAssetColumn(newurl);
                    evt.preventDefault();
                }
            });

            updateVerticalHeight();

            ///set onclick/drag listener
            if (tinyMCE.activeEditor) {
                tinyMCE.activeEditor.plugins.citation.decorateCitationAdders(new_assets);
            }

            ///Decorate thumbs
            DjangoSherd_createThumbs(new_assets);

        }
    });
}

jQuery(function (){/*onDOM Ready*/
    jQuery(window).resize(updateVerticalHeight);

    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            updateVerticalHeight();
        }) 
    });
    //PROJECT PARTICIPANT UPDATES
    jQuery('#participants_close').click(updateParticipantList);

    //initialize Assets Column with ajax
    swapAssetColumn(jQuery('#asset_browse_col').attr('data-ajax') || '/annotations/all/' );
});
