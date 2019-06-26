/* global CitationView: true */
/* global AssignmentEditView: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

(function(jQuery) {
    var global = this;

    global.SelectionAssignmentEditView = AssignmentEditView.extend({
        events: {
            'click .next': 'onNext',
            'click .prev': 'onPrev',
            'click .save': 'onSave',
            'mouseover .asset-table .gallery-item': 'onGalleryItemMouseOver',
            'mouseleave .asset-table': 'onGalleryMouseOut',
            'click .gallery-item-overlay': 'onGalleryItemSelect',
            'keypress form[name="selection-assignment-edit"]': 'onFormKeyPress'
        },
        initialize: function(options) {
            _.bindAll(this, 'onNext', 'onPrev', 'onSave', 'onFormKeyPress',
                'onGalleryItemMouseOver', 'onGalleryMouseOut',
                'onGalleryItemSelect', 'beforeUnload');

            AssignmentEditView.prototype.initialize.apply(this, arguments);

            // Setup the media display window.
            this.citationView = new CitationView();
            this.citationView.init({
                'default_target': 'asset-workspace-videoclipbox',
                'presentation': 'medium',
                'clipform': false,
                'autoplay': false
            });
        },
        validate: function(pageContent) {
            if (pageContent === 'choose-item') {
                return jQuery('input[name="item"]').val() !== '';
            }
            return AssignmentEditView.prototype.validate.apply(this, arguments);
        },
        showPage: function(pageContent) {
            if (pageContent === 'instructions') {
                jQuery('#sliding-content-container').addClass('hidden');
                jQuery('.asset-view-publish-container').addClass('hidden');
            } else if (pageContent === 'choose-item') {
                jQuery('#sliding-content-container').removeClass('hidden');
                jQuery('.asset-view-publish-container').addClass('hidden');
                jQuery(window).trigger('resize');
            } else {
                jQuery('#sliding-content-container').addClass('hidden');
                jQuery('.asset-view-publish-container').removeClass('hidden');
                var itemId = jQuery('input[name="item"]').val();
                this.citationView.openCitationById(null, itemId, null);
            }

            AssignmentEditView.prototype.showPage.apply(this, arguments);
        },
        onGalleryItemMouseOver: function(evt) {
            this.hoverItem = evt.currentTarget;
            var $elt = jQuery(evt.currentTarget);
            var $overlay = jQuery('.gallery-item-overlay').first();
            $overlay.css('top', $elt.position().top);
            $overlay.css('left', $elt.position().left);
            $overlay.css('width', $elt.outerWidth());
            $overlay.css('height', $elt.outerHeight());
            $overlay.removeClass('hidden');
        },
        onGalleryMouseOut: function(evt) {
            delete this.hoverItem;
            var $overlay = jQuery('.gallery-item-overlay');
            $overlay.addClass('hidden');
        },
        onGalleryItemSelect: function(evt) {
            if (!this.hoverItem) {
                return;
            }
            jQuery('.has-error').removeClass('has-error');

            var pk = jQuery(this.hoverItem).attr('data-id');
            jQuery('input[name="item"]').val(pk);

            var clone = jQuery.clone(this.hoverItem);
            jQuery(clone).attr('style', 'float: none');
            jQuery('.selected-item div').replaceWith(clone);

            delete this.hoverItem;

            // scroll to top of page
            jQuery('body').scrollTop(0);
        }
    });
}(jQuery));
