var ProjectPanelHandler = function (el, parent, panel, space_owner) {
    var self = this;
    
    self.el = el;
    self.panel = panel;
    self.projectModified = false;
    self.parentContainer = parent;
    self.space_owner = space_owner;
    self.tiny_mce_settings = tiny_mce_settings;
    jQuery(self.el).find('.project-savebutton').attr("value", "Saved");

    djangosherd.storage.json_update(panel.context);
    
    if (panel.context.can_edit) {
        var select = jQuery(self.el).find("select[name='participants']")[0];
        jQuery(select).addClass("selectfilter");
        SelectFilter.init("id_participants_" + panel.context.project.id,
            "participants", 0, "/media/admin/");
        
        // HACK: move the save options around due to django form constraints
        var assignment_elt = jQuery(self.el).find("label[for='id_publish_2']").parent();
        if (assignment_elt.length > 0) {
            jQuery(self.el).find('div.due-date').appendTo(assignment_elt);
        }
    }
    
    self.project_type = panel.context.project.project_type;
    self.essaySpace = jQuery(self.el).find(".essay-space")[0];

    // hook up behaviors
    jQuery(window).bind('tinymce_init_instance', function (event, instance, param2) {
        self.onTinyMCEInitialize(instance);
    });
    
    jQuery(window).resize(function () {
        self.resize();
    });
    
    self._bind(self.el, "td.panel-container", "panel_state_change", function () {
        self.onClosePanel(jQuery(this).hasClass("subpanel"));
    });
    
    
    self._bind(self.el, "input.project-savebutton", "click", function (evt) { return self.showSaveOptions(evt); });
    self._bind(self.el, "a.project-visibility-link", "click", function (evt) {
        jQuery(self.el).find("input.project-savebutton").click();
    });
    self._bind(self.el, "input.project-previewbutton", "click", function (evt) { return self.preview(evt); });
    self._bind(self.el, "input.participants_toggle", "click", function (evt) { return self.showParticipantList(evt); });
    
    self._bind(self.el, "input.project-revisionbutton", "click", function (evt) { self.showRevisions(evt); });
    self._bind(self.el, "input.project-responsesbutton", "click", function (evt) { self.showResponses(evt); });
    self._bind(self.el, "input.project-my-responses", "click", function (evt) { self.showMyResponses(evt); });
    self._bind(self.el, "input.project-my-response", "click", function (evt) { self.showMyResponse(evt); });
    
    self._bind(self.el, "input.project-create-assignment-response", "click", function (evt) { self.createAssignmentResponse(evt); });
    self._bind(self.el, "input.project-create-instructor-feedback", "click", function (evt) { self.createInstructorFeedback(evt); });
    
    self._bind(self.el, "input.project-title", 'keypress', function (evt) {
        self.setDirty(true);
    });
    
    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': panel.context.project.id + "-videoclipbox",
        'onPrepareCitation': self.onPrepareCitation,
        'presentation': "medium",
        'clipform': true,
        'winHeight': function () {
            var elt = jQuery(self.el).find("div.asset-view-published")[0];
            return jQuery(elt).height() -
                (jQuery(elt).find("div.annotation-title").height() + jQuery(elt).find("div.asset-title").height() + 15);
        }
    });
    self.citationView.decorateLinks(self.essaySpace.id);
    
    if (panel.context.can_edit) {
        tinyMCE.settings = self.tiny_mce_settings;
        tinyMCE.execCommand("mceAddControl", false, panel.context.project.id + "-project-content");
    }
    self.render();
};

ProjectPanelHandler.prototype.onTinyMCEInitialize = function (instance) {
    var self = this;
    
    if (instance && instance.id === self.panel.context.project.id + "-project-content" && !self.tinyMCE) {
    
        self.tinyMCE = instance;
        
        self.tinyMCE.onChange.add(function(args) {
            self.setDirty(true); 
        });
        
        // Reset width to 100% via javascript. TinyMCE doesn't resize properly
        // if this isn't completed AFTER instantiation
        jQuery('#' + self.panel.context.project.id + '-project-content_tbl').css('width', "100%");
        
        jQuery(window).bind('beforeunload', function () {
            return self.beforeUnload();
        });
        
        self.collectionList = new CollectionList({
            'parent': self.el,
            'template': 'collection',
            'template_label': "collection_table",
            'create_annotation_thumbs': true,
            'space_owner': self.space_owner,
            'owners': self.panel.owners,
            'citable': true,
            'view_callback': function () {
                var newAssets = self.collectionList.getAssets();
                self.tinyMCE.plugins.citation.decorateCitationAdders(newAssets);
                jQuery(window).trigger("resize");
            }
        });
        
        if (self.panel.context.editing) {
            self.tinyMCE.show();
            var title = jQuery(self.el).find("input.project-title");
            title.focus();
        }
        
        jQuery(self.el).find(".participants_toggle").removeAttr("disabled");
        
        self.render();
    }
};

