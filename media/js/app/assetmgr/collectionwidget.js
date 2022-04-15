/* global _propertyCount: true, ajaxDelete: true, djangosherd: true */
/* global djangosherd_adaptAsset: true, MediaThread: true */
/* global Mustache: true, Sherd: true, urlWithCourse: true */
/* global CitationView: true, showMessage: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

/**
 * Listens For:
 * asset.on_delete > refresh
 * annotation.on_create > refresh
 * annotation.on_save > refresh
 * annotation.on_delete > refresh
 * collection.open >
 *
 * Signals:
 * asset.edit > when edit in place is clicked
 * asset.on_delete > after ajaxDelete is called
 * asset.select > when an asset is selected
 * asset.update > when an asset was updated
 */

var CollectionWidget = function() {
    this.loading = false;
    this.template = 'collectionwidget';
    this.limits = {offset: 0, limit: 20};
    this.currentRecords =
        {'space_owner': {'username': MediaThread.current_username}};

    this.$modal = jQuery('#collection-modal');
    this.$el = this.$modal.find('.collection-view');
    this.$quickEditView = this.$modal.find('.quick-edit');

    this.switcher_context = jQuery.extend({}, MediaThread.mustacheHelpers);

    var self = this;
    jQuery.when(
        self.getCourse(),
        self.getVocabulary(),
        MediaThread.loadTemplate([self.template]),
        MediaThread.loadTemplate([self.template + '_quickedit'])
    ).done(function(courseReq, vocabularyReq) {
        self.owners = courseReq[0].objects[0].group.user_set;
        self.vocabulary = vocabularyReq[0].objects;
        self.postInitialize();
    }).fail(function() {
        // eslint-disable-next-line no-console
        console.error('Loading error in CollectionWidget constructor');
    });
};

CollectionWidget.prototype.postInitialize = function() {
    var html = Mustache.render(MediaThread.templates[this.template],
        MediaThread.mustacheHelpers);
    this.$el.html(html);

    html = Mustache.render(MediaThread.templates[this.template + '_quickedit'],
        MediaThread.mustacheHelpers);

    this.$quickEditView.html(html);

    this.mapSignals();
    this.mapEvents();
    this.refresh();
};

CollectionWidget.prototype.mapSignals = function() {
    var self = this;

    jQuery(window).on('annotation.on_cancel', {'self': this}, function(event) {
        self.onCancel();
    });

    jQuery(window).on('asset.on_delete annotation.on_delete', {'self': this},
        function(event) {
            self.refresh();
        });

    jQuery(window).on('annotation.on_create annotation.on_save', {'self': this},
        function(event, params) {
            self.onSave(event, params);
        });

    jQuery(window).on(
        'collection.open', {
            'self': this
        }, function(event, params) {
            self.$quickEditView.hide();
            self.$el.show();
            self.open('gallery', params);
        });
    jQuery(window).on('collection.asset.edit', {'self': this},
        function(event, params) {
            self.open('edit', params);
            self.quickEdit('Edit Item', 'asset.edit', params.assetId);
        }
    );
    jQuery(window).on('collection.annotation.edit', {'self': this},
        function(event, params) {
            self.open('edit', params);
            self.quickEdit(
                'Edit Selection', 'annotation.edit',
                params.assetId, params.annotationId);
        }
    );
    jQuery(window).on('collection.annotation.create', {'self': this},
        function(event, params) {
            self.open('create', params);
            self.quickEdit(
                'Create Selection', 'annotation.create',
                params.assetId);
        }
    );
};

