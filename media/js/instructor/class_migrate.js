(function (jQuery) {
    var global = this;
    
    var Course = Backbone.Model.extend({
        urlRoot: '/_main/api/v1/course/',
        customJSON: function () {
            var json = this.toJSON();
            
            json.projects = 0;
            
            for (var i = 0; i < json.project_set.length; i++) {
                if (json.project_set[i].is_class_visible) {
                    json.projects++;
                }
            }
            
            json.items = 0;
            
            return json;
        }
    });
    
    global.CourseMaterialsView = Backbone.View.extend({
        events : {
            'focus input#available-courses': 'focusAvailableCourses',
            'click #view-materials': 'clickViewMaterials'
        },

        initialize: function (options) {
            _.bindAll(this, "setCourse", "focusAvailableCourses", "render", "clickViewMaterials");
            
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
        
        showProjectDialog: function (evt) {
/**            
            var self = this;
            var element = jQuery(".export-finalcutpro")[0];
            var list  = jQuery(element).find("ul.selections")[0];
            jQuery(list).find('li').remove();
            
            if (this.hasOwnProperty('active_asset_annotations')) {
                for (var i = 0; i < this.active_asset_annotations.length; i++) {
                    var ann = this.active_asset_annotations[i];
                    if (ann.annotation) {
                        var li = "<li>" +
                            "<span class='ui-icon-reverse ui-icon-arrowthick-2-n-s'></span>" +
                            "<input readonly='readonly' type='text' name='" + ann.id + "' value='" + ann.metadata.title + "'></input></li>";
                        
                        jQuery(list).append(li);
                    }
                }
            }
            
            jQuery(list).sortable({ containment: 'parent' }).disableSelection();
            
            jQuery(element).dialog({
                buttons: [{ text: "Export",
                    click: function () {
                        jQuery("form[name=export-finalcutpro]").trigger('submit');
                        jQuery(this).dialog("close");
                    }
                }],
                draggable: true,
                resizable: true,
                modal: true,
                width: 425,
                position: "top",
                zIndex: 10000
            });
            
            return false;
**/            
        },
        
        showItemDialog: function (evt) {
        }
    });
}(jQuery));