ProjectPanelHandler.prototype.resize = function () {
    var self = this;
    var visible = getVisibleContentHeight();
    
    visible -= jQuery(self.el).find(".project-visibility-row").height();
    visible -= jQuery(self.el).find(".project-toolbar-row").height();
    visible -= jQuery(self.el).find(".project-participant-row").height();
    visible -= jQuery("#footer").height(); // padding
    
    visible += 30;
    
    if (self.tinyMCE) {
        var editorHeight = visible;
        // tinyMCE project editing window. Make sure we only resize ourself.
        jQuery(self.el).find("table.mceLayout").css('height', (editorHeight) + "px");
        jQuery(self.el).find("iframe").css('height', (editorHeight) + "px");
    }
    
    jQuery(self.el).find("div.essay-space").css('height', (visible + 20) + "px");
    jQuery(self.el).find('div.asset-view-published').css('height', (visible + 30) + "px");
    jQuery(self.el).find('div.ajaxloader').css('height', visible + 'px');
    
    // Resize the collections box, subtracting its header elements    
    visible -= jQuery(self.el).find("div.filter-widget").outerHeight() + 10;
    jQuery(self.el).find('div.collection-assets').css('height', visible + "px");
    
    // For IE
    jQuery(self.el).find('tr.project-content-row').css('height', (visible) + "px");
    jQuery(self.el).find('tr.project-content-row').children('td.panhandle-stripe').css('height', (visible - 10) + "px");
};

ProjectPanelHandler.prototype.render = function () {
    var self = this;
    
    // Make sure initial state is correct
    // Give precedence to media view IF the subpanel is open and we're in preview mode
    var preview = self.isPreview();
    var open = self.isSubpanelOpen();
    if (preview && open) {
        jQuery(self.el).find(".panel-content").removeClass("fluid").addClass("fixed");
        jQuery(self.el).find("td.panel-container.collection").removeClass("fixed").addClass("fluid");
    } else {
        jQuery(self.el).find(".panel-content").removeClass("fixed").addClass("fluid");
        jQuery(self.el).find("td.panel-container.collection").removeClass("fluid").addClass("fixed");
    }
    
    jQuery(window).trigger("resize");
};

ProjectPanelHandler.prototype.onClosePanel = function (isSubpanel) {
    var self = this;
    
    // close any outstanding citation windows
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    self.render();
};

ProjectPanelHandler.prototype.onPrepareCitation = function (target) {
    jQuery(target).parent().css("background", "none");
    
    var a = jQuery(target).parents("td.panel-container.collection");
    if (a && a.length) {
        PanelManager.openSubPanel(a[0]);
    }
};

ProjectPanelHandler.prototype.createAssignmentResponse = function (evt) {
    var self = this;
    
    PanelManager.closeSubPanel(self);
    
    var context = {
        'url': MediaThread.urls['project-create'](),
        'params': { parent: self.panel.context.project.id }
    };
    
    // Short-term
    // Navigate to a new project if the user is looking
    // at another response.
    if (jQuery(self.parentContainer).find("td.panel-container.composition").length > 0) {
        context.callback = function (json) {
            window.location = json.context.project.url;
        };
    }
    
    PanelManager.newPanel(context);
    
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    jQuery(srcElement).remove();
};

