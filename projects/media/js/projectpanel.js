var ProjectPanelHandler = function(panel) {
    djangosherd.storage.json_update(panel.context);
    
    var self = this;
    self.panel = panel;
    self.projectModified = false;
    self.parentContainer = jQuery("#" + panel.context.project.id + "-panel-container").get(0);
    
    self.project_type = panel.context.project.project_type;
    self.essaySpace = jQuery(self.parentContainer).find(".essay-space")[0];
    
    self.citationView = new CitationView();
    self.citationView.init({ 'default_target': panel.context.project.id + "-videoclipbox",
              'onPrepareCitation': self.onPrepareCitation,
              'presentation': "medium" });
    self.citationView.decorateLinks(self.essaySpace.id);
    
    // hook up behaviors
    self._bind(self.parentContainer, "input.project-savebutton", "click", function(evt) { return self.showSaveOptions(evt); });
    self._bind(self.parentContainer, "input.project-previewbutton", "click", function(evt) { return self.preview(evt); } );
    self._bind(self.parentContainer, "input.participants_toggle", "click", function(evt) { return self.showParticipantList(evt); });
    
    //self._bind(self.parentContainer, "input.project-revisionbutton", "click", function() { self.showRevisions });
    //self._bind(self.parentContainer, "input.project-responsesbutton", "click", function() { self.showResponses });
    
    // Wait for tinymce to sort itself out & add a beforeUnload event
    setTimeout(function() { self.postInitialize(); }, 1000);
};

ProjectPanelHandler.prototype.postInitialize = function() {
    var self = this;
    
    var editors = jQuery(self.parentContainer).find("textarea.mceEditor");
    if (editors.length) {
        self.tinyMCE = tinyMCE.get(editors[0].id);
        self.tinyMCE.show();
        self.tinyMCE.onChange.add(function(editor) { self.setDirty(true); } );
        
        // Reset width to 100% via javascript. TinyMCE doesn't resize properly 
        // if this isn't completed AFTER instantiation
        jQuery('#' + self.panel.context.project.id + '-project-content_tbl').css('width', "100%");
        
        jQuery(window).bind('beforeunload', function() { self.beforeUnload });
        
        // There should only be one per view.
        // Could get hairy once discussion is added to the mix.
        self.collection_list = CollectionList.init({
          'parent': self.parentContainer,
          'template': 'collection',
          'template_label': "collection_table",
          'create_annotation_thumbs': true,
        });
        
        jQuery(self.parentContainer).find(".participants_toggle").removeAttr("disabled");
    }
}

ProjectPanelHandler.prototype.onPrepareCitation = function(target) {
    var a = jQuery(target).parents("td.panel-container.media");
    if (a && a.length) {
        PanelManager.openSubPanel(a[0]);
    }
}

ProjectPanelHandler.prototype.showParticipantList = function(evt) {
    var self = this;
    var frm = evt.srcElement.form;
    
    // close any outstanding citation windows
    self.tinyMCE.plugins.editorwindow._closeWindow()
    
    var element = jQuery(self.parentContainer).find(".participant_list")[0];
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
    
    jQuery(element).parent().appendTo(frm);
    return false;
}

ProjectPanelHandler.prototype.updateParticipantList = function(evt) {
    var self = this;
    
    // Compare the participants label with the results from the new list
    var opts = jQuery(self.parentContainer).find("select[name='participants'] option");
    var old_list = jQuery(self.parentContainer).find('.participants_chosen')
        .text()
        .replace(/^\s*/,'')
        .replace(/\s*$/,'')
        .replace(/,\s+/g, ',')
        .split(',');
    
    var matches = old_list.length == opts.length;
    for (var i = 0; i < opts.length && matches; i++) {
        matches = jQuery.inArray(opts[i].innerHTML, old_list) >= 0;
    }
    
    if (!matches) {
        self.updateParticipantsLabel();
        self.setDirty(true, true);
    }
    
    return false;
}

ProjectPanelHandler.prototype.updateParticipantsLabel = function() {
    var self = this;
    
    var opts = jQuery(self.parentContainer).find("select[name='participants'] option");
    var participant_list = ""; 
    for (var i = 0; i < opts.length; i++) {
        if (participant_list.length > 0)
            participant_list += ", ";
        participant_list +=  opts[i].innerHTML;
    }
    jQuery(self.parentContainer).find('.participants_chosen').html(participant_list);
}


