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

var AssetList = new (function () {
    var self= this;
    this.collections = [];
    this.switcherTitle = function(title) {
        jQuery('#switcher-title').html(title);
    };
    this.projectLinks = function(project) {
        var p = project.participants;
        var links = [];
        for (var i=0;i<p.length;i++) {
            var u = p[i].username;
            ///don't include self, since that's already in there
            if (p[i].username == project.username)
                continue;
            links.push({type:'assetlist',
                        href:'/yourspace/'+u+'/asset/',
                        ajax:'/annotations/'+u+'/',
                        title:p[i].name
                       });
        }
        return links;
    }
    this.linkifyList = function(link_ary) {
        var html = '';
        for (var i=0;i<link_ary.length;i++) {
            html += '<li><a class="'+link_ary[i].type+'-switch" href="'+link_ary[i].href+'"'
                +'data-ajax="'+link_ary[i].ajax+'">'+link_ary[i].title+'</a></li>'
        }
        return html;
    }
    this.extraLinks = function() {
        ///NOTE: gets overridden in discussion so the project itself is also added.
        var proj = djangosherd.storage.lastProject();
        if (proj) {
            return self.linkifyList(self.projectLinks(proj));
        } else return '';
    }
    this.replaceWithProject = function(project) {
        var dom = jQuery('#materials').html(
            '<div class="essay-space published">'
                +project.body
                +'</div>'
        ).get(0);

        //update DOM state...
        DjangoSherd_decorate_citations(dom);
        self.switcherTitle(project.title);
        jQuery('#choice_my_items').show();
        jQuery('#switcher-collection-filter').hide();
        jQuery(".switcher-top").removeClass("open");
        jQuery(".switcher-top").addClass("closed");
        jQuery("ul.switcher-options").hide();
    }
    this.decorators = {
        project:function(evt) {
            var newurl = this.getAttribute('data-ajax') || this.getAttribute('href');
            if (newurl) {
                djangosherd.storage.get({type:'project', url:newurl, id:'xxx'}, 
                                        self.replaceWithProject);
                evt.preventDefault();
            }
        },
        asset:function(evt) {
            var newurl = this.getAttribute('data-ajax') || this.getAttribute('href');
            if (newurl) {
                self.swapAssetColumn(newurl);
                evt.preventDefault();
            }
        }
    };
    this.onInit = function(){};
    this.swapAssetColumn = function (asset_url, init) {
        var extra = (/\?/.test(asset_url)) ? '&' : '?';
        ///TODO: show hourglass icon so people know to wait for a large query (e.g. class collection)
        jQuery.ajax({
            url:asset_url+extra+'edit_mode=true',
            dataType:'html',
            cache: false, // Chrome && Internet Explorer has aggressive caching policies.
            success:function(html) {
                jQuery('#asset_browse_col').replaceWith(html);
                var new_assets = jQuery('#asset_browse_col').get(0);
                /***
                 All the stateful crap we have to update upon reload of an annotation list
                 ***/
                ///ASSETS UPDATE
                //length of list
                updateVerticalHeight();
                //hide-show for annotation notes/tags
                hs_init(new_assets);
                ///set onclick/drag listener
                if (tinyMCE.activeEditor) {
                    tinyMCE.activeEditor.plugins.citation.decorateCitationAdders(new_assets);
                    jQuery(new_assets.parentNode).addClass('annotation-embedding');
                }
                ///Decorate thumbs
                DjangoSherd_createThumbs(new_assets);

                ///SWITCHER UPDATE
                ///Ajaxify switcher links for swapping out asset_browse_col
                var extras = self.extraLinks();
                if (extras) {
                    jQuery('#switcher-extras').append(extras).show();
                    
                }

                var url_path = asset_url.split('?')[0];
                jQuery('div.collection-filter a',new_assets).click(function(evt){
                    var newquery = this.getAttribute('data-ajax') || this.getAttribute('href');
                    if (newquery) {
                        self.swapAssetColumn(url_path+'?'+newquery.split('?')[1]);
                        evt.preventDefault();
                    }
                });
                jQuery('div.collection-chooser a',new_assets).each(function() {
                    if (jQuery(this).hasClass('project-switch')) {
                        jQuery(this).click(self.decorators.project);
                    } else {
                        jQuery(this).click(self.decorators.asset);
                    }
                });
                if (init) {
                    self.onInit();
                    if (window.SherdSlider) SherdSlider.init();
                }
                if (window.SherdSlider) SherdSlider.signal('onLoad','asset_column',new_assets);
            }
        });
    }
})()

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

    //initialize Assets Column with ajax
    //AssetList.swapAssetColumn(jQuery('#asset_browse_col').attr('data-ajax') || '/annotations/all/' , /*init=*/true);
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

