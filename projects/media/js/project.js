(function () {
    
    window.ProjectView = (function ProjectViewAbstract() {
        var self = this;
        
        this.init = function (options, panels) {
            self.options = options;
            self.project_types = [ 'assignment', 'composition' ];
            self.project_modified = false;
            
            // Create an assetview.
            // @todo - We have potentially more than 1 assetview on this page. The singleton nature in the
            // core architecture means the two views are really sharing the underlying code.
            // Consider how to resolve this contention. (It's a big change in the core.)
            
            // This may be DANGEROUS in any sense. The old assetview should be destroyed first?
            djangosherd.storage = new DjangoSherd_Storage();
            djangosherd.assetview = new Sherd.GenericAssetView({ clipform: false, clipstrip: true});
            
            // Stash the project data in storage
            for (var i = 0; i < panels.length; i++) {
                djangosherd.storage.json_update(panels[i].context);
            }
            
            /** // ???? used by whom?
            if (options.open_from_hash) {
                // project feedback & discussion
                var annotation_to_open = String(document.location.hash).match(/annotation=annotation(\d+)/);
                if (annotation_to_open != null) {
                    openCitation('/annotations/'+annotation_to_open[1] + '/', { autoplay:false});
                }
            }
            **/
            
            // WARN ON UNLOAD
            tinyMCE.onAddEditor.add(function (manager, ed) {
                ed.onChange.add(function (editor) {
                    self.setDirty(true);
                });
            });
            
            jQuery(window).bind('beforeunload', function (evt) {
                if (self.project_modified) {
                    return "Changes to your project have not been saved.";
                } else {
                    var title = jQuery("#id_title:visible");
                    if (title && title.length > 0) {
                        var value = title.val();
                        if (!value || value.length < 1) {
                            return "Please specify a project title.";
                        } else if (value === "Untitled") {
                            return 'Please update your "Untitled" project title.';
                        }
                    }
                }
            });
            
            // Decorate any active editing windows -- are there more than 1?
            if (tinyMCE.activeEditor) {
                var new_assets = jQuery('#asset_table').get(0);
                
                tinyMCE.activeEditor.plugins.citation.decorateCitationAdders(new_assets);
                jQuery(new_assets.parentNode).addClass('annotation-embedding');
            }

            // Decorate any essay windows -- definitely can be more than 1
            self.citations = {};
            
            for (var j = 0; j < self.project_types.length; j++) {
                var project_type = self.project_types[j];
                var projectEssayId = project_type + "-essay-space";
                var projectEssay = document.getElementById(projectEssayId);
                
                if (projectEssay) {
                    var presentation = "small";
                    if (jQuery("#" + project_type + "-asset-view-published").hasClass("medium")) {
                        presentation = "medium";
                    }
                    
                    var cv = new CitationView();
                    cv.init({ 'default_target': project_type + "-videoclipbox",
                              'onPrepareCitation': self.onPrepareCitation,
                              'presentation': presentation });
                    cv.decorateLinks(projectEssayId);
                    self.citations[projectEssayId] = cv;
                }
            }
                
            // Could there be more than 1? This could get heavy if there are...
            self.collection_list = CollectionList.init({
                'template': 'collection',
                'template_label': 'collection_table',
                'create_annotation_thumbs': true
            });
        };

        this.onPrepareCitation = function (target) {
            var a = jQuery(target).parents("td.panel-container.media");
            if (a && a.length) {
                PanelManager.openSubPanel(a[0]);
            }
        };
        
        this.setDirty = function (is_dirty, animate) {
            if (is_dirty) {
                self.project_modified = true;
                if (animate) {
                    jQuery("#save-button").effect("bounce", {}, 750);
                }
            } else {
                self.project_modified = false;
            }
        };
        
        this.htmlEncode = function (value) {
            return jQuery('<div/>').text(value).html();
        };

        this.htmlDecode = function (value) {
            return jQuery('<div/>').html(value).text();
        };
        
        this.updateParticipantsChosen = function () {
            var opts = jQuery("select[name='participants'] option");
            var participant_list = "";
            for (var i = 0; i < opts.length; i++) {
                if (participant_list.length > 0) {
                    participant_list += ", ";
                }
                participant_list +=  opts[i].innerHTML;
            }
            jQuery("#participants_chosen").html(participant_list);
        };
        
        this.showParticipantList = function () {
            tinyMCE.activeEditor.plugins.editorwindow._closeWindow();
            
            var element = jQuery("#participant_list")[0];
            jQuery(element).dialog({
                buttons: [{ text: "Ok",
                            click: function () { self._save = true; jQuery(this).dialog("close"); }},
                          { text: "Cancel",
                            click: function () { jQuery(this).dialog("close"); }}
                      ],
                "beforeClose": function (event, ui) { if (self._save) { self.updateParticipantList(); } self._save = false; return true; },
                "draggable": false, 
                "resizable": false, 
                "modal": true, 
                "width": 425, 
                "height": 245});
            
            return false;
        };

        this.updateParticipantList = function (evt) {
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
        };
        
        this.preview = function (evt) {
            // Unload any citations
            for (var i = 0; i < self.citations.length; i++)
                self.citations[i].unload();
            
            // What's the project type we're previewing?
            var project_type = null;
            for (var i = 0; i < self.project_types.length; i++) {
                if (jQuery(evt.srcElement).hasClass(self.project_types[i]))
                    project_type = self.project_types[i];
            }
            
            if (jQuery("#" + project_type + "-essay-space:visible").length) {
                // Edit View
                jQuery("#" + project_type + "-essay-space").hide();
                tinyMCE.activeEditor.show();
                jQuery("#" + project_type + "-materials-panhandle-label").html("Add Selection");
                jQuery("#" + project_type + "-preview-button").attr("value", "Preview");
                jQuery("#" + project_type + "-asset-view-published").hide();
                
                // Kill the asset view
                self.citations[project_type + "-essay-space"].unload();
                
                jQuery("#" + project_type + "-collection-materials").show();
            } else {
                // Preview View
                tinyMCE.activeEditor.hide();
                tinyMCE.activeEditor.plugins.editorwindow._closeWindow()
                
                jQuery("#" + project_type + "-project-content").hide();
                jQuery("#" + project_type + "-collection-materials").hide();
                
                // Get updated text into the preview space
                // Decorate any new links
                jQuery("#" + project_type + "-essay-space").html(tinyMCE.activeEditor.getContent());
                self.citations[project_type + "-essay-space"].decorateLinks();

                jQuery("#" + project_type + "-essay-space").show();
                jQuery("#" + project_type + "-materials-panhandle-label").html("View Selection");
                jQuery("#" + project_type + "-preview-button").attr("value", "Edit");
                jQuery("#" + project_type + "-asset-view-published").show();
            }
            
            jQuery("#" + project_type + "-materials").toggleClass("media collection");
            jQuery("#" + project_type + "-materials-panhandle").toggleClass("media collection");
            jQuery("#" + project_type + "-materials-pantab").toggleClass("media collection");
            
            return false;
        };
        
        this.showSaveOptions = function (evt) {
            var element = jQuery("#save-publish-status")[0];
            
            jQuery(element).dialog({
                buttons: [{ text: "Save",
                            click: function () { self._save = true; jQuery(this).dialog("close"); }},
                          { text: "Cancel",
                            click: function () { jQuery(this).dialog("close"); }}
                      ],
                "beforeClose": function (event, ui) { if (self._save) { self.saveProject(event); } self._save = false; return true; },
                "draggable": false, 
                "resizable": false, 
                "modal": true, 
                "width": 250, 
                "height": 145});
            
            return false;
        };
        
        this.saveProject = function (evt) {
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
                error: function () {
                    jQuery("#save-button").removeAttr("disabled");
                    alert('There was an error saving your project.');
                },
                success: function (json, textStatus, xhr) {
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
                     
                    if (self.collection_list) {
                        self.collection_list.updateProject();
                    }
                    
                    self.setDirty(false);
                    self.revision = json.revision;
                    
                    jQuery("#save-button").removeAttr("disabled");
                    jQuery("#save-button").attr("value", "Saved");
                    jQuery("#save-button").effect("bounce", { times: 3  }, 1000, function () { jQuery("#save-button").attr("value", "Save & Publish"); });
                }
            });
            
            return true;
        }
    })();
})();


