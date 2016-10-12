/* global djangosherd: true, CitationView: true, CollectionList: true */
/* global getVisibleContentHeight: true, MediaThread: true, Mustache: true */
/* global SelectFilter: true, showMessage: true, STATIC_URL: true */
/* global tinymce: true, tinymceSettings: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

var ProjectPanelHandler = function(el, $parent, panel, space_owner) {
    var self = this;

    this.$el = jQuery(el);
    this.panel = panel;
    this.$parentContainer = $parent;
    this.space_owner = space_owner;
    self.$el.find('.project-savebutton').text('Saved');

    djangosherd.storage.json_update(panel.context);
    MediaThread.loadTemplate('project_revisions')
        .then(function() {
            self.initAfterTemplateLoad(el, $parent, panel, space_owner);
        });
};

ProjectPanelHandler.prototype.initAfterTemplateLoad = function(
    el, $parent, panel, space_owner
) {
    var self = this;

    if (panel.context.can_edit) {
        self.$el.find('select[name="participants"]').select2({
            width: '50%',
            placeholder: 'Select one or more authors'
        });

        self.$el.on('change', 'select[name="participants"]', function(evt) {
            self.setDirty(true);
            self._validAuthors();
            return self.updateParticipantsLabel();
        });

        // HACK: move the save options around due to django form constraints
        var assignment_elt = self.$el.find('label[for="id_publish_2"]')
                                            .parent();
        if (assignment_elt.length > 0) {
            self.$el.find('div.due-date').appendTo(assignment_elt);
        }
    }

    self.project_type = panel.context.project.project_type;
    self.essaySpace = self.$el.find('.essay-space')[0];

    // hook up behaviors

    jQuery(window).resize(function() {
        self.resize();
    });

    self._bind(self.$el, 'td.panel-container', 'panel_state_change',
        function() {
            self.onClosePanel(jQuery(this).hasClass('subpanel'));
        });

    self._bind(self.$el, 'form[name="editproject"]', 'keypress keydown keyup',
        function(e) {
            if (e.keyCode === 13) {
                e.preventDefault();
            }
        });

    self._bind(self.$el, '.project-savebutton', 'click', function(evt) {
        return self.showSaveOptions(evt);
    });
    self._bind(self.$el, 'a.project-visibility-link', 'click', function(evt) {
        self.$el.find('.project-savebutton').click();
    });
    self._bind(self.$el, '.project-previewbutton', 'click', function(evt) {
        return self.preview(evt);
    });

    self._bind(self.$el, '.project-revisionbutton', 'click',
        function(evt) {
            self.showRevisions(evt);
        });
    self._bind(self.$el, '.project-responsesbutton', 'click',
        function(evt) {
            self.showResponses(evt);
        });
    self._bind(self.$el, '.project-my-responses', 'click', function(evt) {
        self.showMyResponses(evt);
    });
    self._bind(self.$el, '.project-my-response', 'click', function(evt) {
        self.showMyResponse(evt);
    });

    self._bind(self.$el, '.project-create-assignment-response', 'click',
        function(evt) {
            self.createAssignmentResponse(evt);
        });
    self._bind(self.$el, '.project-create-instructor-feedback', 'click',
        function(evt) {
            self.createInstructorFeedback(evt);
        });

    self._bind(self.$el, 'input.project-title', 'keypress', function(evt) {
        self.setDirty(true);
    });

    // Setup the media display window.
    self.citationView = new CitationView();
    self.citationView.init({
        'default_target': panel.context.project.id + '-videoclipbox',
        'onPrepareCitation': self.onPrepareCitation,
        'presentation': 'medium',
        'clipform': true,
        'winHeight': function() {
            var elt = self.$el.find('div.asset-view-published')[0];
            return jQuery(elt).height() -
                (jQuery(elt).find('div.annotation-title').height() +
                 jQuery(elt).find('div.asset-title').height() + 15);
        }
    });
    self.citationView.decorateLinks(self.essaySpace.id);

    if (panel.context.can_edit) {
        var settings = jQuery.extend(tinymceSettings, {
            init_instance_callback: function(editor) {
                self.onTinyMCEInitialize(editor);
            },
            setup: function(ed) {
                ed.on('change', function(e) {
                    self.setDirty(true);
                });
            },
            selector: '#' + panel.context.project.id + '-project-content'
        });
        tinymce.init(settings);
    }

    self.render();
    self.updateRevisions();
};

ProjectPanelHandler.prototype.onTinyMCEInitialize = function(instance) {
    var self = this;

    if (instance &&
        instance.id === self.panel.context.project.id + '-project-content' &&
        !self.tinymce
       ) {
        self.tinymce = instance;

        // Reset width to 100% via javascript. TinyMCE doesn't resize properly
        // if this isn't completed AFTER instantiation
        var q = '#' + self.panel.context.project.id + '-project-content_tbl';
        jQuery(q).css('width', '100%');

        jQuery(window).on('beforeunload', function() {
            return self.beforeUnload();
        });

        self.collectionList = new CollectionList({
            '$parent': self.$el,
            'template': 'collection',
            'template_label': 'collection_table',
            'create_annotation_thumbs': true,
            'space_owner': self.space_owner,
            'owners': self.panel.owners,
            'citable': true,
            'view_callback': function() {
                var assets = self.collectionList.getAssets();
                self.tinymce.plugins.citation.decorateCitationAdders(assets);
                jQuery(window).trigger('resize');

                // Fired by CollectionList & AnnotationList
                jQuery(window).on('assets.refresh', {'self': self},
                    function(event, html) {
                        self.tinymce.plugins.citation.decorateCitationAdders(
                            self.collectionList.getAssets());
                    });
            }
        });

        if (self.panel.context.editing) {
            self.tinymce.show();
            var title = self.$el.find('input.project-title');
            title.focus();

            self.$el.find('.participants_chosen').parent().hide();
            self.$el.find('.participant_list').show();
        }

        self.render();
    }
};

ProjectPanelHandler.prototype.resize = function() {
    var self = this;
    var visible = getVisibleContentHeight();

    visible -= self.$el.find('.project-visibility-row').height();
    visible -= self.$el.find('.project-toolbar-row').height();
    visible -= self.$el.find('.project-participant-row').height();
    visible -= jQuery('#footer').height(); // padding

    visible += 30;

    if (self.tinymce) {
        var editorHeight = visible;
        // tinymce project editing window. Make sure we only resize ourself.
        self.$el.find('table.mceLayout')
            .css('height', editorHeight + 'px');
        self.$el.find('.mce-edit-area iframe')
            .css('height', editorHeight + 'px');
    }

    self.$el.find('div.essay-space')
        .css('height', (visible + 20) + 'px');
    self.$el.find('div.asset-view-published')
        .css('height', (visible + 30) + 'px');
    self.$el.find('div.ajaxloader').css('height', visible + 'px');

    // Resize the collections box, subtracting its header elements
    visible -= self.$el.find('div.filter-widget').outerHeight() + 10;
    self.$el.find('div.collection-assets')
        .css('height', visible + 'px');

    // For IE
    self.$el.find('tr.project-content-row')
        .css('height', (visible) + 'px');
    self.$el.find('tr.project-content-row')
        .children('td.panhandle-stripe').css('height', (visible - 10) + 'px');
};

ProjectPanelHandler.prototype.render = function() {
    var self = this;

    // Make sure initial state is correct
    // Give precedence to media view IF the subpanel is open
    // and we're in preview mode
    var preview = self.isPreview();
    var open = self.isSubpanelOpen();
    if (preview && open) {
        self.$el.find('.panel-content')
                       .removeClass('fluid')
                       .addClass('fixed');
        self.$el.find('td.panel-container.collection')
                       .removeClass('fixed')
                       .addClass('fluid');
    } else {
        self.$el.find('.panel-content')
                       .removeClass('fixed')
                       .addClass('fluid');
        self.$el.find('td.panel-container.collection')
                       .removeClass('fluid')
                       .addClass('fixed');
    }

    jQuery(window).trigger('resize');
};

ProjectPanelHandler.prototype.onClosePanel = function(isSubpanel) {
    var self = this;

    // close any outstanding citation windows
    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    self.render();
};

ProjectPanelHandler.prototype.onPrepareCitation = function(target) {
    jQuery(target).parent().css('background', 'none');

    var a = jQuery(target).parents('td.panel-container.collection');
    if (a && a.length) {
        window.panelManager.openSubPanel(a[0]);
    }
};

ProjectPanelHandler.prototype.createAssignmentResponse = function(evt) {
    var self = this;

    window.panelManager.closeSubPanel(self);

    var context = {
        'url': MediaThread.urls['project-create'](),
        'params': {parent: self.panel.context.project.id}
    };

    // Short-term
    // Navigate to a new project if the user is looking
    // at another response.
    var q = 'td.panel-container.composition';
    if (self.$parentContainer.find(q).length > 0) {
        context.callback = function(json) {
            window.location = json.context.project.url;
        };
    }

    window.panelManager.newPanel(context);

    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    jQuery(srcElement).remove();
};

ProjectPanelHandler.prototype.createInstructorFeedback = function(evt) {
    var self = this;

    window.panelManager.closeSubPanel(self);

    window.panelManager.newPanel({
        'url': MediaThread.urls['discussion-create'](),
        'params': {
            'publish': 'PrivateStudentAndFaculty',
            'inherit': 'true',
            'app_label': 'projects',
            'model': 'project',
            'obj_pk': self.panel.context.project.id,
            'comment_html': self.$el.find('h1.project-title')
                                           .html()
                                           .trim() + ': Instructor Feedback'
        }
    });

    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    jQuery(srcElement).remove();
};

ProjectPanelHandler.prototype.showRevisions = function(evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;

    // close any outstanding citation windows
    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    var element = self.$el.find('.revision-list')[0];
    jQuery(element).dialog({
        buttons: [{text: 'Cancel',
                   click: function() {
                       jQuery(this).dialog('close');
                   }},
                  {text: 'View',
                   click: function() {
                       self._save = true; jQuery(this).dialog('close');
                   }}
              ],
        beforeClose: function(event, ui) {
            if (self._save) {
                self._save = false;
                var q = 'select[name="revisions"] option:selected';
                var opts = self.$el.find(q);
                if (opts.length < 1) {
                    showMessage('Please select a revision', null, 'Error');
                    return false;
                } else {
                    var val = jQuery(opts[0]).val();
                    window.open(val, 'mediathread_project' +
                                     self.panel.context.project.id);
                }
            }
            return true;
        },
        modal: true,
        width: 425,
        height: 245,
        position: {
            my: 'center top',
            at: 'center top',
            of: window,
            collision: 'none'
        },
        zIndex: 10000
    });

    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.showResponses = function(evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;

    // close any outstanding citation windows
    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    var element = self.$el.find('.response-list')[0];
    jQuery(element).dialog({
        buttons: [{text: 'Cancel',
                   click: function() {
                       jQuery(this).dialog('close');
                   }},
                  {text: 'View Response',
                   click: function() {
                       self._save = true; jQuery(this).dialog('close');
                   }}
                 ],
        beforeClose: function(event, ui) {
            if (self._save) {
                self._save = false;
                var opts = self.$el.find(
                    'select[name="responses"] option:selected');
                if (opts.length < 1) {
                    showMessage('Please select a response', null, 'Error');
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
        position: {
            my: 'center top',
            at: 'center top',
            of: window,
            collision: 'none'
        },
        zIndex: 10000
    });

    jQuery(element).parent().appendTo(frm);
    return false;
};

// Multiple responses.
ProjectPanelHandler.prototype.showMyResponses = function(evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;

    // close any outstanding citation windows
    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    var element = self.$el.find('.my-response-list')[0];
    jQuery(element).dialog({
        buttons: [{text: 'Cancel',
                   click: function() {
                       jQuery(this).dialog('close');
                   }},
                  {text: 'View',
                   click: function() {
                       self._save = true; jQuery(this).dialog('close');
                   }}
                 ],
        beforeClose: function(event, ui) {
            if (self._save) {
                self._save = false;
                var opts = self.$el.find(
                    'select[name="my-responses"] option:selected');
                if (opts.length < 1) {
                    showMessage('Please select a response', null, 'Error');
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
        position: {
            my: 'center top',
            at: 'center top',
            of: window,
            collision: 'none'
        },
        zIndex: 10000
    });

    jQuery(element).parent().appendTo(frm);
    return false;
};

// A single response
ProjectPanelHandler.prototype.showMyResponse = function(evt) {
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    window.location = jQuery(srcElement).data('url');
};

ProjectPanelHandler.prototype.updateParticipantsLabel = function() {
    var self = this;

    var opts = self.$el.find('select[name="participants"] option:selected');
    var participant_list = '';
    for (var i = 0; i < opts.length; i++) {
        if (participant_list.length > 0) {
            participant_list += ', ';
        }
        participant_list +=  opts[i].innerHTML;
    }
    self.$el.find('.participants_chosen').html(participant_list);
};

ProjectPanelHandler.prototype.isPreview = function() {
    var self = this;
    return jQuery(self.essaySpace).css('display') === 'block';
};

ProjectPanelHandler.prototype.isSubpanelOpen = function() {
    var self = this;
    return self.$el.find('td.panel-container.collection')
        .hasClass('open');
};

ProjectPanelHandler.prototype.preview = function(evt) {
    var self = this;

    // Unload any citations
    // Close any tinymce windows
    self.citationView.unload();

    if (self.tinymce) {
        self.tinymce.plugins.editorwindow._closeWindow();
    }

    if (self.isPreview()) {
        // Switch to Edit View
        jQuery(self.essaySpace).hide();

        self.$el.find('td.panhandle-stripe div.label')
            .html('Insert Selections');
        self.$el.find('.project-previewbutton')
            .text('Preview');
        self.$el.find('div.asset-view-published').hide();
        self.$el.find('h1.project-title').hide();

        // Kill the asset view
        self.citationView.unload();

        self.$el.find('div.collection-materials').show();
        self.$el.find('input.project-title').show();
        self.$el.find('span.project-current-version').show();

        var $elt = self.$el.find('.participant_list').first();
        if ($elt) {
            self.$el.find('.participants_chosen').parent().hide();
            $elt.show();
        }

        // Highlight toolbar
        self.$el.find(
            'table.panel-subcontainer tr td.panel-subcontainer-toolbar-column')
            .addClass('editing');

        // Make the edit space take up the most room
        self.$el.find('.panel-content.fixed')
            .removeClass('fixed').addClass('fluid');
        self.$el.find('td.panel-container.collection')
            .removeClass('fluid').addClass('fixed');

        if (self.tinymce) {
            self.tinymce.show();
        }
    } else {
        // Switch to Preview View
        if (self.tinymce) {
            self.tinymce.hide();
            self.tinymce.plugins.editorwindow._closeWindow();
        }

        var val = self.$el.find('input.project-title').val();
        self.$el.find('h1.project-title').html(val);

        self.$el.find('textarea.mceEditor').hide();
        self.$el.find('div.collection-materials').hide();
        self.$el.find('input.project-title').hide();
        self.$el.find('span.project-current-version').hide();

        self.$el.find('.participant_list').hide();
        self.$el.find('.participants_chosen').parent().show();

        // De-Highlight toolbar
        self.$el.find(
            'table.panel-subcontainer tr td.panel-subcontainer-toolbar-column')
            .removeClass('editing');

        // Give precedence to media view IF the subpanel is open
        if (self.$el.find('td.panel-container.collection')
                .hasClass('open')) {
            self.$el.find('.panel-content')
                .removeClass('fluid').addClass('fixed');
            self.$el.find('td.panel-container.collection')
                .removeClass('fixed').addClass('fluid');
        }

        // Get updated text into the preview space - decorate any new links
        jQuery(self.essaySpace).html(tinymce.activeEditor.getContent());
        self.citationView.decorateLinks(self.essaySpace.id);

        jQuery(self.essaySpace).show();
        self.$el.find('td.panhandle-stripe div.label')
            .html('View Inserted Selections');
        self.$el.find('.project-previewbutton')
            .text('Edit');
        self.$el.find('div.asset-view-published').show();
        self.$el.find('h1.project-title').show();
    }

    jQuery(window).trigger('resize');

    return false;
};

ProjectPanelHandler.prototype.showSaveOptions = function(evt) {
    var self = this;

    // Validate title. Not empty or 'Untitled'. At least one author
    if (!self._validTitle(true) || !self._validAuthors(true)) {
        return false;
    }

    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var frm = srcElement.form;
    var element = jQuery(frm).find('div.save-publish-status')[0];

    jQuery(element).dialog({
        buttons: [{text: 'Cancel',
                   click: function() {
                       jQuery(this).dialog('close');
                   }},
                  {text: 'Save',
                   click: function() {
                       self._save = true;
                       jQuery(this).dialog('close');
                   }}
              ],
        create: function(event, ui) {
            jQuery('#id_due_date').datepicker({
                minDate: 0,
                dateFormat: 'mm/dd/yy',
                beforeShow: function(input, inst) {
                    inst.dpDiv.css({
                        top: (input.offsetHeight) + 'px'
                    });
                }
            });
        },
        beforeClose: function(event, ui) {
            if (self._save) {
                self.saveProject(frm);
            }

            self._save = false;
            return true;
        },
        draggable: true,
        resizable: false,
        modal: true,
        width: 450,
        position: {
            my: 'center top',
            at: 'center top',
            of: window,
            collision: 'none'
        },
        zIndex: 10000
    });

    jQuery(element).parent().appendTo(frm);
    return false;
};

ProjectPanelHandler.prototype.saveProject = function(frm) {
    var self = this;

    tinymce.activeEditor.save();

    if (!self._validTitle() || !self._validAuthors()) {
        return false;
    }

    self.$el.find('select[name="participants"] option:selected');
    var data = jQuery(frm).serializeArray();
    data = data.concat(jQuery(document.forms.editparticipants)
        .serializeArray());

    var saveButton = self.$el.find('.project-savebutton').get(0);
    jQuery(saveButton).attr('disabled', 'disabled')
        .text('Saving...')
        .addClass('saving');

    jQuery.ajax({
        type: 'POST',
        url: frm.action,
        data: data,
        dataType: 'json',
        error: function() {
            jQuery(saveButton).removeAttr('disabled')
                .text('Save').removeClass('saving');
            showMessage('There was an error saving your project.',
                        null, 'Error');
        },
        success: function(json, textStatus, xhr) {
            if (json.status === 'error') {
                showMessage(json.msg, null, 'Error');
            } else {
                var lastVersionPublic = self.$el.find(
                    '.last-version-public').get(0);
                if (json.revision.public_url) {
                    jQuery(lastVersionPublic).attr('href',
                                                   json.revision.public_url);
                    jQuery(lastVersionPublic).show();
                } else {
                    jQuery(lastVersionPublic).attr('href', '');
                    jQuery(lastVersionPublic).hide();
                }

                if (json.is_essay_assignment) {
                    self.$el.removeClass('composition')
                        .addClass('assignment');
                    self.$el.find('.composition')
                        .removeClass('composition').addClass('assignment');
                    self.$el.next('.pantab-container')
                        .find('.composition').removeClass('composition')
                        .addClass('assignment');
                    self.$el.prev().removeClass('composition')
                        .addClass('assignment');
                    self.$el.prev().find('div.label')
                         .html('assignment');
                    self.$el.prev().prev().find('.composition')
                        .removeClass('composition').addClass('assignment');

                    self.$el.find('a.project-export').hide();
                    self.$el.find('a.project-print').hide();
                } else {
                    self.$el.removeClass('assignment')
                        .addClass('composition');
                    self.$el.find('.assignment')
                        .removeClass('assignment').addClass('composition');
                    self.$el.next('.pantab-container')
                        .find('.assignment').removeClass('assignment')
                        .addClass('composition');
                    self.$el.prev().removeClass('assignment')
                        .addClass('composition');
                    self.$el.prev().find('div.label')
                        .html('composition');
                    self.$el.prev().prev().find('.assignment')
                        .removeClass('assignment').addClass('composition');

                    self.$el.find('a.project-export').show();
                    self.$el.find('a.project-print').show();
                }

                self.$el.find('.project-visibility-description')
                               .html(json.revision.visibility);

                if (json.revision.due_date) {
                    self.$el.find('.project-due-date')
                                   .html('Due ' + json.revision.due_date);
                } else {
                    self.$el.find('.project-due-date').html('');
                }

                self.revision = json.revision;
                if ('title' in json) {
                    document.title = 'Mediathread ' + json.title;
                }
                self.setDirty(false);
                self.updateRevisions();
            }
            jQuery(saveButton).removeAttr('disabled')
                .removeClass('saving', 1200, function() {
                    jQuery(this).text('Saved'); });
        }
    });

    return true;
};

ProjectPanelHandler.prototype.setDirty = function(isDirty) {
    var self = this;

    if (!isDirty && self.tinymce) {
        // clear the tinymce dirty flags
        tinymce.activeEditor.isNotDirty = true;
    }

    if (isDirty) {
        self.$el.find('.project-savebutton').text('Save');
        // Set a single timer to kick off a save event.
        // If the timer is already active, don't set another one
        // Clear the timer variable at the end
        if (self.dirtyTimer === undefined) {
            self.dirtyTimer = window.setTimeout(function() {
                var frm = self.$el.find('form[name=editproject]');
                self.saveProject(frm[0]);
                self.dirtyTimer = undefined;
            }, 10000);
        }
    } else {
        self.$el.find('.project-savebutton').text('Saved');
        if (self.dirtyTimer !== undefined) {
            window.clearTimeout(self.dirtyTimer);
            self.dirtyTimer = undefined;
        }
    }
};

ProjectPanelHandler.prototype.isDirty = function() {
    return tinymce.activeEditor.isDirty();
};

ProjectPanelHandler.prototype.updateRevisions = function() {
    var self =  this;
    var $elt = jQuery('#project-revisions');

    if ($elt.length > 0) {
        jQuery.ajax({
            type: 'GET',
            url: MediaThread.urls['project-revisions'](
                    self.panel.context.project.id),
            dataType: 'json',
            error: function() {},
            success: function(json, textStatus, xhr) {
                var rendered = Mustache.render(
                    MediaThread.templates.project_revisions, json);
                $elt.html(rendered);
            }
        });
    }
};

ProjectPanelHandler.prototype.beforeUnload = function() {
    var self = this;
    var msg = null;

    // Check tinymce dirty state.
    // For some reason, the instance is not always current
    if (self.isDirty()) {
        msg = 'Changes to your project have not been saved.';
    } else {
        var title = self.$el.find('input[name=title]');
        if (title && title.length > 0) {
            var value = jQuery(title[0]).val();
            if (!value || value.length < 1) {
                msg = 'Please specify a project title.';
            } else if (value === 'Untitled') {
                msg = 'Please update your "Untitled" project title.';
            }
        }
    }

    if (msg) {
        window.panelManager.openPanel(self.$el);
        return msg;
    }
};

ProjectPanelHandler.prototype._bind = function($parent, elementSelector,
                                               event, handler) {
    var elements = $parent.find(elementSelector);
    if (elements.length) {
        jQuery(elements[0]).on(event, handler);
        return true;
    } else {
        return false;
    }
};

ProjectPanelHandler.prototype._validAuthors = function(interactive) {
    var self = this;
    var $select = self.$el.find('select[name="participants"]');
    // Make sure there's at least one author
    var options = $select.find('option:selected');
    if (options.length < 1) {
        if (interactive) {
            showMessage(
                'This project has no authors. ' +
                'Please select at least one author.',
                null, 'Error');
        }
        return false;
    } else {
        return true;
    }
};

ProjectPanelHandler.prototype._validTitle = function(interactive) {
    var self = this;

    var $title = self.$el.find('input.project-title');
    var value = $title.val();
    if (!value || value.length < 1) {
        if (interactive) {
            showMessage('Please specify a project title.', null, 'Error');
        }
        $title.focus();
        return false;
    } else if (value === 'Untitled') {
        if (interactive) {
            showMessage('Please update your "Untitled" project title.',
                        null, 'Error');
        }
        $title.focus();
        return false;
    } else {
        return true;
    }
};
