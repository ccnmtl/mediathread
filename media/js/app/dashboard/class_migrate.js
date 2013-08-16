(function (jQuery) {
    var global = this;
    
    var SherdNote = Backbone.Model.extend({
        
    });

    var SherdNoteList = Backbone.Collection.extend({
        model: SherdNote
    });

    var Asset = Backbone.Model.extend({
        defaults: {
            annotations: new SherdNoteList()
        },
        initialize: function (attrs) {
            if (attrs.hasOwnProperty("annotations")) {
                this.set("annotations", new SherdNoteList(attrs.annotations));
            }
        }
    });

    var AssetList = Backbone.Collection.extend({
        model: Asset,
        urlRoot:  '/_main/api/v1/asset/',
        total_sherdnotes: function () {
            var count = 0;
            this.forEach(function (obj) {
                count += obj.get('annotations').length;
            });
            return count;
        },
        getByDataId: function (id) {
            var internalId = this.urlRoot + id + '/';
            return this.get(internalId);
        }
    });

    var Project = Backbone.Model.extend({
        defaults: {
            annotations: new SherdNoteList()
        },
        initialize: function (attrs) {
            if (attrs.hasOwnProperty("annotations")) {
                this.set("annotations", new SherdNoteList(attrs.annotations));
            }
        }
    });

    var ProjectList = Backbone.Collection.extend({
        model: Project,
        urlRoot:  '/_main/api/v1/project/',
        total_sherdnotes: function () {
            var count = 0;
            this.forEach(function (obj) {
                count += obj.get('annotations').length;
            });
            return count;
        },
        getByDataId: function (id) {
            var internalId = this.urlRoot + id + '/';
            return this.get(internalId);
        }
    });
    
    var Course = Backbone.Model.extend({
        defaults: {
            project_set: new ProjectList(),
            asset_set: new AssetList()
        },
        urlRoot:  '/_main/api/v1/course/',
        url: function () {
            var url = Backbone.Model.prototype.url.apply(this);
            
            var filters = this.get('facultyIds');
            if (filters !== null && filters.length > 0) {
                url += '?';
                url += 'project_set__author__id__in=' + filters;
                url += '&asset_set__sherdnote_set__author__id__in=' + filters;
                /* @TODOurl += '&asset_set__sherdnote_set__range1__isnull=False';*/
                url += '&order_by=title';
            }
            
            return url;
        },
        parse: function (response) {
            if (response) {
                response.project_set = new ProjectList(response.project_set);
                
                // filter archives
                var assets = [];
                for (var i = 0; i < response.asset_set.length; i++) {
                    if (response.asset_set[i].primary_type !== 'archive') {
                        assets.push(response.asset_set[i]);
                    }
                }
                response.asset_set = new AssetList(assets);
            }
            return response;
        }
    });
    
    global.CourseMaterialsView = Backbone.View.extend({
        events : {
            'focus input#available-courses': 'focusAvailableCourses',
            'click #view-materials': 'clickViewMaterials',
            'click #import-all': 'importAll',
            'click #import-projects': 'importProjects',
            'click #select-all-projects': 'selectAllProjects',
            'click #clear-all-projects': 'clearAllProjects',
            'click #import-items': 'importItems',
            'click #select-all-items': 'selectAllItems',
            'click #clear-all-items': 'clearAllItems',
            'click #import-selected': 'migrateCourseMaterials',
            'click #clear-selected': 'clearSelectedMaterials',
            'click #switch-course': 'switchCourse',
            'click input.deselect-project': 'deselectProject',
            'click input.deselect-asset': 'deselectAsset'
        },

        initialize: function (options) {
            _.bindAll(this, "setCourse", "focusAvailableCourses", "render",
                "clickViewMaterials", "importAll", "importProjects", "importItems",
                "selectAllItems", "clearAllItems", "selectAllProjects", "clearAllProjects",
                "renderSelectedList", "switchCourse", "setCourse",
                "deselectProject", "deselectAsset", "clearSelectedMaterials");
            
            this.selectedCourse = undefined;
            this.availableCourses = options.availableCourses;
            
            this.courseTemplate = _.template(jQuery("#course-template").html());
            this.selectedTemplate = _.template(jQuery("#selected-template").html());
            
            this.selectedProjects = new ProjectList();
            this.selectedAssets = new AssetList();
            this.selectedProjects.on("add remove", this.renderSelectedList);
            this.selectedAssets.on("add remove", this.renderSelectedList);
            
            this.is_staff = jQuery("#is-staff").attr("value") === "True";
            this.role_in_course = jQuery("#role-in-course").attr("value");
            
            var self = this;
            
            jQuery(window).resize(function () {
                self.resize();
            });
            
            // Setup initial state based on user's available courses
            // availableCourses are setup in the Django template
            if (this.availableCourses.length < 1) {
                // The professor is only affiliated with one course. Explain
                jQuery("#no-materials-to-migrate").show();
            } else if (this.availableCourses.length === 1) {
                jQuery("#course-materials-container").show();
                this.setCourse(this.availableCourses[0].id);
            } else {
                jQuery("#available-courses-selector").show();
                 
                jQuery("#available-courses").autocomplete({
                    source: this.availableCourses,
                    select: function (event, ui) {
                        if (self.selectedCourse === undefined ||
                            confirm("Are you sure?")) {
                            self.selectedCourse = ui.item.id;
                            return true;
                        } else {
                            
                            return false;
                        }
                    }
                });
            }
        },
        clickViewMaterials: function (evt) {
            if (this.selectedCourse !== undefined) {
                this.setCourse(this.selectedCourse);
            }
        },
        
        focusAvailableCourses: function (evt) {
            var srcElement = evt.srcElement || evt.target || evt.originalTarget;
            if (jQuery(srcElement).attr("value") === "Type course name here") {
                jQuery(srcElement).attr("value", "");
                jQuery(srcElement).removeClass("default");
            }
        },
        
        render: function () {
            var json = this.model.toJSON();
            
            json.is_staff = this.is_staff;
            json.role_in_course = this.role_in_course;
            
            var markup = this.courseTemplate(json);
            jQuery("#course").html(markup);
            
            jQuery("#course-title").html(this.model.get("title"));
            
            jQuery("#available-courses-selector").fadeOut(function () {
                jQuery("#course-materials-container").fadeIn();
            });
        },
        
        renderSelectedList: function () {
            var json = {
                'project_set': this.selectedProjects.toJSON(),
                'asset_set': this.selectedAssets.toJSON()
            };
            var markup = this.selectedTemplate(json);
            jQuery("#selected-for-import").html(markup);
            if (this.selectedProjects.length > 0 ||
                this.selectedAssets.length > 0) {
                jQuery("#selected-for-import").show();
                jQuery(window).trigger("resize");
            } else {
                jQuery("#selected-for-import").hide();
            }
        },
        
        resize: function () {
            var visible = getVisibleContentHeight();
            visible -= jQuery("div.dashboard-module-header").height();
            visible -= jQuery("#course-title").height();
            visible -= jQuery("#footer").height();
            jQuery("#to_import").css('height', (visible - 20) + 'px');
        },
        
        setCourse: function (courseId) {
            var facultyIds = "";
            
            for (var i = 0; i < this.availableCourses.length; i++) {
                if (this.availableCourses[i].id === courseId) {
                    facultyIds = this.availableCourses[i].faculty_ids;
                    break;
                }
            }
            
            this.model = new Course({id: courseId,
                                     facultyIds: facultyIds});
            this.model.on('change', this.render);
            this.model.fetch();
        },
        
        switchCourse: function () {
            this.selectedCourse = undefined;
            
            this.selectedProjects.off("add remove");
            this.selectedAssets.off("add remove");

            this.selectedProjects = new ProjectList();
            this.selectedAssets = new AssetList();

            this.selectedProjects.on("add remove", this.renderSelectedList);
            this.selectedAssets.on("add remove", this.renderSelectedList);
            
            jQuery("#course-materials-container").fadeOut();
            jQuery("#course").html("");
            jQuery("#selected-for-import").fadeOut();
            jQuery("#selected-for-import").html("");
            jQuery("#available-courses-selector").fadeIn();
            jQuery("#available-courses").val("Type course name here");
            jQuery("#available-courses").addClass("default");
            jQuery("#course-title").html("");
        },
        
        migrateCourseMaterials: function () {
            var self = this;
            // @todo - put up an overlay & a progress indicator.
            
            var data = {
                'fromCourse': this.model.get('id'),
                'on_behalf_of': jQuery("#on_behalf_of").attr("value"),
                'project_set': JSON.stringify(this.selectedProjects.toJSON()),
                'asset_set': JSON.stringify(this.selectedAssets.toJSON())
            };
            
            jQuery.ajax({
                type: 'POST',
                url: '.',
                data: data,
                dataType: 'json',
                error: function () {
                    // Remove overlay & progress indicator
                    showMessage('There was an error migrating these course materials.');
                },
                success: function (json, textStatus, xhr) {
                    var msg = "";
                    if (json.asset_count) {
                        msg += json.asset_count + " items imported<br />";
                        if (json.note_count) {
                            msg += " with " + json.note_count + " selection(s)<br />";
                        }
                    }
                    if (json.project_count) {
                        msg += json.project_count + " projects imported";
                    }
                    if (json.error) {
                        msg = msg;
                    }
                    showMessage(msg, function() {                        
                        jQuery("#selected-for-import").fadeOut();
                        jQuery("#selected-for-import").html("");
                        
                        self.selectedProjects.reset();
                        self.selectedAssets.reset();
                    });
                }
            });
        },
        
        clearSelectedMaterials: function (evt) {
            jQuery("#selected-for-import").fadeOut();
            jQuery("#selected-for-import").html("");
            this.selectedProjects.reset();
            this.selectedAssets.reset();
        },
        
        importAll: function (evt) {
            var self = this;
            jQuery("#import-all-dialog").dialog({
                buttons: [{ text: "Cancel",
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                          { text: 'Select',
                            click: function () {
                                jQuery(this).dialog("close");
                                
                                self.model.get('project_set').forEach(function (project) {
                                    if (!self.selectedProjects.get(project.id)) {
                                        self.selectedProjects.add(project);
                                    }
                                });
                                self.model.get('asset_set').forEach(function (asset) {
                                    if (!self.selectedAssets.get(asset.id)) {
                                        self.selectedAssets.add(asset);
                                    }
                                });
                            }
                          }
                ],
                draggable: true,
                resizable: false,
                modal: true,
                width: 425
            });
            
            return false;
        },
        
        importProjects: function (evt) {
            var self = this;
            var element = jQuery("#import-projects-dialog");
            jQuery(element).dialog({
                buttons: [{ text: "Cancel",
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                          { text: 'Select',
                            click: function () {
                                var lst = jQuery("input.project");
                                if (lst.length > 0) {
                                    jQuery(lst).each(
                                        function (idx, elt) {
                                            var id = jQuery(elt).attr("value");
                                            var project = self.model.get('project_set').getByDataId(id);
                                            if (jQuery(elt).is(":checked")) {
                                                if (!self.selectedProjects.get(project)) {
                                                    self.selectedProjects.add(project, {silent: true});
                                                }
                                                jQuery(elt).removeAttr('checked');
                                            } else {
                                                self.selectedProjects.remove(project, {silent: true});
                                            }
                                        }
                                    );
                                    
                                    self.renderSelectedList();
                                }
                                jQuery(this).dialog("close");
                            }
                          }
                ],
                draggable: true,
                resizable: true,
                modal: true,
                width: 600,
                height: 450,
                maxHeight: 450,
                position: "center"
            });
            
            jQuery(element).parent().appendTo(this.el);
            return false;
        },
        
        importItems: function (evt) {
            var self = this;
            var element = jQuery("#import-items-dialog");
            jQuery(element).dialog({
                buttons: [{ text: "Cancel",
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                          { text: 'Select',
                            click: function () {
                                var lst = jQuery("input.asset");
                                if (lst.length > 0) {
                                    jQuery(lst).each(
                                        function (idx, elt) {
                                            var id = jQuery(elt).attr("value");
                                            var asset = self.model.get('asset_set').getByDataId(id);
                                            if (jQuery(elt).is(":checked")) {
                                                if (!self.selectedAssets.get(asset)) {
                                                    self.selectedAssets.add(asset);
                                                }
                                                jQuery(elt).removeAttr('checked');
                                            } else {
                                                self.selectedAssets.remove(asset);
                                            }
                                        }
                                    );
                                    
                                    self.renderSelectedList();
                                }
                                jQuery(this).dialog("close");
                            }
                          }
                ],
                draggable: true,
                resizable: true,
                modal: true,
                width: 600,
                height: 450,
                maxHeight: 450
            });
            
            jQuery(element).parent().appendTo(this.el);
            return false;
        },
        
        selectAllItems: function (evt) {
            jQuery("div.import-stuff input:checkbox.asset").attr("checked", "checked");
        },
        
        clearAllItems: function (evt) {
            jQuery("div.import-stuff input:checkbox.asset").removeAttr("checked");
        },
        
        selectAllProjects: function (evt) {
            jQuery("div.import-stuff input:checkbox.project").attr("checked", "checked");
        },
        
        clearAllProjects: function (evt) {
            jQuery("div.import-stuff input:checkbox.project").removeAttr("checked");
        },
        
        deselectProject: function (evt) {
            var srcElement = evt.srcElement || evt.target || evt.originalTarget;
            
            var project = this.selectedProjects.getByDataId(jQuery(srcElement).attr("name"));
            this.selectedProjects.remove(project.id);
        },
        
        deselectAsset: function (evt) {
            var srcElement = evt.srcElement || evt.target || evt.originalTarget;
            
            var asset = this.selectedAssets.getByDataId(jQuery(srcElement).attr("name"));
            this.selectedAssets.remove(asset.id);
        }
        
    });
}(jQuery));