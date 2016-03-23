/* global _: true, Backbone: true */
/* global confirmAction: true */

(function() {
    window.CourseRosterView = Backbone.View.extend({
        events: {
            'click .btn-promote': 'onPromote',
            'click .btn-demote': 'onDemote',
            'click .btn-remove': 'onRemove',
            'click .btn-add-uni-user': 'onAddUNIUser'
        },
        initialize: function(options) {
            _.bindAll(this, 'onPromote', 'onDemote', 'onRemove',
                      'onAddUNIUser', 'onActionConfirmed');
            var self = this;

            jQuery(this.el).find('.tablesorter').tablesorter({
                sortList: [[0,0]],
                headerTemplate: '{content} {icon}',
                headers: {
                    '.nosort': {
                        sorter: false
                    },
                }
            });
        },
        onPromote: function(evt) {
            evt.preventDefault();
            var $elt = jQuery(evt.currentTarget);
            this.form = $elt.parents('form').first();
            var name = $elt.data('user-fullname');
            confirmAction(
                'Are you sure you want to promote ' + name + ' to faculty?',
                 this.onActionConfirmed, 'Confirm');
        },
        onDemote: function(evt) {
            evt.preventDefault();
            var $elt = jQuery(evt.currentTarget);
            this.form = $elt.parents('form').first();
            var name = $elt.data('user-fullname');
            confirmAction(
                'Are you sure you want to demote ' + name + ' to student?',
                 this.onActionConfirmed, 'Confirm');
        },
        onRemove: function(evt) {
            evt.preventDefault();
            var $elt = jQuery(evt.currentTarget);
            this.form = $elt.parents('form').first();
            var name = $elt.data('user-fullname');
            confirmAction(
                'Are you sure you want to remove ' + name + ' from the course?',
                 this.onActionConfirmed, 'Confirm');
        },
        onAddUNIUser: function(evt) {
            jQuery(this.el).find('#add-uni-user form').submit();
        },
        onActionConfirmed: function(evt) {
            this.form.submit();  // redirects
        }
    });
})();