ProjectPanelHandler.prototype.createInstructorFeedback = function (evt) {
    var self = this;
    
    PanelManager.closeSubPanel(self);
    
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
        buttons: [{ text: "Update",
                    click: function () { jQuery(this).dialog("close"); }}
                 ],
        beforeClose: function (event, ui) {
            self._save = false;
            if (!self._validAuthors()) {
                return false;
            } else {
                self.updateParticipantList();
                return true;
            }
        },
        draggable: true,
        resizable: false,
        modal: true,
        width: 600,
        position: "top",
        zIndex: 10000
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
        buttons: [{ text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }},
                  { text: "View",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }}
              ],
        beforeClose: function (event, ui) {
            if (self._save) {
                self._save = false;
                var opts = jQuery(self.el).find("select[name='revisions'] option:selected");
                if (opts.length < 1) {
                    showMessage("Please select a revision");
                    return false;
                } else {
                    var val = jQuery(opts[0]).val();
                    window.open(val, 'mediathread_project' + self.panel.context.project.id);
                }
            }
            return true;
        },
        modal: true,
        width: 425,
        height: 245,
        position: "top",
        zIndex: 10000
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
        buttons: [{ text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }},
                  { text: "View Response",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }}
                 ],
        beforeClose: function (event, ui) {
            if (self._save) {
                self._save = false;
                var opts = jQuery(self.el).find("select[name='responses'] option:selected");
                if (opts.length < 1) {
                    showMessage("Please select a response");
                    return false;
                } else {
                    var val = jQuery(opts[0]).val();
                    window.location = val;
                }
            }
            
            return true;
        },
        modal: true,
        width: 425,
        height: 200,
        position: "top",
        zIndex: 10000
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