ProjectPanelHandler.prototype.preview = function(evt) {
    var self = this;
    
    // Unload any citations
    // Close any tinymce windows
    self.citationView.unload();
    self.tinyMCE.plugins.editorwindow._closeWindow();
    
    // What's the project type we're previewing?
    if (jQuery(self.essaySpace).is(":visible")) {
        // Edit View
        jQuery(self.essaySpace).hide();
        
        jQuery(self.parentContainer).find("td.panhandle-stripe div.label").html("Add Selection");
        jQuery(self.parentContainer).find("input.project-previewbutton").attr("value", "Preview");
        jQuery(self.parentContainer).find("div.asset-view-published").hide();
        jQuery(self.parentContainer).find("h1.project-title").hide();
        
        // Kill the asset view
        self.citationView.unload();
        
        jQuery(self.parentContainer).find("div.collection-materials").show();
        jQuery(self.parentContainer).find("input.project-title").show();
        jQuery(self.parentContainer).find("input.participants_toggle").show();
        
        self.tinyMCE.show();
    } else {
        // Preview View
        self.tinyMCE.hide();
        self.tinyMCE.plugins.editorwindow._closeWindow()
        
        jQuery(self.parentContainer).find("textarea.mceEditor").hide();
        jQuery(self.parentContainer).find("div.collection-materials").hide();
        jQuery(self.parentContainer).find("input.project-title").hide();
        jQuery(self.parentContainer).find("input.participants_toggle").hide();
        
        // Get updated text into the preview space - decorate any new links
        jQuery(self.essaySpace).html(self.tinyMCE.getContent());
        self.citationView.decorateLinks(self.essaySpace.id);

        jQuery(self.essaySpace).show();
        jQuery(self.parentContainer).find("td.panhandle-stripe div.label").html("View Selection");
        jQuery(self.parentContainer).find("input.project-previewbutton").attr("value", "Edit");
        jQuery(self.parentContainer).find("div.asset-view-published").show();
        jQuery(self.parentContainer).find("h1.project-title").show();
    }
    
    jQuery(self.parentContainer).find("td.panel-container").toggleClass("media collection");
    jQuery(self.parentContainer).find("td.panhandle-stripe").toggleClass("media collection");
    jQuery(self.parentContainer).find("div.pantab").toggleClass("media collection");
    return false;
}


ProjectPanelHandler.prototype.showSaveOptions = function(evt) {
    var self = this;
    
    var frm = evt.srcElement.form;
    var element = jQuery(frm).find("div.save-publish-status")[0];
        
    jQuery(element).dialog({
        buttons: [{ text: "Save",
                    click: function() { self._save = true; jQuery(this).dialog("close"); }},
                  { text: "Cancel",
                    click: function() { jQuery(this).dialog("close"); }}
              ],
        "beforeClose": function(event, ui) { 
            if (self._save)
                self.saveProject(frm); 

            self._save = false; 
            return true; 
         },
        "draggable": false, 
        "resizable": false, 
        "modal": true, 
        "width": 250, 
        "height": 145});
    
    jQuery(element).parent().appendTo(frm);
    return false;
}

ProjectPanelHandler.prototype.saveProject = function(frm) {
    var self = this;
    
    tinyMCE.triggerSave();
    
    if (/preview/.test(frm.target)) {
        return true;
    }
    
    var title = jQuery(self.parentContainer).find("input.project-title");
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
    jQuery(self.parentContainer).find("select[name='participants'] option").attr("selected","selected");
    var data = jQuery(frm).serializeArray();
    data = data.concat(jQuery(document.forms['editparticipants']).serializeArray());
    
    var saveButton = jQuery(self.parentContainer).find(".project-savebutton").get(0); 
    jQuery(saveButton).attr("disabled", "disabled");
    
    jQuery.ajax({
        type: 'POST',
        url: frm.action,
        data: data,
        dataType: 'json',
        error: function(){
            jQuery(saveButton).removeAttr("disabled");
            alert('There was an error saving your project.');
        },
        success: function(json,textStatus,xhr){
            //jQuery('#last-version-link').attr('href',json.revision.url);

            var lastVersionPublic = jQuery(self.parentContainer).find(".last-version-public").get(0);
            if (json.revision.public_url) {
                jQuery(lastVersionPublic).attr("href", json.revision.public_url);
                jQuery(lastVersionPublic).show();
            } else {
                jQuery(lastVersionPublic).attr("href", "");
                jQuery(lastVersionPublic).hide();
            }
            
            jQuery(self.parentContainer).find('.project-visibility-description').html(json.revision.visibility);
            
            //self.updateParticipantsLabel();
            //jQuery("#participant_list").hide();
            //jQuery("#save-publish-status").hide();
            
            //if (self.collection_list)
            //    self.collection_list.updateProject(); 
            
            self.setDirty(false);
            self.revision = json.revision;
            
            jQuery(saveButton).removeAttr("disabled")
                .attr("value", "Saved")
                .effect("bounce", { times:3  }, 1000, function() { jQuery(saveButton).attr("value", "Save & Publish")});
        }
    });
    
    return true;
}

ProjectPanelHandler.prototype.setDirty = function(is_dirty, animate) {
    var self = this;
    if (is_dirty) {
        self.project_modified = true;
        if (animate) {
            jQuery(self.parentContainer).find("input.project-savebutton").effect("bounce", {}, 750);
        }
    } else {
        self.project_modified = false;
    }
}

ProjectPanelHandler.prototype.beforeUnload = function() {
    var self = this;
    
    if (self.projectModified) {
        return "Changes to your project have not been saved.";
    } else {
        var title = jQuery(self.parentContainer).find("input[name=title]");
        if (title && title.length > 0) {
            var value = title[0].val();
            if (!value || value.length < 1) {
                return "Please specify a project title.";
            } else if (value == "Untitled") {
                return 'Please update your "Untitled" project title.';
            }
        }
    }
}

ProjectPanelHandler.prototype._bind = function(parent, elementSelector, event, handler) {
    var elements = jQuery(parent).find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).bind(event, handler);
        return true;
    } else {
        return false;
    }
}





