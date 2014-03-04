var ProjectList = function (config) {
    var self = this;
    self.template_label = config.template_label;
    self.parent = config.parent;
    self.switcher_context = {};
    
    jQuery.ajax({
        url: '/media/templates/' + config.template + '.mustache?nocache=v2',
        dataType: 'text',
        cache: false, // Chrome && Internet Explorer has aggressive caching policies.
        success: function (text) {
            MediaThread.templates[config.template] = Mustache.template(config.template, text);
            self.refresh(config);
        }
    });
    
    jQuery(window).bind('projectlist.refresh', { 'self': self }, function (event) {
        var self = event.data.self;
        self.refresh(config);
    });
    
    return this;
};

ProjectList.prototype.createAssignmentResponse = function (evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    
    if (!jQuery(srcElement).is("a")) {
        srcElement = jQuery(srcElement).parent();
    }
    
    var params = { 'parent': jQuery(srcElement).data("id") };
    
    jQuery.ajax({
        type: 'POST',
        url: MediaThread.urls['project-create'](),
        dataType: 'json',
        data: params,
        success: function (json) {
            window.location = json.context.project.url;
        }
    });
};

ProjectList.prototype.deleteAssignmentResponse = function (evt) {
    var self = this;
    var srcElement = evt.srcElement || evt.target || evt.originalTarget;
    var link = jQuery(srcElement).parent()[0];
    var data_id = jQuery(link).data("id");
    
    return ajaxDelete(link, data_id, {
        object_type: 'assignment response',
        success: function () {
            self.refresh(self.config);
        }
    });
};

ProjectList.prototype.refresh = function (config) {
    var self = this;
    var url;
        
    if (config.view === 'all' || !config.space_owner) {
        url = MediaThread.urls['all-projects']();
    } else {
        url = MediaThread.urls['your-projects'](config.space_owner);
    }
    
    jQuery("a.linkRespond").unbind("click");
    jQuery("a.btnRespond").unbind("click");
    jQuery("a.btnDeleteResponse").unbind("click");
    
    jQuery.ajax({
        url: url,
        dataType: 'json',
        cache: false, // Internet Explorer has aggressive caching policies.
        success: function (the_records) {
            self.update(the_records);
            
            jQuery("a.btnRespond").bind("click", function (evt) {
                self.createAssignmentResponse(evt);
            });
            
            jQuery("a.linkRespond").bind("click", function (evt) {
                self.createAssignmentResponse(evt);
            });

            
            jQuery("a.btnDeleteResponse").bind("click", function (evt) {
                self.deleteAssignmentResponse(evt);
            });
        }
    });
};

ProjectList.prototype.selectOwner = function (username) {
    var self = this;
    var url = username ? MediaThread.urls['your-projects'](username) : MediaThread.urls['all-projects']();
    
    jQuery.ajax({
        type: 'GET',
        url: url,
        dataType: 'json',
        error: function () {
            showMessage('There was an error retrieving the project list.');
        },
        success: function (the_records) {
            self.update(the_records);
        }
    });
    
    return false;
};

ProjectList.prototype.getShowingAllItems = function (json) {
    return !json.hasOwnProperty('space_owner');
};

ProjectList.prototype.getSpaceUrl = function (active_tag, active_modified) {
    var self = this;
    if (self.getShowingAllItems(self.current_records)) {
        return MediaThread.urls['all-projects']();
    } else {
        return MediaThread.urls['your-projects'](self.current_records.space_owner.username);
    }
};

ProjectList.prototype.updateSwitcher = function () {
    var self = this;
    self.switcher_context.display_switcher_extras = !self.switcher_context.showing_my_items;
    Mustache.update("switcher_collection_chooser", self.switcher_context, { parent: self.parent });
    
    // hook up switcher choice owner behavior
    jQuery(self.parent).find("a.switcher-choice.owner").unbind('click').click(function (evt) {
        var srcElement = evt.srcElement || evt.target || evt.originalTarget;
        var bits = srcElement.href.split("/");
        var username = bits[bits.length - 1];
        
        if (username === "all-class-members") {
            username = null;
        }
        return self.selectOwner(username);
    });

};

ProjectList.prototype.update = function (the_records) {
    var self = this;
    self.switcher_context.owners = the_records.course.group.user_set;
    self.switcher_context.space_viewer = the_records.space_viewer;
    self.switcher_context.selected_view = self.selected_view;
    
    if (self.getShowingAllItems(the_records)) {
        self.switcher_context.selected_label = "All Class Members";
        self.switcher_context.showing_all_items = true;
        self.switcher_context.showing_my_items = false;
        the_records.showing_all_items = true;
    } else if (the_records.space_owner.username === the_records.space_viewer.username) {
        self.switcher_context.selected_label = "Me";
        self.switcher_context.showing_my_items = true;
        self.switcher_context.showing_all_items = false;
        the_records.showing_my_items = true;
    } else {
        self.switcher_context.showing_my_items = false;
        self.switcher_context.showing_all_items = false;
        self.switcher_context.selected_label = the_records.space_owner.public_name;
    }
    
    self.current_records = the_records;
    
    var n = _propertyCount(the_records.active_filters);
    if (n > 0) {
        the_records.active_filter_count = n;
    }
    
    Mustache.update(self.template_label, the_records, {
        parent: self.parent,
        pre: function (elt) { jQuery(elt).hide(); },
        post: function (elt) {
            self.updateSwitcher();
            
            jQuery(elt).fadeIn("slow");
        }
    });
};
    