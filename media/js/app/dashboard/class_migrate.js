(function (jQuery) {
    var global = this;

    var Asset = Backbone.Model.extend({
        initialize: function (attrs) {
            this.id = attrs['id'];
        }
    });

    var AssetList = Backbone.Collection.extend({
        model: Asset,
        total_sherdnotes: function () {
            var count = 0;
            this.forEach(function (obj) {
                count += obj.get('annotation_count')
            });
            return count;
        }
    });

    var Project = Backbone.Model.extend({
        initialize: function (attrs) {
            this.id = attrs['id'];
        }
    });

    var ProjectList = Backbone.Collection.extend({
        model: Project,
        total_sherdnotes: function () {
            var count = 0;
            this.forEach(function (obj) {
                count += obj.get('annotation_count').length;
            });
            return count;
        }
    });
    
    var Course = Backbone.Model.extend({
        urlRoot: '/dashboard/migrate/materials/',
        parse: function (response) {
            if (response) {
                response.projects = new ProjectList(response.projects);
                response.assets = new AssetList(response.assets);
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
            
            jQuery("#course-title").html(this.model.get("course").title);
            
            jQuery("#available-courses-selector").fadeOut(function () {
                jQuery("#course-materials-container").fadeIn();
            });
        },
        
        renderSelectedList: function () {
            var json = {
                'projects': this.selectedProjects.toJSON(),
                'assets': this.selectedAssets.toJSON()
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
            this.model = new Course({id: courseId});
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
            
            asset_ids = [];
            this.selectedAssets.forEach(function (asset) {
                asset_ids.push(asset.id);
            });
            project_ids = [];
            this.selectedProjects.forEach(function (project) {
               project_ids.push(project.id); 
            });
            
            var data = {
                'fromCourse': this.model.get('id'),
                'on_behalf_of': jQuery("#on_behalf_of").attr("value"),
                'project_ids': project_ids,
                'asset_ids': asset_ids
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
                                
                                self.model.get('projects').forEach(function (project) {
                                    if (!self.selectedProjects.get(project.id)) {
                                        self.selectedProjects.add(project);
                                    }
                                });
                                self.model.get('assets').forEach(function (asset) {
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
                buttons: [{
                    text: "Cancel",
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
                                        var project = self.model.get('projects').get(id);
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
                }],
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
                                            var asset = self.model.get('assets').get(id);
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
            
            var project = this.selectedProjects.get(jQuery(srcElement).attr("name"));
            this.selectedProjects.remove(project.id);
        },
        
        deselectAsset: function (evt) {
            var srcElement = evt.srcElement || evt.target || evt.originalTarget;
            
            var asset = this.selectedAssets.get(jQuery(srcElement).attr("name"));
            this.selectedAssets.remove(asset.id);
        }
        
    });
}(jQuery));