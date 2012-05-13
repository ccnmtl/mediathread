var ProjectPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    
    self.el = el;
    self.panel = panel;
    self.projectModified = false;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    
    djangosherd.storage.json_update(panel.context);
    
    if (panel.context.can_edit) {
        var select = jQuery(self.el).find("select[name='participants']")[0];
        jQuery(select).addClass("selectfilter");
        SelectFilter.init("id_participants_" + panel.context.project.id, "participants", 0, "/media/");
    }
    
    self.project_type = panel.context.project.project_type;
    self.essaySpace = jQuery(self.el).find(".essay-space")[0];
    
    // hook up behaviors
    jQuery(window).bind('tinymce_init_instance', function (event, instance, param2) {
        self.postInitialize(instance);
    });
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    self._bind(self.el, "input.project-savebutton", "click", function (evt) { return self.showSaveOptions(evt); });
    self._bind(self.el, "input.project-previewbutton", "click", function (evt) { return self.preview(evt); });
    self._bind(self.el, "input.participants_toggle", "click", function (evt) { return self.showParticipantList(evt); });
    
    self._bind(self.el, "input.project-revisionbutton", "click", function (evt) { self.showRevisions(evt); });
    self._bind(self.el, "input.project-responsesbutton", "click", function (evt) { self.showResponses(evt); });
    
    self._bind(self.el, "input.project-create-assignment-response", "click", function (evt) { self.createAssignmentResponse(evt); });
    self._bind(self.el, "input.project-create-instructor-feedback", "click", function (evt) { self.createInstructorFeedback(evt); });
    
    self._bind(self.el, "input.project-title", 'change', function (evt) { self.projectModified = true; });
    
    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': panel.context.project.id + "-videoclipbox",
        'onPrepareCitation': self.onPrepareCitation,
        'presentation': "medium"
    });
    self.citationView.decorateLinks(self.essaySpace.id);
    
    if (panel.context.can_edit) {
        tinyMCE.execCommand("mceAddControl", false, panel.context.project.id + "-project-content");
    }

    self.resize();
};

ProjectPanelHandler.prototype.postInitialize = function (instance) {
    var self = this;
    
    if (instance && instance.id === self.panel.context.project.id + "-project-content" && !self.tinyMCE) {
    
        self.tinyMCE = instance;
        self.tinyMCE.onChange.add(function (editor) {
            self.setDirty(true);
        });
        
        // Reset width to 100% via javascript. TinyMCE doesn't resize properly
        // if this isn't completed AFTER instantiation
        jQuery('#' + self.panel.context.project.id + '-project-content_tbl').css('width', "100%");
        
        jQuery(window).bind('beforeunload', function () {
            return self.beforeUnload();
        });
        
        self.collection_list = new CollectionList({
            'parent': self.el,
            'template': 'collection',
            'template_label': "collection_table",
            'create_annotation_thumbs': true,
            'space_owner': self.space_owner
        });
        
        self.resize();
        
        if (self.panel.context.editing) {
            self.tinyMCE.show();
            self.tinyMCE.focus();
        }
        
        jQuery(self.el).find(".participants_toggle").removeAttr("disabled");
    }
};

ProjectPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    jQuery(self.el).find('tr td.panel-container div.panel').css('height', (visible) + "px");
    
    visible -= jQuery(self.el).find(".project-toolbar-row").height();
    visible -= jQuery(self.el).find(".project-participant-row").height();
    visible -= 35; // padding
    
    if (self.tinyMCE) {
        var editorHeight = visible - 15;
        // tinyMCE project editing window. Make sure we only resize ourself.
        jQuery(self.el).find("table.mceLayout").css('height', (editorHeight) + "px");
        jQuery(self.el).find("iframe").css('height', (editorHeight) + "px");
    }
    
    jQuery(self.el).find("div.essay-space").css('height', (visible) + "px");
    jQuery(self.el).find('tr.project-content-row').css('height', (visible) + "px");
    jQuery(self.el).find('tr.project-content-row').children('td.panhandle-stripe').css('height', (visible) + "px");
    jQuery(self.el).find('div.scroll').css('height', (visible - 50) + "px");
};

ProjectPanelHandler.prototype.onPrepareCitation = function (target) {
    var a = jQuery(target).parents("td.panel-container.collection");
    if (a && a.length) {
        PanelManager.openSubPanel(a[0]);
    }
};

ProjectPanelHandler.prototype.createAssignmentResponse = function (evt) {
    var self = this;
    
    PanelManager.newPanel({
        'url': MediaThread.urls['project-create'](),
        'params': { parent: self.panel.context.project.id }
    });
    
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    jQuery(srcElement).remove();
};

