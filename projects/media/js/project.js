(function() {
    window.ProjectView = new (function ProjectViewAbstract() {
        var self = this;
        var project_modified = false;
        var options = null;
        
        this.commonInitialize = function(options) {
            self.options = options;
            
            // Create an assetview.
            // @todo - We have two assetviews on this page. The singleton nature in the 
            // core architecture means the two views are really sharing the underlying code.
            // Consider how to resolve this contention. (It's a big change in the core.)
            
            // This may be DANGEROUS in any sense. The old assetview should be destroyed first?
            djangosherd.storage = new DjangoSherd_Storage();
            djangosherd.assetview = new Sherd.GenericAssetView({ clipform:false, clipstrip: true});
            
            if (options.project_json) {
                // Locally cache all assets & annotations associated with the project
                djangosherd.storage.get({type:'project',id:'xxx',url:options.project_json});
            }
        }
        
        this.commonPostInitialize = function() {
            self.citations = {};
            
            for (var i = 0; i < self.options.targets.length; i++) {
                var cv = new CitationView();
                cv.init({ 'default_target': self.options.targets[i].default_target,
                          'onPrepareCitation': self.onPrepareCitation,
                          'presentation': self.options.presentation });
                cv.decorateLinks(self.options.targets[i].parent);
                self.citations[self.options.targets[i].parent] = cv;
            }
            
            if (self.options.view_callback)
                self.options.view_callback();
        }
        
        this.initReadOnly = function(options) {
            self.commonInitialize(options);
            self.commonPostInitialize();
        }
        
        this.initEditing = function(options) {
            self.commonInitialize(options);
            
            // WARN ON UNLOAD
            tinyMCE.onAddEditor.add(function(manager, ed) {
                ed.onChange.add(function(editor) {
                    self.project_modified = true;
                }) 
            });

            // ???? used by whom?
            if (options.open_from_hash) {
                // project feedback & discussion
                var annotation_to_open = String(document.location.hash).match(/annotation=annotation(\d+)/);
                if (annotation_to_open != null) {
                    openCitation('/annotations/'+annotation_to_open[1] + '/', { autoplay:false});
                }
            }
            
            self.collection_list = CollectionList.init({
              'space_owner': options.space_owner,
              'template': 'collection',
              'template_label': 'collection_table',
              'create_annotation_thumbs': true,
              'view_callback': self.postInitializeEditing,
              'project_id': options.project_id,
              'enable_project_selection': options.enable_project_selection
            });
        }
        
        this.postInitializeEditing = function() {
            if (tinyMCE.activeEditor) {
                var new_assets = jQuery('#asset_table').get(0);
                
                tinyMCE.activeEditor.plugins.citation.decorateCitationAdders(new_assets);
                jQuery(new_assets.parentNode).addClass('annotation-embedding');
            }
            
            jQuery(document.forms['editproject']).bind('submit', self.saveProject);
            
            jQuery(window).bind('beforeunload',function(evt) {
                if (self.project_modified) {
                    return "Changes to your project have not been saved.";
                } else {
                    var title = jQuery("#id_title:visible");
                    if (title && title.length > 0) {
                        var value = title.val();
                        if (!value || value.length < 1) {
                            return "Please specify a project title.";
                        } else if (value == "Untitled") {
                            return 'Please update your "Untitled" project title.';
                        }
                    }
                }
                
            });

            //PROJECT PARTICIPANT UPDATES
            jQuery('input.participants_toggle').click(self.updateParticipantList);

            self.commonPostInitialize();
        }
        
        this.onPrepareCitation = function(target) {
            var a = jQuery(target).parents("td.panel-container.media");
            if (a && a.length) {
                PanelManager.openSubPanel(a[0]);
            }
        }

        this.updateParticipantsChosen = function() {
            var opts = document.forms['editproject'].participants.options;
            var participant_list = ""; 
            for (var i = 0; i < opts.length; i++) {
                if (participant_list.length > 0)
                    participant_list += ", ";
                participant_list +=  opts[i].innerHTML;
            }
            jQuery("#participants_chosen").html(participant_list);
        }

        this.updateParticipantList = function() {
            if (jQuery("#participant_list").is(":visible")) {
                var opts = document.forms['editproject'].participants.options;
                var old_list = jQuery('#participants_chosen').text().replace(/^\s*/,'').replace(/\s*$/,'').replace(/,\s+/g, ',').split(',');
                
                var matches = old_list.length == opts.length;
                for (var i = 0; i < opts.length && matches; i++) {
                    matches = jQuery.inArray(opts[i].innerHTML, old_list) >= 0;
                }
                
                if (!matches) {
                    self.updateParticipantsChosen();
                    jQuery("#participant_update").show();
                    self.project_modified = true;
                }
            }
            jQuery("#participant_list").toggle();
            jQuery(window).trigger('resize');
            return false;
        }
        
        this.preview = function(evt) {
            if (jQuery("#composition-essay-space:visible").length) {
                // Edit View
                jQuery("#composition-essay-space").hide();
                tinyMCE.activeEditor.show();
                jQuery("#composition-materials-panhandle-label").html("Add Selection");
                jQuery("#preview-button").attr("value", "Preview");
                jQuery("#composition-asset-view-published").hide();
                
                // Kill the asset view
                self.citations["composition-essay-space"].unload();
                
                jQuery("#save-button").show();
                jQuery("#id_publish").show();
                jQuery("label[for='id_publish']").html("Status");
                jQuery("#collection-materials").show();
            } else {
                // Preview View
                tinyMCE.activeEditor.hide();
                jQuery("#project-content").hide();
                jQuery("#save-button").hide();
                jQuery("#id_publish").hide();
                var selected = jQuery("#id_publish option:selected").text();
                jQuery("label[for='id_publish']").html(selected);
                jQuery("#collection-materials").hide();
                
                // Get updated text into the preview space
                // Decorate any new links
                jQuery("#composition-essay-space").html(tinyMCE.activeEditor.getContent());
                self.citations["composition-essay-space"].decorateLinks();

                jQuery("#composition-essay-space").show();
                jQuery("#composition-materials-panhandle-label").html("View Selection");
                jQuery("#preview-button").attr("value", "Edit");
                jQuery("#composition-asset-view-published").show();
            }
            
            jQuery("#composition-materials").toggleClass("media collection");
            jQuery("#composition-materials-panhandle").toggleClass("media collection");
            jQuery("#composition-materials-pantab").toggleClass("media collection");
            
            return false;
        }

        this.saveProject = function(evt) {
            tinyMCE.triggerSave();
            var frm = evt.target;
            if (/preview/.test(frm.target)) {
                return true;
            }
            
            var title = jQuery("#id_title:visible");
            var value = title.val();
            if (!value || value.length < 1) {
                alert("Please specify a project title.");
                title.focus();
                return false;
            } else if (value == "Untitled") {
                alert('Please update your "Untitled" project title.');
                title.focus();
                return false;
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
                    
                    self.updateParticipantsChosen();
                    jQuery("#participant_list").hide();
                    jQuery("#participant_update").hide();
                    self.project_modified = false;
                    
                    if (self.collection_list)
                        self.collection_list.updateProject(); 
                    
                    jQuery(window).trigger('resize');
                }
            });
        }
    })();

})();


