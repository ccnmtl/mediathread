(function (jQuery) {
    var global = this;
    
    var SherdNote = Backbone.Model.extend({
        
    });

    var SherdNoteList = Backbone.Collection.extend({
        model: SherdNote
    });

    var Asset = Backbone.Model.extend({
        defaults: {
            sherdnote_set: new SherdNoteList()
        },
        initialize: function (attrs) {
            if (attrs.hasOwnProperty("sherdnote_set")) {
                this.set("sherdnote_set", new SherdNoteList(attrs.sherdnote_set));
            }
        }
    });

    var AssetList = Backbone.Collection.extend({
        model: Asset,
        total_sherdnotes: function () {
            var count = 0;
            this.forEach(function (obj) {
                count += obj.get('sherdnote_set').length;
            });
            return count;
        }
    });

    var Project = Backbone.Model.extend({
        defaults: {
            sherdnote_set: new SherdNoteList()
        },
        initialize: function (attrs) {
            if (attrs.hasOwnProperty("sherdnote_set")) {
                this.set("sherdnote_set", new SherdNoteList(attrs.sherdnote_set));
            }
        }
    });

    var ProjectList = Backbone.Collection.extend({
        model: Project,
        total_sherdnotes: function () {
            var count = 0;
            this.forEach(function (obj) {
                count += obj.get('sherdnote_set').length;
            });
            return count;
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
            
            var filters = this.get('facultyString');
            if (filters !== null && filters.length > 0) {
                url += '?';
                url += 'project_set__author__id__in=' + filters;
                url += '&asset_set__sherdnote_set__author__id__in=' + filters;
            }
            
            return url;
        },
        parse: function (response) {
            if (response) {
                response.project_set = new ProjectList(response.project_set);
                response.asset_set = new AssetList(response.asset_set);
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
            'click #clear-all-items': 'clearAllItems'
        },

        initialize: function (options) {
            _.bindAll(this, "setCourse", "focusAvailableCourses", "render",
                "clickViewMaterials", "importAll", "importProjects", "importItems",
                "selectAllItems", "clearAllItems", "selectAllProjects", "clearAllProjects");
            
            this.selectedCourse = undefined;
            this.availableCourses = options.availableCourses;
            this.projectsTemplate = _.template(jQuery("#projects-template").html());
            this.itemsTemplate = _.template(jQuery("#items-template").html());
            this.courseTemplate = _.template(jQuery("#course-template").html());
            
            var self = this;
            // Setup initial state based on user's available courses
            // availableCourses are setup in the Django template
            if (this.availableCourses.length < 1) {
                // The professor is only affiliated with one course. Explain
                jQuery("#no-materials-to-migrate").show();
            } else if (this.availableCourses.length === 1) {
                jQuery("#course-materials-container").show();
                this.setCourse(this.availableCourses[0].id,
                               this.availableCourses[0].faculty_string);
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
            var markup = this.courseTemplate(json);
            jQuery("#course").html(markup);
            jQuery("#course-materials-container").show();
        },
        
        setCourse: function (courseId, courseFaculty) {
            this.model = new Course({id: courseId,
                                     facultyString: courseFaculty.trim()});
            this.model.on('change', this.render);
            this.model.fetch();
        },
        
        migrateCourse: function () {
            // Put up an overlay & a progress indicator.
            
            var data = {
                'fromCourse': this.model.get('id')
            };
            
            jQuery.ajax({
                type: 'POST',
                url: '.',
                data: data,
                dataType: 'json',
                error: function () {
                    // Remove overlay & progress indicator
                    alert('There was an error saving your project.');
                },
                success: function (json, textStatus, xhr) {
                    var msg = "Success! \n";
                    if (json.asset_count) {
                        msg += json.asset_count + " items imported";
                        if (json.note_count) {
                            msg += " with " + json.note_count + " selections";
                        }
                        
                        msg += "\n";
                    }
                    if (json.project_count) {
                        msg += json.project_count + " projects imported";
                    }
                    alert(msg);

                    // Remove overlay & progress indicator
                }
            });
        },
        
        importAll: function (evt) {
            var self = this;
            jQuery("#import-all-dialog").dialog({
                buttons: [{ text: "Cancel",
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                          { text: 'Import',
                            click: function () {
                                jQuery(this).dialog("close");
                                self.migrateCourse();
                            }
                          },
                ],
                draggable: true,
                resizable: false,
                modal: true,
                width: 425,
                open: function () {
                    var container = jQuery(this.el).find('#import-items-dialog')[0];
                    jQuery(container).masonry({
                        itemSelector : '.gallery-item',
                        columnWidth: 3
                    });
                }
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
                          { text: 'Import',
                            click: function () {
                                var lst = jQuery("input.project:checked");
                                if (lst.length > 0) {
                                    jQuery(lst).each(
                                        function (idx, elt) {
                                            var id = jQuery(elt).attr("value");
                                            var type = "project";
                                            var description = jQuery(elt).parent().prev("td").html();
                                            alert(id);
                                            alert(type);
                                            alert(description);
                                        }
                                    );
                                    
                                    jQuery("div.selected-for-import").show();
                                }
                                jQuery(this).dialog("close");
                            }
                          },
                ],
                draggable: true,
                resizable: true,
                modal: true,
                width: 600,
                maxHeight: 450
            });
            
            jQuery(element).parent().appendTo(this.el);
            return false;
        },
        
        selectAllProjects: function (evt) {
            jQuery("div.import-stuff input:checkbox").attr("checked", "checked");
        },
        
        clearAllProjects: function (evt) {
            jQuery("div.import-stuff input:checkbox").removeAttr("checked");
        },
        
        importItems: function (evt) {
            var element = jQuery("#import-items-dialog");
            jQuery(element).dialog({
                buttons: [{ text: "Cancel",
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                          { text: 'Import',
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                ],
                draggable: true,
                resizable: true,
                modal: true,
                width: 725,
                maxHeight: 425
            });
            
            jQuery(element).parent().appendTo(this.el);
            return false;
        },
        
        selectAllItems: function (evt) {
            jQuery("h4.asset_title input:checkbox").attr("checked", "checked");
        },
        
        clearAllItems: function (evt) {
            jQuery("h4.asset_title input:checkbox").not(".required").removeAttr("checked");
        }
    });
}(jQuery));