// Multiple responses.
ProjectPanelHandler.prototype.showMyResponses = function (evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    
    // close any outstanding citation windows
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    var element = jQuery(self.el).find(".my-response-list")[0];
    jQuery(element).dialog({
        buttons: [{ text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }},
                  { text: "View",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }}
                 ],
        beforeClose: function (event, ui) {
            if (self._save) {
                self._save = false;
                var opts = jQuery(self.el).find("select[name='my-responses'] option:selected");
                if (opts.length < 1) {
                    showMessage("Please select a response");
                    return false;
                } else {
                    var val = jQuery(opts[0]).val();
                    window.location = val;
                }
            }
            
            return true;
        },
        modal: true,
        width: 425,
        height: 200,
        position: "top",
        zIndex: 10000
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

// A single response
ProjectPanelHandler.prototype.showMyResponse = function (evt) {
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    window.location = jQuery(srcElement).data("url");
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
        self.setDirty(true);
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

ProjectPanelHandler.prototype.isPreview = function () {
    var self = this;
    return jQuery(self.essaySpace).css("display") === "block";
};

ProjectPanelHandler.prototype.isSubpanelOpen = function () {
    var self = this;
    return jQuery(self.el).find("td.panel-container.collection").hasClass("open");
};

ProjectPanelHandler.prototype.preview = function (evt) {
    var self = this;
    
    // Unload any citations
    // Close any tinymce windows
    self.citationView.unload();
    
    if (self.tinyMCE) {
        self.tinyMCE.plugins.editorwindow._closeWindow();
    }
    
    if (self.isPreview()) {
        // Switch to Edit View
        jQuery(self.essaySpace).hide();
        
        jQuery(self.el).find("td.panhandle-stripe div.label").html("Insert Selections");
        jQuery(self.el).find("input.project-previewbutton").attr("value", "Preview");
        jQuery(self.el).find("div.asset-view-published").hide();
        jQuery(self.el).find("h1.project-title").hide();
        
        // Kill the asset view
        self.citationView.unload();
        
        jQuery(self.el).find("div.collection-materials").show();
        jQuery(self.el).find("input.project-title").show();
        jQuery(self.el).find("input.participants_toggle").show();
        jQuery(self.el).find("span.project-current-version").show();
        
        // Highlight toolbar
        jQuery(self.el).find('table.panel-subcontainer tr td.panel-subcontainer-toolbar-column').addClass("editing");
        
        // Make the edit space take up the most room
        jQuery(self.el).find(".panel-content.fixed").removeClass("fixed").addClass("fluid");
        jQuery(self.el).find("td.panel-container.collection").removeClass("fluid").addClass("fixed");
        
        self.tinyMCE.show();
    } else {
        // TinyMCE bug
        // The first time the editor is shown
        // the project can be marked as dirty incorrectly
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
        
        // De-Highlight toolbar
        jQuery(self.el).find('table.panel-subcontainer tr td.panel-subcontainer-toolbar-column').removeClass("editing");

        // Give precedence to media view IF the subpanel is open
        if (jQuery(self.el).find("td.panel-container.collection").hasClass("open")) {
            jQuery(self.el).find(".panel-content").removeClass("fluid").addClass("fixed");
            jQuery(self.el).find("td.panel-container.collection").removeClass("fixed").addClass("fluid");
        }
        
        // Get updated text into the preview space - decorate any new links
        jQuery(self.essaySpace).html(tinyMCE.activeEditor.getContent());
        self.citationView.decorateLinks(self.essaySpace.id);

        jQuery(self.essaySpace).show();
        jQuery(self.el).find("td.panhandle-stripe div.label").html("View Inserted Selections");
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
    
    // Validate title. Not empty or "Untitled". At least one author
    if (!self._validTitle() || !self._validAuthors()) {
        return false;
    }
    
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    var element = jQuery(frm).find("div.save-publish-status")[0];
        
    jQuery(element).dialog({
        buttons: [{ text: "Cancel",
                    click: function () { jQuery(this).dialog("close"); }},
                  { text: "Save",
                    click: function () { self._save = true; jQuery(this).dialog("close"); }}
              ],
        create: function () {
            jQuery('#id_due_date').datepicker({
                minDate: 0,
                dateFormat: 'mm/dd/yy',
                beforeShow: function (input, inst) {
                    inst.dpDiv.css({
                        top: (input.offsetHeight) + 'px'
                    });
                }
            });
        },
        open: function( event, ui ) {
            if (!jQuery('#id_publish_2').is(":checked")) {
                jQuery("#id_due_date").attr("disabled", "disabled");
            }            
            jQuery("input[name=publish]").bind('click', function () {
                if (jQuery('#id_publish_2').is(":checked")) {
                    jQuery("#id_due_date").removeAttr("disabled");
                } else {
                    jQuery("#id_due_date").attr("disabled", "disabled");
                }           
            });
        },
        beforeClose: function (event, ui) {
            if (self._save) {
                self.saveProject(frm);
            }

            self._save = false;
            return true;
        },
        draggable: false,
        resizable: false,
        modal: true,
        width: 430,
        position: "top",
        zIndex: 10000
    });
    
    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.saveProject = function (frm, skipValidation) {
    var self = this;
    
    tinyMCE.activeEditor.save();
    
    if (skipValidation === undefined) {
        if (!self._validTitle() || !self._validAuthors()) {
            return false;
        }
    }

    jQuery(self.el).find("select[name='participants'] option")
        .attr("selected", "selected");
    var data = jQuery(frm).serializeArray();
    data = data.concat(jQuery(document.forms.editparticipants)
        .serializeArray());

    var saveButton = jQuery(self.el).find(".project-savebutton").get(0);
    jQuery(saveButton).attr("disabled", "disabled")
        .attr("value", "Saving...")
        .addClass("saving");
    
    jQuery.ajax({
        type: 'POST',
        url: frm.action,
        data: data,
        dataType: 'json',
        error: function () {
            jQuery(saveButton).removeAttr("disabled").attr("value", "Save").removeClass("saving");
            showMessage('There was an error saving your project.');
        },
        success: function (json, textStatus, xhr) {
            if (json.status === 'error') {
                showMessage(json.msg);
            } else {
                var lastVersionPublic = jQuery(self.el).find(".last-version-public").get(0);
                if (json.revision.public_url) {
                    jQuery(lastVersionPublic).attr("href", json.revision.public_url);
                    jQuery(lastVersionPublic).show();
                } else {
                    jQuery(lastVersionPublic).attr("href", "");
                    jQuery(lastVersionPublic).hide();
                }
                
                if (json.is_assignment) {
                    jQuery(self.el).removeClass("composition").addClass("assignment");
                    jQuery(self.el).find(".composition").removeClass("composition").addClass("assignment");
                    jQuery(self.el).next(".pantab-container").find(".composition").removeClass("composition").addClass("assignment");
                    jQuery(self.el).prev().removeClass("composition").addClass("assignment");
                    jQuery(self.el).prev().find("div.label").html("assignment");
                    jQuery(self.el).prev().prev().find(".composition").removeClass("composition").addClass("assignment");
                    
                    jQuery(self.el).find('a.project-export').hide();
                    jQuery(self.el).find('a.project-print').hide();
                } else {
                    jQuery(self.el).removeClass("assignment").addClass("composition");
                    jQuery(self.el).find(".assignment").removeClass("assignment").addClass("composition");
                    jQuery(self.el).next(".pantab-container").find(".assignment").removeClass("assignment").addClass("composition");
                    jQuery(self.el).prev().removeClass("assignment").addClass("composition");
                    jQuery(self.el).prev().find("div.label").html("composition");
                    jQuery(self.el).prev().prev().find(".assignment").removeClass("assignment").addClass("composition");
                    
                    jQuery(self.el).find('a.project-export').show();
                    jQuery(self.el).find('a.project-print').show();                    
                }
                
                jQuery(self.el).find('.project-visibility-description').html(json.revision.visibility);
                
                if (json.revision.due_date) {
                    jQuery(self.el).find('.project-due-date').html("Due " + json.revision.due_date);
                } else {
                    jQuery(self.el).find('.project-due-date').html("");
                }
                
                self.revision = json.revision;
                if ("title" in json) {
                    document.title = "Mediathread " + json.title;
                }
                self.setDirty(false);
                self.updateRevisions();
            }    
            jQuery(saveButton).removeAttr("disabled")
                .removeClass("saving", 1200, function () {
                    jQuery(this).attr("value", "Saved"); });
        }
    });
    
    return true;
};

ProjectPanelHandler.prototype.setDirty = function (isDirty) {
    var self = this;
    
    if (self.projectModified !== isDirty) {
        self.projectModified = isDirty;
        
        if (!isDirty && self.tinyMCE) {
            self.tinyMCE.isNotDirty = 1; // clear the tinymce dirty flags
        }
        
        if (isDirty) {
            jQuery(self.el).find('.project-savebutton').attr("value", "Save");
            // Set a single timer to kick off a save event.
            // If the timer is already active, don't set another one
            // Clear the timer variable at the end
            if (self.dirtyTimer === undefined) {                
                self.dirtyTimer = window.setTimeout(function() {
                    var frm = jQuery(self.el).find('form[name=editproject]')[0];
                    self.saveProject(frm, true);
                    self.dirtyTimer = undefined;
                }, 10000);
            }
        } else {
            jQuery(self.el).find('.project-savebutton').attr("value", "Saved");
            if (self.dirtyTimer !== undefined) {
                window.clearTimeout(self.dirtyTimer);
                self.dirtyTimer = undefined;
            }
        }
    }
};

ProjectPanelHandler.prototype.isDirty = function() {
    var self = this;
    return self.projectModified ||
        self.tinyMCE.isDirty() ||
        (self.tinyMCE.editorId === tinyMCE.activeEditor.editorId &&
                tinyMCE.activeEditor.isDirty())
};

ProjectPanelHandler.prototype.updateRevisions = function() {
    var self =  this;
    
    jQuery.ajax({
        type: 'GET',
        url: MediaThread.urls['project-revisions'](
                self.panel.context.project.id),
        dataType: 'json',
        error: function () {},
        success: function (json, textStatus, xhr) {
            Mustache.update("revisions", {'context': json});
        }
    });            
    
};

ProjectPanelHandler.prototype.beforeUnload = function () {
    var self = this;
    var msg = null;
    
    // Check tinyMCE dirty state. For some reason, the instance we're holding is not always current
    if (self.isDirty()) {
        msg = "Changes to your project have not been saved.";
    } else {
        var title = jQuery(self.el).find("input[name=title]");
        if (title && title.length > 0) {
            var value = jQuery(title[0]).val();
            if (!value || value.length < 1) {
                msg = "Please specify a project title.";
            } else if (value === "Untitled") {
                msg = 'Please update your "Untitled" project title.';
            }
        }
    }
    
    if (msg) {
        PanelManager.openPanel(self.el);
        return msg;
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

ProjectPanelHandler.prototype._validAuthors = function () {
    var self = this;
    // Make sure there's at least one author
    var options = jQuery(self.el).find("select[name='participants'] option");
    if (options.length < 1) {
        showMessage("This project has no authors. Please select at least one author.");
        return false;
    } else {
        return true;
    }
};

ProjectPanelHandler.prototype._validTitle = function () {
    var self = this;
    
    var title = jQuery(self.el).find("input.project-title");
    var value = title.val();
    if (!value || value.length < 1) {
        showMessage("Please specify a project title.");
        title.focus();
        return false;
    } else if (value === "Untitled") {
        showMessage('Please update your "Untitled" project title.');
        title.focus();
        return false;
    } else {
        return true;
    }
};
