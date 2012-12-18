(function (jQuery) {
    var global = this;
    
    var Selection = Backbone.Model.extend({
        
    });

    var SelectionList = Backbone.Collection.extend({
        model: Selection
    });

    var Item = Backbone.Model.extend({
        
    });

    var ItemList = Backbone.Collection.extend({
        model: Item,
        parse: function (response) {
            if (response) {
                response.selections = new SelectionList(response.selections);
            }
            return response;
        }
    });

    var Project = Backbone.Model.extend({
        parse: function (response) {
            if (response) {
                response.item_set = new ItemList(response.item_set);
            }
            return response;
        }
    });

    var ProjectList = Backbone.Collection.extend({
        model: Project
    });
    
    var Course = Backbone.Model.extend({
        urlRoot: '/_main/api/v1/course/',
        parse: function (response) {
            if (response) {
                response.project_set = new ProjectList(response.questions);
                response.item_set = new ItemList(response.questions);
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