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
                    self.setDirty(true);
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
            jQuery('input#participants_toggle').click(self.showParticipantList);
            jQuery('input#save-button').click(self.showSaveOptions);
            
            self.commonPostInitialize();
        }
        
        this.onPrepareCitation = function(target) {
            var a = jQuery(target).parents("td.panel-container.media");
            if (a && a.length) {
                PanelManager.openSubPanel(a[0]);
            }
        }
        
        this.setDirty = function(is_dirty, animate) {
            if (is_dirty) {
                self.project_modified = true;
                if (animate) {
                    jQuery("#save-button").effect("bounce", {}, 750);
                }
            } else {
                self.project_modified = false;
            }
        }
        
        this.htmlEncode = function(value) {
            return jQuery('<div/>').text(value).html();
        }

        this.htmlDecode = function(value) {
            return jQuery('<div/>').html(value).text();
        }
        
        this.updateParticipantsChosen = function() {
            var opts = jQuery("select[name='participants'] option");
            var participant_list = ""; 
            for (var i = 0; i < opts.length; i++) {
                if (participant_list.length > 0)
                    participant_list += ", ";
                participant_list +=  opts[i].innerHTML;
            }
            jQuery("#participants_chosen").html(participant_list);
        }
        
        this.showParticipantList = function() {
            tinyMCE.activeEditor.plugins.editorwindow._closeWindow()
            
            var element = jQuery("#participant_list")[0];
            jQuery(element).dialog({
                buttons: [{ text: "Ok",
                            click: function() { self._save = true; jQuery(this).dialog("close"); }},
                          { text: "Cancel",
                            click: function() { jQuery(this).dialog("close"); }}
                      ],
                "beforeClose": function(event, ui) { if (self._save) { self.updateParticipantList(); } self._save = false; return true; },
                "draggable": false, 
                "resizable": false, 
                "modal": true, 
                "width": 425, 
                "height": 245});
            
            return false;
        }

        this.updateParticipantList = function(evt) {
            console.log('updateParticipantList');
            var opts = jQuery("select[name='participants'] option");
            var old_list = jQuery('#participants_chosen').text().replace(/^\s*/,'').replace(/\s*$/,'').replace(/,\s+/g, ',').split(',');
            
            var matches = old_list.length == opts.length;
            for (var i = 0; i < opts.length && matches; i++) {
                matches = jQuery.inArray(opts[i].innerHTML, old_list) >= 0;
            }
            
            if (!matches) {
                self.updateParticipantsChosen();
                self.setDirty(true, true);
            }
            
            return false;
        }
        
        this.preview = function(evt) {
            // Unload any citations
            for (var i = 0; i < self.citations.length; i++)
                self.citations[i].unload();
            
            if (jQuery("#composition-essay-space:visible").length) {
                // Edit View
                jQuery("#composition-essay-space").hide();
                tinyMCE.activeEditor.show();
                jQuery("#composition-materials-panhandle-label").html("Add Selection");
                jQuery("#preview-button").attr("value", "Preview");
                jQuery("#composition-asset-view-published").hide();
                
                // Kill the asset view
                self.citations["composition-essay-space"].unload();
                
                jQuery("#id_publish").show();
                jQuery("label[for='id_publish']").html("Status");
                jQuery("#collection-materials").show();
            } else {
                // Preview View
                tinyMCE.activeEditor.hide();
                tinyMCE.activeEditor.plugins.editorwindow._closeWindow()
                
                jQuery("#project-content").hide();
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
        
        this.showSaveOptions = function(evt) {
            var element = jQuery("#save-publish-status")[0];
            
            jQuery(element).dialog({
                buttons: [{ text: "Save",
                            click: function() { self._save = true; jQuery(this).dialog("close"); }},
                          { text: "Cancel",
                            click: function() { jQuery(this).dialog("close"); }}
                      ],
                "beforeClose": function(event, ui) { if (self._save) { self.saveProject(event); } self._save = false; return true; },
                "draggable": false, 
                "resizable": false, 
                "modal": true, 
                "width": 250, 
                "height": 145});
            
            return false;
        }
        
        this.saveProject = function(evt) {
            tinyMCE.triggerSave();
            var frm = document.forms['editproject'];
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
            
            
            // select all participants so they will be picked up when the form is serialized
            jQuery("select[name=participants] option").attr("selected","selected");
            var data = jQuery(frm).serializeArray();
            data = data.concat(jQuery(document.forms['editvisibility']).serializeArray());
            data = data.concat(jQuery(document.forms['editparticipants']).serializeArray());
            
            jQuery("#save-button").attr("disabled", "disabled");
            
            jQuery.ajax({
                type: 'POST',
                url: frm.action,
                data: data,
                dataType: 'json',
                error: function(){
                    jQuery("#save-button").removeAttr("disabled");
                    alert('There was an error saving your project.');
                },
                success: function(json,textStatus,xhr){
                    //jQuery('#last-version-link').attr('href',json.revision.url);

                    if (json.revision.public_url) {
                        jQuery('#last-version-public').attr("href", json.revision.public_url);
                        jQuery('#last-version-public').show();
                    } else {
                        jQuery('#last-version-public').attr("href", "");
                        jQuery('#last-version-public').hide();
                    }
                    
                    jQuery('#project-visibility').html(json.revision.visibility);
                    
                    self.updateParticipantsChosen();
                    jQuery("#participant_list").hide();
                    jQuery("#save-publish-status").hide();
                    
                    if (self.collection_list)
                        self.collection_list.updateProject(); 
                    
                    self.setDirty(false);
                    self.revision = json.revision;
                    
                    jQuery("#save-button").removeAttr("disabled");
                    jQuery("#save-button").attr("value", "Saved");
                    jQuery("#save-button").effect("bounce", { times:3  }, 1000, function() { jQuery("#save-button").attr("value", "Save & Publish")});
                }
            });
            
            return true;
        }
    })();

})();


