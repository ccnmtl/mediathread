/* global STATIC_URL: true */
/* global _propertyCount: true, ajaxDelete: true, MediaThread: true */
/* global Mustache: true, showMessage: true, urlWithCourse */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

var ProjectList = function(config) {
    var self = this;

    self.template_label = config.template_label;
    self.parent = config.parent;
    self.switcher_context = {};
    self.page = 1;
    self.space_owner = config.space_owner;

    jQuery.ajax({
        url: STATIC_URL + 'templates/' +
            config.template + '.mustache?nocache=v2',
        dataType: 'text',
        cache: false, // Chrome && IE have aggressive caching policies.
        success: function(text) {
            MediaThread.templates[config.template] = text;
            self.refresh();
        }
    });

    jQuery(window).on('projectlist.refresh', {'self': self}, function(event) {
        var self = event.data.self;
        self.refresh();
    });

    jQuery(config.parent).on('click', 'ul.pagination li a.page', function(evt) {
        var page = jQuery(this).data('page');
        if (self.page !== page) {
            self.page = page;
            self.refresh();
        }
    });

    return this;
};

ProjectList.prototype.createAssignmentResponse = function(evt) {
    var $elt = jQuery(evt.currentTarget);

    if (!$elt.is('a')) {
        $elt = $elt.parent();
    }

    jQuery.ajax({
        type: 'POST',
        url: MediaThread.urls['project-create'](),
        dataType: 'json',
        data: {'parent': $elt.data('id')},
        success: function(json) {
            // eslint-disable-next-line  scanjs-rules/assign_to_location
            window.location = json.context.project.url;
        }
    });
};

ProjectList.prototype.deleteProject = function(icon) {
    var self = this;

    var link = jQuery(icon).parent()[0];
    var title = jQuery(link).prevAll('a').first().html();
    var objectType = jQuery(link).data('object-type');

    return ajaxDelete(link, jQuery(link).data('container-id'), {
        object_type: objectType,
        msg: 'Are you sure you want to delete ' + title + '?',
        success: function() {
            self.page = 1;
            self.refresh();
        }
    });
};

ProjectList.prototype.refreshUrl = function() {
    var self = this;
    var url;

    if (!self.space_owner) {
        url = MediaThread.urls['all-projects']();
    } else {
        url = MediaThread.urls['your-projects'](self.space_owner);
    }

    url += '?page=' + self.page;
    url = urlWithCourse(url, MediaThread.current_course);

    return url;
};

ProjectList.prototype.refresh = function() {
    var self = this;
    jQuery('.ajaxloader').show();

    jQuery('a.linkRespond').off('click');
    jQuery('a.btnRespond').off('click');
    jQuery('a.btnDeleteResponse').off('click');

    jQuery.ajax({
        url: self.refreshUrl(),
        dataType: 'json',
        cache: false, // Internet Explorer has aggressive caching policies.
        success: function(the_records) {
            self.update(the_records);

            jQuery('[data-toggle="tooltip"]').tooltip();

            jQuery('a.btnRespond').on('click', function(evt) {
                self.createAssignmentResponse(evt);
            });

            jQuery('a.linkRespond').on('click', function(evt) {
                self.createAssignmentResponse(evt);
            });

            jQuery('a.delete-project img').on('click', function(evt) {
                evt.preventDefault();
                self.deleteProject(this);
                return false;
            });
        }
    });
};

ProjectList.prototype.selectOwner = function(username) {
    var self = this;
    jQuery('.ajaxloader').show();

    self.space_owner = username;
    self.page = 1;

    jQuery.ajax({
        type: 'GET',
        url: self.refreshUrl(),
        dataType: 'json',
        error: function() {
            showMessage('There was an error retrieving the project list.',
                null, 'Error');
        },
        success: function(the_records) {
            self.update(the_records);
        }
    });

    return false;
};

ProjectList.prototype.updateSwitcher = function() {
    // hook up switcher choice owner behavior

    var self = this;
    jQuery(self.parent).find('a.switcher-choice.owner')
        .off('click').on('click', function(evt) {
            var srcElement =
                evt.srcElement || evt.target || evt.originalTarget;
            var bits = srcElement.href.split('/');
            var username = bits[bits.length - 1];

            if (username === 'all-class-members') {
                username = null;
            }
            return self.selectOwner(username);
        }
        );
};

ProjectList.prototype.update = function(the_records) {
    var self = this;

    self.switcher_context.owners = the_records.course.group.user_set;
    self.switcher_context.space_viewer = the_records.space_viewer;
    self.switcher_context.selected_view = self.selected_view;

    if (!self.space_owner) {
        self.switcher_context.selected_label = 'All Class Members';
        self.switcher_context.showing_all_items = true;
        self.switcher_context.showing_my_items = false;
        the_records.showing_all_items = true;
    } else if (self.space_owner === the_records.space_viewer.username) {
        self.switcher_context.selected_label = 'Me';
        self.switcher_context.showing_my_items = true;
        self.switcher_context.showing_all_items = false;
        the_records.showing_my_items = true;
    } else {
        self.switcher_context.showing_my_items = false;
        self.switcher_context.showing_all_items = false;
        self.switcher_context.selected_label =
            the_records.space_owner.public_name;
    }

    self.current_records = the_records;

    var n = _propertyCount(the_records.active_filters);
    if (n > 0) {
        the_records.active_filter_count = n;
    }

    self.switcher_context.display_switcher_extras =
        !self.switcher_context.showing_my_items;
    the_records.switcher_collection_chooser = self.switcher_context;
    the_records = jQuery.extend({}, the_records, MediaThread.mustacheHelpers);
    var rendered = Mustache.render(MediaThread.templates.homepage,
        the_records);

    var $el = jQuery('#classwork_table');
    $el.html(rendered).hide().fadeIn('slow');

    self.parent = $el;
    self.updateSwitcher();

    jQuery('.ajaxloader').hide();
};
