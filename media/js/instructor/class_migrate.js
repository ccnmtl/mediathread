(function (jQuery) {
    var global = this;
    
    var Course = Backbone.Model.extend({
        urlRoot: '/_main/api/v1/course/'
    });
    
    global.CourseMaterialsView = Backbone.View.extend({
        events : {
            'focus input#available-courses': 'focusAvailableCourses'
        },

        initialize: function (options) {
            _.bindAll(this, "setCourse", "focusAvailableCourses", "render", "renderProjects", "renderItems");
            
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
                this.setCourse(this.availableCourses[0].id);
            } else {
                jQuery("#available-courses-selector").show();
                 
                jQuery("#available-courses").autocomplete({
                    source: this.availableCourses,
                    select: function (event, ui) {
                        self.setCourse(ui.item.id);
                    }
                });
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
        },
        
        renderItems: function () {
        },
        
        renderProjects: function () {
        },
        
        setCourse: function (courseId) {
            this.model = new Course({ id: courseId });
            this.model.on('change', this.render);
            this.model.fetch();
        },
    });
}(jQuery));