CollectionWidget.prototype.mapEvents = function() {
    var self = this;
    self.$el.on('click', '.filter-widget h3', function(evt) {
        jQuery(evt.currentTarget).parent().toggleClass('collapsed');
        jQuery(window).trigger('resize');
    });

    self.$el.on('blur', 'input[name="search-text"]', function(evt) {
        self.currentRecords.active_filters.search_text =
            self.$el.find('input[name="search-text"]').val();
    });

    self.$el.on('keyup', 'input[name="search-text"]', function(evt) {
        if (evt.keyCode === 13) {
            evt.preventDefault();
            self.currentRecords.active_filters.search_text =
                self.$el.find('input[name="search-text"]').val();
            return self.filter();
        }
    });

    self.$el.on('click', '.btn-search-text', function(evt) {
        self.currentRecords.active_filters.search_text =
            self.$el.find('input[name="search-text"]').val();
        return self.filter();
    });

    self.$el.on(
        'click', 'a.switcher-choice.filterbydate', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.href.split('/');
            var filterName = bits[bits.length - 1];

            if (filterName === 'all') {
                self.currentRecords.active_filters.modified = '';
            } else {
                self.currentRecords.active_filters.modified = filterName;
            }
            return self.filter();
        });

    self.$el.on(
        'click', 'a.switcher-choice.filterbymedia', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.href.split('/');
            var filterName = bits[bits.length - 1];

            if (filterName === 'all') {
                self.currentRecords.active_filters.media_type = '';
            } else {
                self.currentRecords.active_filters.media_type = filterName;
            }
            return self.filter();
        });

    self.$el.on(
        'change', '.switcher-tool select.vocabulary', function(evt) {
            var option = evt.added || evt.removed;
            var vocab = jQuery(option.element).parent().attr('data-id');
            if (!Object.prototype.hasOwnProperty.call(
                self.currentRecords.active_filters, vocab)) {
                self.currentRecords.active_filters[vocab] = [];
            }

            if (evt.added) {
                self.currentRecords.active_filters[vocab].push(option.id);
            } else if (evt.removed) {
                var index = self.currentRecords.active_filters[vocab]
                    .indexOf(option.id);
                self.currentRecords.active_filters[vocab].splice(index, 1);
            }
            return self.filter();
        });

    self.$el.on(
        'change', '.switcher-tool select.course-tags', function() {
            var $elt = self.$el.find('select.course-tags');
            self.currentRecords.active_filters.tag = $elt.val();
            return self.filter();
        });

    self.$el.on(
        'click', 'a.collection-choice.edit-asset', function(evt) {
            var bits = evt.currentTarget.href.split('/');
            var assetId = bits[bits.length - 1];
            self.quickEdit('Edit Item', 'asset.edit', assetId);
            return false;
        });

    self.$el.on(
        'click', 'a.collection-choice.delete-asset', function(evt) {
            var bits = evt.currentTarget.href.split('/');
            var asset_id = bits[bits.length - 1];
            self.deleteAsset(asset_id);
            return false;
        });

    self.$el.on(
        'click', 'a.collection-choice.delete-annotation', function(evt) {
            var bits = evt.currentTarget.href.split('/');
            return self.deleteAnnotation(bits[bits.length - 1]);
        });

    self.$el.on(
        'click', 'a.collection-choice.create-annotation', function(evt) {
            var bits = evt.currentTarget.href.split('/');
            var assetId = bits[bits.length - 1];
            self.quickEdit('Create Selection', 'annotation.create', assetId);
            return false;
        });

    self.$el.on('click', 'a.collection-choice.edit-annotation', function(evt) {
        var bits = evt.currentTarget.href.split('/');
        var annotationId = bits[bits.length - 1];
        var assetId = jQuery('#annotation-' + annotationId)
            .parents('div.record')
            .children('input.record').attr('value');
        self.quickEdit(
            'Edit Selection', 'annotation.edit', assetId, annotationId);
        return false;
    });

    self.$el.on('click', 'a.page-link', function(evt) {
        const page = jQuery(evt.target).data('page-number');
        const offset = (page - 1) * self.limits.limit;
        self.refresh(offset, true);
        return false;
    });

    self.$el.on('click', '.clickableCitation', function(evt) {
        var $elt = jQuery(this);
        var annotationId = $elt.data('annotation-id');
        var assetId = $elt.data('asset-id');
        var editable = $elt.data('editable');
        var url = MediaThread.urls['annotation-copy'](assetId, annotationId);

        if (annotationId && editable) {
            self.signalInsert(assetId, annotationId);
            self.hideCollection();
            return;
        }

        if (annotationId) {
            // copy the annotation for the user to ensure they can
            // edit the annotation's start & end times if neeed.
            jQuery.ajax({
                type: 'POST',
                url: urlWithCourse(url),
                dataType: 'json',
                error: function() {
                    showMessage('There was an error adding your item');
                },
                success: function(json, textStatus, xhr) {
                    self.signalInsert(assetId, json.annotation.id);
                    self.hideCollection();
                }
            });
            return;
        }

        // No annotation id
        // get or create the user's global annotation
        // return the global annotation instead of the item
        jQuery.ajax({
            type: 'POST',
            url: MediaThread.urls['annotation-create-global'](assetId),
            dataType: 'json',
            error: function() {
                showMessage('There was an error adding your item');
            },
            success: function(json, textStatus, xhr) {
                self.signalInsert(assetId, json.annotation.id);
                self.hideCollection();
            }
        });
    });
};