ProjectPanelHandler.prototype.createInstructorFeedback = function (evt) {
    var self = this;

    PanelManager.newPanel({
        'url': MediaThread.urls['discussion-create'](),
        'params': {
            'publish': 'PrivateStudentAndFaculty',
            'inherit': 'true',
            'app_label': 'projects',
            'model': 'project',
            'obj_pk': self.panel.context.project.id,
            'comment_html': jQuery(self.el).find("h1.project-title").html().trim() + ": Instructor Feedback"
        }
    });
    
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    jQuery(srcElement).remove();
};

ProjectPanelHandler.prototype.showParticipantList = function (evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    
    // close any outstanding citation windows
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    var element = jQuery(self.el).find(".participant_list")[0];
    jQuery(element).dialog({
        buttons: [{ text: "Ok",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }},
                  { text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }}
              ],
        beforeClose: function (event, ui) { if (self._save) { self.updateParticipantList(); } self._save = false; return true; },
        draggable: true,
        resizable: false,
        modal: true,
        width: 425,
        height: 245,
        position: "top"
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.showRevisions = function (evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    
    // close any outstanding citation windows
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    var element = jQuery(self.el).find(".revision-list")[0];
    jQuery(element).dialog({
        buttons: [{ text: "View",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }},
                  { text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }}
              ],
        beforeClose: function (event, ui) {
            if (self._save) {
                var opts = jQuery(self.el).find("select[name='revisions'] option:selected");
                var val = jQuery(opts[0]).val();
                window.open(val, 'mediathread_project' + self.panel.context.project.id);
            }
            self._save = false;
            return true;
        },
        modal: true,
        width: 425,
        height: 245,
        position: "top"
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.showResponses = function (evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    
    // close any outstanding citation windows
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    var element = jQuery(self.el).find(".response-list")[0];
    jQuery(element).dialog({
        buttons: [{ text: "View",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }},
                  { text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }}
              ],
        beforeClose: function (event, ui) {
            if (self._save) {
                var opts = jQuery(self.el).find("select[name='responses'] option:selected");
                var val = jQuery(opts[0]).val();
                window.location = val;
            }
            self._save = false;
            return true;
        },
        modal: true,
        width: 425,
        height: 200,
        position: "top"
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.updateParticipantList = function (evt) {
    var self = this;
    
    // Compare the participants label with the results from the new list
    var opts = jQuery(self.el).find("select[name='participants'] option");
    var old_list = jQuery(self.el).find('.participants_chosen')
        .text()
        .replace(/^\s*/, '')
        .replace(/\s*$/, '')
        .replace(/,\s+/g, ',')
        .split(',');
    
    var matches = old_list.length === opts.length;
    for (var i = 0; i < opts.length && matches; i++) {
        matches = jQuery.inArray(opts[i].innerHTML, old_list) >= 0;
    }
    
    if (!matches) {
        self.updateParticipantsLabel();
        self.setDirty(true, true);
    }
    
    return false;
};

ProjectPanelHandler.prototype.updateParticipantsLabel = function () {
    var self = this;
    
    var opts = jQuery(self.el).find("select[name='participants'] option");
    var participant_list = "";
    for (var i = 0; i < opts.length; i++) {
        if (participant_list.length > 0) {
            participant_list += ", ";
        }
        participant_list +=  opts[i].innerHTML;
    }
    jQuery(self.el).find('.participants_chosen').html(participant_list);
};


ProjectPanelHandler.prototype.preview = function (evt) {
    var self = this;
    
    // Unload any citations
    // Close any tinymce windows
    self.citationView.unload();
    
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    if (jQuery(self.essaySpace).is(":visible")) {
        // Switch to Edit View
        jQuery(self.essaySpace).hide();
        
        jQuery(self.el).find("td.panhandle-stripe div.label").html("Add Selection");
        jQuery(self.el).find("input.project-previewbutton").attr("value", "Preview");
        jQuery(self.el).find("div.asset-view-published").hide();
        jQuery(self.el).find("h1.project-title").hide();
        
        // Kill the asset view
        self.citationView.unload();
        
        jQuery(self.el).find("div.collection-materials").show();
        jQuery(self.el).find("input.project-title").show();
        jQuery(self.el).find("input.participants_toggle").show();
        jQuery(self.el).find("span.project-current-version").show();
        
        self.tinyMCE.show();
    } else {
        var isDirty = self.projectModified;
        
        // Switch to Preview View
        self.tinyMCE.hide();
        self.tinyMCE.plugins.editorwindow._closeWindow();
        
        jQuery(self.el).find("h1.project-title").html(jQuery(self.el).find("input.project-title").val());
        
        jQuery(self.el).find("textarea.mceEditor").hide();
        jQuery(self.el).find("div.collection-materials").hide();
        jQuery(self.el).find("input.project-title").hide();
        jQuery(self.el).find("input.participants_toggle").hide();
        jQuery(self.el).find("span.project-current-version").hide();
        
        // Get updated text into the preview space - decorate any new links
        jQuery(self.essaySpace).html(self.tinyMCE.getContent());
        self.citationView.decorateLinks(self.essaySpace.id);

        jQuery(self.essaySpace).show();
        jQuery(self.el).find("td.panhandle-stripe div.label").html("View Selection");
        jQuery(self.el).find("input.project-previewbutton").attr("value", "Edit");
        jQuery(self.el).find("div.asset-view-published").show();
        jQuery(self.el).find("h1.project-title").show();
        
        // TinyMCE bug
        // The first time the editor is shown
        // the project can be marked as dirty incorrectly
        self.projectModified = isDirty;
    }
    
    jQuery(window).trigger("resize");
    
    return false;
};


ProjectPanelHandler.prototype.showSaveOptions = function (evt) {
    var self = this;
    
    if (!self._validTitle()) {
        return false;
    }
    
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    var element = jQuery(frm).find("div.save-publish-status")[0];
        
    jQuery(element).dialog({
        buttons: [{ text: "Save",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }},
                  { text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }}
              ],
        beforeClose: function (event, ui) {
            if (self._save) {
                self.saveProject(frm);
            }

            self._save = false;
            return true;
        },
        draggable: true,
        resizable: false,
        modal: true,
        width: 250,
        height: 145,
        position: "top"
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.saveProject = function (frm) {
    var self = this;
    
    self.tinyMCE.save();
    
    if (/preview/.test(frm.target)) {
        return true;
    }
    
    if (!self._validTitle()) {
        return false;
    }
    
    // select all participants so they will be picked up when the form is serialized
    jQuery(self.el).find("select[name='participants'] option").attr("selected", "selected");
    var data = jQuery(frm).serializeArray();
    data = data.concat(jQuery(document.forms.editparticipants).serializeArray());
    
    var saveButton = jQuery(self.el).find(".project-savebutton").get(0);
    jQuery(saveButton).attr("disabled", "disabled");
    
    jQuery.ajax({
        type: 'POST',
        url: frm.action,
        data: data,
        dataType: 'json',
        error: function () {
            jQuery(saveButton).removeAttr("disabled");
            alert('There was an error saving your project.');
        },
        success: function (json, textStatus, xhr) {
            jQuery(self.el).find(".project-current-version").html("Version " + json.revision.id);
            
            var lastVersionPublic = jQuery(self.el).find(".last-version-public").get(0);
            if (json.revision.public_url) {
                jQuery(lastVersionPublic).attr("href", json.revision.public_url);
                jQuery(lastVersionPublic).show();
            } else {
                jQuery(lastVersionPublic).attr("href", "");
                jQuery(lastVersionPublic).hide();
            }
            
            jQuery(self.el).find('.project-visibility-description').html(json.revision.visibility);
            
            self.setDirty(false);
            self.revision = json.revision;
            
            jQuery(saveButton).removeAttr("disabled")
                .attr("value", "Saved")
                .effect("bounce", { times: 3  }, 1000, function () { jQuery(saveButton).attr("value", "Save"); });
        }
    });
    
    return true;
};

ProjectPanelHandler.prototype.setDirty = function (is_dirty, animate) {
    var self = this;
    if (is_dirty) {
        self.projectModified = true;
        if (animate) {
            jQuery(self.el).find("input.project-savebutton").attr("value", "Save Needed")
            .effect("highlight", { times: 3 }, 750);
        }
    } else {
        self.projectModified = false;
    }
};

ProjectPanelHandler.prototype.beforeUnload = function () {
    var self = this;
    
    if (self.projectModified) {
        return "Changes to your project have not been saved.";
    } else {
        var title = jQuery(self.el).find("input[name=title]");
        if (title && title.length > 0) {
            var value = jQuery(title[0]).val();
            if (!value || value.length < 1) {
                return "Please specify a project title.";
            } else if (value === "Untitled") {
                return 'Please update your "Untitled" project title.';
            }
        }
    }
};

ProjectPanelHandler.prototype._bind = function (parent, elementSelector, event, handler) {
    var elements = jQuery(parent).find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).bind(event, handler);
        return true;
    } else {
        return false;
    }
};

ProjectPanelHandler.prototype._validTitle = function () {
    var self = this;
    
    var title = jQuery(self.el).find("input.project-title");
    var value = title.val();
    if (!value || value.length < 1) {
        alert("Please specify a project title.");
        title.focus();
        return false;
    } else if (value === "Untitled") {
        alert('Please update your "Untitled" project title.');
        title.focus();
        return false;
    } else {
        return true;
    }
};





