/* global _: true, Backbone: true */
/* global showMessage: true */

(function() {
    window.CourseRosterView = Backbone.View.extend({
        events: {
            'click .btn-promote': 'onPromote',
            'click .btn-demote': 'onDemote',
        },
        initialize: function(options) {
            _.bindAll(this, 'onPromote', 'onDemote', 'onActionConfirmed');
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
            showMessage(
                'Are you sure you want to promote ' + name + ' to faculty?',
                 this.onActionConfirmed, 'Confirm');
        },
        onDemote: function(evt) {
            evt.preventDefault();
            var $elt = jQuery(evt.currentTarget);
            this.form = $elt.parents('form').first();
            var name = $elt.data('user-fullname');
            showMessage(
                'Are you sure you want to demote ' + name + ' to student?',
                 this.onActionConfirmed, 'Confirm');
        },
        onActionConfirmed: function(evt) {
            this.form.submit();  // redirects
        }
    });
})();