CollectionWidget.prototype.open = function(displayMode, params) {
    // disable requested filters
    this.disable = params && params.disable || [];

    // filter by requested filters
    this.currentRecords.active_filters = params;
    this.filter();

    // store some callback information
    this.caller = params && params.caller;

    // show the full collection or an edit view
    this.displayMode = displayMode;

    if (params && params.allowAssets) {
        this.$modal.addClass('show-assets');
    } else {
        this.$modal.removeClass('show-assets');
    }

    this.showCollection();
};

CollectionWidget.prototype.showCollection = function() {
    if (this.$modal.hasClass('modal')) {
        this.$modal.modal('show');
    } else {
        this.$modal.show();
    }
};

CollectionWidget.prototype.hideCollection = function() {
    if (this.$modal.hasClass('modal')) {
        this.$modal.modal('hide');
    } else {
        this.$modal.hide();
    }
};

CollectionWidget.prototype.onCancel = function() {
    if (this.displayMode !== 'gallery') {
        this.hideCollection();
    } else {
        this.$quickEditView.fadeOut();
        this.$el.fadeIn();
    }
};

CollectionWidget.prototype.onSave = function(evt, params) {
    this.refresh();

    if (this.displayMode === 'gallery') {
        this.$quickEditView.fadeOut();
        this.$el.fadeIn();
    } else {
        this.hideCollection();

        var ctx = {'detail': params};
        ctx.detail.caller = this.caller;
        document.dispatchEvent(new CustomEvent('asset.save', ctx));

    }
};

