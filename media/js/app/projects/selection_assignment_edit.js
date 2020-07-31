/* global CitationView: true */
/* global AssignmentEditView: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function(jQuery) {
    var global = this;

    global.SelectionAssignmentEditView = AssignmentEditView.extend({
        events: {
            'click .next': 'onNext',
            'click .prev': 'onPrev',
            'click .save': 'onSave'
        },
        initialize: function(options) {
            _.bindAll(this, 'onNext', 'onPrev', 'onSave', 'beforeUnload');

            AssignmentEditView.prototype.initialize.apply(this, arguments);
        },
        validate: function(pageContent) {
            if (pageContent === 'choose-item') {
                return jQuery('select.select-asset').val() !== null;
            }
            return AssignmentEditView.prototype.validate.apply(this, arguments);
        },
        showPage: function(pageContent) {
            if (pageContent === 'instructions') {
                jQuery('#asset-container').addClass('hidden');
                jQuery('.asset-view-publish-container').addClass('hidden');
            } else if (pageContent === 'choose-item') {
                jQuery('#asset-container').removeClass('hidden');
                jQuery('.asset-view-publish-container').addClass('hidden');
                jQuery(window).trigger('resize');
            } else {
                jQuery('#asset-container').addClass('hidden');
                jQuery('.asset-view-publish-container').removeClass('hidden');
            }

            AssignmentEditView.prototype.showPage.apply(this, arguments);
        }
    });
}(jQuery));
