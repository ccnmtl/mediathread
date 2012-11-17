(function (jQuery) {
    var global = this;
    
    var Course = Backbone.Model.extend({
        urlRoot: '/_main/api/v1/course/',
        customJSON: function () {
            var json = this.toJSON();
            
            json.project_set_selections = 0;
            for (var i = 0; i < json.project_set.length; i++) {
                json.project_set_selections += json.project_set[i].selection_count;
            }

            json.items = 0;
            
            return json;
        }
    });
    
    global.CourseMaterialsView = Backbone.View.extend({
        events : {
            'focus input#available-courses': 'focusAvailableCourses',
            'click #view-materials': 'clickViewMaterials',
            'click #import-all': 'importAll',
            'click #import-projects': 'importProjects',
            'click #import-items': 'importItems'
        },

        initialize: function (options) {
            _.bindAll(this, "setCourse", "focusAvailableCourses", "render", "clickViewMaterials", 'importAll', 'importProjects', 'importItems');
            
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
            var json = this.model.customJSON();
            var markup = this.courseTemplate(json);
            jQuery("#course").html(markup);
            jQuery("#course-materials-container").show();
        },
        
        setCourse: function (courseId) {
            this.model = new Course({ id: courseId });
            this.model.on('change', this.render);
            this.model.fetch();
        },
        
        importAll: function (evt) {
            jQuery("#import-all-dialog").dialog({
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
                resizable: false,
                modal: true,
                width: 425,
                zIndex: 10000,
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
            jQuery("#import-projects-dialog").dialog({
                buttons: [{ text: "Cancel",
                            click: function () {
                                jQuery(this).dialog("close");
                            }
                          },
                          { text: 'Import',
                            click: function () {
                                jQuery("div.selected-for-import").show();
                                jQuery(this).dialog("close");
                            }
                          },
                ],
                draggable: true,
                resizable: true,
                modal: true,
                width: 600,
                height: 450,
                zIndex: 10000
            });
            
            return false;
        },
        
        importItems: function (evt) {
            jQuery("#import-items-dialog").dialog({
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
                height: 550,
                zIndex: 10000
            });
            
            return false;
        }
    });
}(jQuery));