CollectionWidget.prototype.filter = function() {
    this.setLoading(true);

    this.$el.find('select.course-tags, select.vocabulary')
        .select2('enable', false);

    var self = this;
    djangosherd.storage.get({
        type: 'asset',
        url: self.filteredUrl()
    },
    false,
    function(the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

CollectionWidget.prototype.refresh = function(offset, updating) {
    this.setLoading(true);
    this.limits.offset = offset || 0;

    var self = this;
    djangosherd.storage.get({
        type: 'asset',
        url: this.filteredUrl(updating || false)
    },
    false,
    function(the_records) {
        self.updateAssets(the_records);
    });
};

CollectionWidget.prototype.createThumbs = function(assets) {
    djangosherd.thumbs = [];
    for (var i = 0; i < assets.length; i++) {
        var asset = assets[i];
        djangosherd_adaptAsset(asset); //in-place
        if (asset.thumbable && asset.annotations.length > 0) {
            for (var j = 0; j < asset.annotations.length; j++) {
                var ann = asset.annotations[j];

                let view = null;
                switch (asset.type) {
                case 'image':
                    view = new Sherd.Image.OpenLayers();
                    break;
                case 'fsiviewer':
                    view = new Sherd.Image.FSIViewer();
                    break;
                case 'pdf':
                    view = new Sherd.Pdf.PdfJS();
                    break;
                default:
                    console.error(
                        'collectionwidget error: unrecognized asset type: ' +
                            asset.type) ;
                }
                djangosherd.thumbs.push(view);
                var objDiv = document.createElement('div');
                objDiv.setAttribute('class', 'annotation-thumb');

                var t = this.$el.find('.annotation-thumb-' + ann.id);
                if (t.length > 0) {
                    t[0].appendChild(objDiv);
                } else {
                    // eslint-disable-next-line no-console
                    console.error('CollectionWidget error!');
                }

                // should probably be in .view
                asset.presentation = 'thumb';

                ann.asset = asset;
                view.html.push(objDiv, ann);
                view.setState(ann.annotation);
            }
        }
    }
};

CollectionWidget.prototype.updateSwitcher = function() {
    this.switcher_context.display_switcher_extras =
        !this.switcher_context.showing_my_items;

    var context =
        jQuery.extend({}, this.switcher_context, MediaThread.mustacheHelpers);

    var self = this;
    MediaThread.loadTemplate('collection_chooser')
        .then(function(template) {
            var rendered = Mustache.render(template, context);
            jQuery(self.$el)
                .find('.collection-chooser-container')
                .html(rendered);
            // hook up switcher choice owner behavior
            self.$el.find('a.switcher-choice.owner')
                .off('click').on('click', function(evt) {
                    var srcElement = evt.srcElement ||
                        evt.target ||
                        evt.originalTarget;
                    var bits = srcElement.href.split('/');
                    var username = bits[bits.length - 1];

                    if (username === 'all-class-members') {
                        self.currentRecords.space_owner = null;
                    } else {
                        self.currentRecords.space_owner = {'username': {}};
                        self.currentRecords.space_owner.username.id = '';
                        self.currentRecords.space_owner.username.public_name =
                            '';
                        self.currentRecords.space_owner.username = username;
                    }
                    return self.filter();
                });

            self.$el.find('select.course-tags')
                .select2({
                    placeholder: 'Select tag',
                    width: '72%'
                });
            if ('tag' in self.currentRecords.active_filters &&
                self.currentRecords.active_filters.tag.length > 0) {
                self.$el.find('select.course-tags').select2(
                    'val',
                    self.currentRecords.active_filters.tag.split(','));
            }

            var vocabulary = self.$el.find('select.vocabulary')[0];
            jQuery(vocabulary).select2({
                width: '76%'
            });

            var values = [];
            for (var key in self.currentRecords.active_filters) {
                if (Object.prototype.hasOwnProperty.call(
                    self.currentRecords.active_filters, key) &&
                    self.currentRecords.active_filters[key].length > 0) {
                    if (self.currentRecords.active_filters[key].split) {
                        var val = self.currentRecords.active_filters[key]
                            .split(',');
                        self.currentRecords.active_filters[key] = val;
                        values = values.concat(val);
                    }
                }
            }
            jQuery(vocabulary).select2('val', values);

            jQuery(window).trigger('resize');
        });
};

CollectionWidget.prototype.getAssets = function() {
    return this.$el.find('.asset-table').get(0);
};

CollectionWidget.prototype.updateAssets = function(the_records) {
    this.switcher_context.owners = this.owners;
    this.switcher_context.space_viewer = the_records.space_viewer;
    this.switcher_context.selected_view = this.selected_view;

    if (!Object.prototype.hasOwnProperty.call(
        the_records, 'space_owner') ||
            the_records.space_owner === null) {
        this.switcher_context.selected_label = 'All Class Members';
        this.switcher_context.showing_all_items = true;
        this.switcher_context.showing_my_items = false;
        the_records.showing_all_items = true;
    } else if (the_records.space_owner.username ===
               the_records.space_viewer.username) {
        this.switcher_context.selected_label = 'Me';
        this.switcher_context.showing_my_items = true;
        this.switcher_context.showing_all_items = false;
        the_records.showing_my_items = true;
    } else {
        this.switcher_context.showing_my_items = false;
        this.switcher_context.showing_all_items = false;
        this.switcher_context.selected_label =
            the_records.space_owner.public_name;
    }

    this.currentRecords = the_records;

    var n = _propertyCount(the_records.active_filters);
    if (n > 0) {
        the_records.active_filter_count = n;
    }

    if (this.disable) {
        for (var i = 0; i < this.disable.length; i++) {
            this.currentRecords['disable_' + this.disable[i]] = true;
        }
    }

    var self = this;
    var $elt = jQuery(this.$el).find('.asset-table');
    $elt.hide();
    jQuery.when.apply(
        this,
        MediaThread.loadTemplates([
            self.template,
            self.template + '_assets'
        ])
    ).then(function() {
        var renderedMain = Mustache.render(
            MediaThread.templates[self.template],
            jQuery.extend({}, the_records, MediaThread.mustacheHelpers)
        );
        self.$el.html(renderedMain);

        var rendered = Mustache.render(
            MediaThread.templates[self.template + '_assets'],
            jQuery.extend({}, the_records, MediaThread.mustacheHelpers)
        );
        $elt = jQuery(self.$el).find('.asset-table');
        $elt.html(rendered);
        self.updateAssetsPost($elt, the_records);
    });
};

CollectionWidget.prototype.updateAssetsPost = function($elt, the_records) {
    this.createThumbs(the_records.assets);
    this.updateSwitcher();

    jQuery('.filter-widget').show();

    $elt.fadeIn('slow');

    jQuery(window).trigger('resize');
    this.setLoading(false);
    jQuery(window).trigger('collection.ready');
};

CollectionWidget.prototype.initCitationView = function() {
    if (!Object.prototype.hasOwnProperty.call(this, 'citationView')) {
        // Setup the media display window.
        this.citationView = new CitationView();
        this.citationView.init({
            'default_target': 'asset-workspace-videoclipbox2',
            'presentation': 'small',
            'clipform': true,
            'autoplay': false,
            'pdf_iframe': true,
            'winHeight': function() {
                return 250;
            }
        });
    }
};

CollectionWidget.prototype.quickEdit = function(
    title, evtType, assetId, annotationId
) {
    this.initCitationView();

    this.$quickEditView.find('.asset-view-title').html(title);
    this.$el.fadeOut();
    this.$quickEditView.fadeIn();

    // Setup the edit view
    var self = this;
    window.annotationList.init({
        'parent': this.$modal.find('.collection-body'),
        'asset_id': assetId,
        'annotation_id': annotationId,
        'edit_state': evtType,
        'update_history': false,
        'vocabulary': self.vocabulary,
        'view_callback': function() {
            self.citationView.openCitationById(null, assetId, annotationId);
        }
    });
};

CollectionWidget.prototype.deleteAsset = function(assetId) {
    var url = MediaThread.urls['asset-delete'](assetId);
    return ajaxDelete(null, 'record-' + assetId, {
        'href': url,
        'item': true,
        'success': function() {
            jQuery(window).trigger('asset.on_delete');
        }
    });
};

CollectionWidget.prototype.deleteAnnotation = function(annotationId) {
    var assetId = jQuery('#annotation-' + annotationId)
        .parents('div.record').children('input.record')
        .attr('value');
    var url = MediaThread.urls['annotation-delete'](assetId, annotationId);
    return ajaxDelete(null, 'annotation-' + annotationId, {
        'href': url,
        'success': function() {
            jQuery(window).trigger('annotation.on_delete');
        }
    });
};

/** Getters & Setters **/

CollectionWidget.prototype.getCourse = function() {
    return jQuery.ajax({
        type: 'GET',
        url: '/api/course/?course=' + MediaThread.current_course,
        dataType: 'json'
    });
};

CollectionWidget.prototype.getVocabulary = function() {
    return jQuery.ajax({
        type: 'GET',
        url: '/api/vocabulary/?course=' + MediaThread.current_course,
        dataType: 'json'
    });
};

CollectionWidget.prototype.baseUrl = function() {
    var owner = this.selectedOwner();

    if (owner) {
        return MediaThread.urls['your-space'](
            owner.username, null, null, true);
    } else {
        return MediaThread.urls['all-space'](
            null, null, true);
    }
};

CollectionWidget.prototype.isValidFilter = function(filter) {
    var filters = [
        'tag', 'modified', 'search_text',
        'media_type', 'primary_type'
    ];
    return filters.indexOf(filter) > -1 || filter.startsWith('vocabulary-');
};

CollectionWidget.prototype.filteredUrl = function(updating) {
    var url = this.baseUrl();

    // tack on all the filters
    if (Object.prototype.hasOwnProperty.call(
        this.currentRecords, 'active_filters')) {
        for (var filter in this.currentRecords.active_filters) {
            if (Object.prototype.hasOwnProperty.call(
                this.currentRecords.active_filters, filter) &&
                    this.isValidFilter(filter)) {
                var val = this.currentRecords.active_filters[filter];
                if (val) {
                    url += '&' + filter + '=' + escape(val.toString());
                }
            }
        }
    }

    if (updating) {
        var urlParams = {
            offset: this.limits.offset,
            limit: this.limits.limit
        };

        url += '&' + jQuery.param(urlParams);
    }

    url = urlWithCourse(url, MediaThread.current_course);

    return url;
};

CollectionWidget.prototype.selectedOwner = function() {
    return this.currentRecords.space_owner;
};

CollectionWidget.prototype.activeTags = function() {
    return ('tag' in this.currentRecords.active_filters) ?
        this.currentRecords.active_filters.tag : null;
};

CollectionWidget.prototype.activeModified = function() {
    return ('modified' in this.currentRecords.active_filters) ?
        this.currentRecords.active_filters.modified : null;
};

CollectionWidget.prototype.getLoading = function() {
    return this.loading;
};

CollectionWidget.prototype.setLoading = function(isLoading) {
    this.loading = isLoading;
    if (this.loading) {
        jQuery('.ajaxloader').show();
    } else {
        jQuery('.ajaxloader').hide();
    }
};

CollectionWidget.prototype.signalInsert = function(assetId, annotationId) {
    var ctx = {'detail': {
        'assetId': assetId,
        'annotationId': annotationId,
        'caller': this.caller
    }};
    document.dispatchEvent(new CustomEvent('asset.select', ctx));
};

jQuery(document).ready(function() {
    if (typeof djangosherd !== 'undefined' && MediaThread.current_user) {
        MediaThread.collection = new CollectionWidget();
    }
});
