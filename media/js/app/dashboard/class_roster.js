/* global showMessage: true */

(function() {
    window.CourseRosterView = Backbone.View.extend({
        events: {
            'click .btn-promote': 'onPromote',
            'click .btn-demote': 'onDemote',
            'click .btn-remove': 'onRemove',
            'click .btn-add-uni-user': 'onAddUNIUser',
            'click .btn-invite_email-user': 'onInviteEmailUser'
        },
        initialize: function(options) {
            _.bindAll(this, 'onPromote', 'onDemote', 'onRemove',
                'onAddUNIUser', 'onInviteEmailUser',
                'onActionConfirmed');

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
                'Are you sure you want to promote ' + name + ' to instructor?',
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
        onRemove: function(evt) {
            evt.preventDefault();
            var $elt = jQuery(evt.currentTarget);
            this.form = $elt.parents('form').first();
            var name = $elt.data('user-fullname');
            showMessage(
                'Are you sure you want to remove ' + name + ' from the course?',
                this.onActionConfirmed, 'Confirm');
        },
        onActionConfirmed: function(evt) {
            this.form.submit();  // redirects
            delete this.form;
        },
        onAddUNIUser: function(evt) {
            evt.stopImmediatePropagation();
            var $frm = jQuery(this.el).find('#add-uni-user form').first();
            if ($frm.find('textarea[name="unis"]').val() === '') {
                $frm.addClass('has-error');
                return false;
            }

            $frm.submit();
        },
        onInviteEmailUser: function(evt) {
            evt.stopImmediatePropagation();
            var $frm = jQuery(this.el).find('#invite-email-user form').first();
            if ($frm.find('textarea[name="emails"]').val() === '') {
                $frm.addClass('has-error');
                return false;
            }
            $frm.submit();
        }
    });
})();
