/* global _propertyCount: true, ajaxDelete: true, djangosherd: true */
/* global djangosherd_adaptAsset: true, MediaThread: true */
/* global Mustache: true, Sherd: true, urlWithCourse */
/* global pdfjsLib: true */
// jscs:disable requireCamelCaseOrUpperCaseIdentifiers

/**
 * Listens For:
 * asset.on_delete > refresh
 * annotation.on_create > refresh
 * annotation.on_save > refresh
 * annotation.on_delete > refresh
 *
 * Signals:
 * asset.edit > when edit in place is clicked
 * asset.on_delete > after ajaxDelete is called
 * annotation.create > when create selection is clicked
 * annotation.edit > when edit in place is clicked
 */

import {renderPage} from '../../pdf/utils.js';

var CollectionList = function(config) {
    var self = this;
    self.config = config;
    self.template_label = config.template_label;
    self.view_callback = config.view_callback;
    self.create_annotation_thumbs = config.create_annotation_thumbs;
    self.create_asset_thumbs = config.create_asset_thumbs;
    self.$parent = config.$parent;
    self.selected_view =
        Object.prototype.hasOwnProperty.call(config, 'selectedView') ?
            config.selectedView : 'Medium';
    self.citable =
        Object.prototype.hasOwnProperty.call(config, 'citable') ?
            config.citable : false;
    self.owners = config.owners;
    self.limits = {offset: 0, limit: 20};
    self.loading = false;
    self.current_asset = config.current_asset;

    self.$el = self.$parent.find('div.' + self.template_label);

    self.switcher_context = jQuery.extend({}, MediaThread.mustacheHelpers);

    jQuery(window).on('asset.on_delete', {'self': self}, function(event) {
        var self = event.data.self;
        var $div = self.$el.find('div.collection-assets');
        if (!self.citable && $div.length > 0) {
            event.data.self.refresh();
        }
    });
    jQuery(window).on('annotation.on_create', {'self': self},
        function(event, params) {
            var self = event.data.self;
            self.current_annotation = params.annotationId;

            const page = self.current_records.paginator.currentPage;
            const offset = (page - 1) * self.limits.limit;
            self.refresh(null, offset, true);
        }
    );
    jQuery(window).on('annotation.on_delete', {'self': self}, function(event) {
        var self = event.data.self;
        if (!self.citable) {
            event.data.self.refresh();
        }
    });
    jQuery(window).on('annotation.on_save', {'self': self},
        function(event, params) {
            var self = event.data.self;
            self.current_annotation = params.annotationId;

            const page = self.current_records.paginator.currentPage;
            const offset = (page - 1) * self.limits.limit;
            self.refresh(null, offset, true);
        }
    );

    MediaThread.loadTemplate(config.template)
        .done(function() {
            var renderedCollection =
                Mustache.render(
                    MediaThread.templates[config.template],
                    MediaThread.mustacheHelpers);
            self.$el.html(renderedCollection);

            self.refresh(config);
        });

    self.$el.on('click', '.filter-widget h3', function(evt) {
        jQuery(evt.currentTarget).parent().toggleClass('collapsed');
    });

    self.$el.on('blur', 'input[name="search-text"]', function(evt) {
        self.current_records.active_filters.search_text =
            self.$el.find('input[name="search-text"]').val();
    });

    self.$el.on('keyup', 'input[name="search-text"]', function(evt) {
        if (evt.keyCode === 13) {
            evt.preventDefault();
            self.current_records.active_filters.search_text =
                self.$el.find('input[name="search-text"]').val();
            return self.filter();
        }
    });
    self.$el.on('click', '.btn-search-text', function(evt) {
        self.current_records.active_filters.search_text =
            self.$el.find('input[name="search-text"]').val();
        return self.filter();
    });

    self.$el.on(
        'click', 'a.switcher-choice.filterbydate', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.href.split('/');
            var filterName = bits[bits.length - 1];

            if (filterName === 'all') {
                self.current_records.active_filters.modified = '';
            } else {
                self.current_records.active_filters.modified = filterName;
            }
            return self.filter();
        });

    self.$el.on(
        'change', 'select.vocabulary', function(evt) {
            var option = evt.added || evt.removed;
            var vocab = jQuery(option.element).parent().attr('data-id');
            if (!Object.prototype.hasOwnProperty.call(
                self.current_records.active_filters, vocab)) {
                self.current_records.active_filters[vocab] = [];
            }

            if (evt.added) {
                self.current_records.active_filters[vocab].push(option.id);
            } else if (evt.removed) {
                var index = self.current_records.active_filters[vocab]
                    .indexOf(option.id);
                self.current_records.active_filters[vocab].splice(index, 1);
            }
            return self.filter();
        });

    self.$el.on(
        'change', 'select.course-tags', function() {
            var $elt = self.$el.find('select.course-tags');
            self.current_records.active_filters.tag = $elt.val();
            return self.filter();
        });

    self.$parent.on(
        'click', 'a.switcher-choice.filterbytag', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.href.split('/');
            return self.filterByTag(bits[bits.length - 1]);
        });

    self.$el.on(
        'click', 'a.collection-choice.edit-asset', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.parentNode.href.split('/');
            var asset_id = bits[bits.length - 1];
            jQuery(window).trigger('asset.edit', [asset_id]);
            return false;
        });

    self.$el.on(
        'click', 'a.collection-choice.delete-asset', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.parentNode.href.split('/');
            var asset_id = bits[bits.length - 1];
            self.deleteAsset(asset_id);
            return false;
        });

    self.$el.on(
        'click', 'a.collection-choice.delete-annotation', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.parentNode.href.split('/');
            return self.deleteAnnotation(bits[bits.length - 1]);
        });

    self.$el.on(
        'click', 'a.collection-choice.create-annotation', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var bits = src.href.split('/');
            var asset_id = bits[bits.length - 1];
            jQuery(window).trigger('annotation.create',
                [evt.currentTarget, asset_id]);
            return false;
        });

    self.$el.on(
        'click', '.collection-choice.edit-annotation', function(evt) {
            var src = evt.srcElement || evt.target || evt.originalTarget;
            var annotation_id = jQuery(src).data('id');
            var asset_id = jQuery('#annotation-' + annotation_id)
                .parents('div.record')
                .children('input.record').attr('value');
            jQuery(window).trigger('annotation.edit',
                [evt.currentTarget, asset_id, annotation_id]);
            return false;
        });

    var q = '#collection-overlay, #collection-help, #collection-help-tab';
    self.$parent.on('click', '#collection-help-button', function() {
        jQuery(q).show();
        return false;
    });

    self.$parent.on('click', '.dismiss-help', function() {
        jQuery(q).hide();
        return false;
    });

    self.$el.on('click', 'a.page-link', function(evt) {
        const page = jQuery(evt.target).data('page-number');
        const offset = (page - 1) * self.limits.limit;
        self.refresh(null, offset, true);
        return false;
    });
};

CollectionList.prototype.getLoading = function() {
    return this.loading;
};

CollectionList.prototype.setLoading = function(isLoading) {
    this.loading = isLoading;
    if (this.loading) {
        jQuery('.ajaxloader').show();
    } else {
        jQuery('.ajaxloader').hide();
    }
};

CollectionList.prototype.constructUrl = function(config, updating) {
    var url;

    if (config && config.$parent) {
        // Retrieve the full asset w/annotations from storage
        if (config.view === 'all' || !config.space_owner) {
            url = MediaThread.urls['all-space'](
                config.tag, null, this.citable);
        } else {
            url = MediaThread.urls['your-space'](
                config.space_owner, config.tag, null, this.citable);
        }
    } else {
        url = this.getSpaceUrl();

        for (var filter in this.current_records.active_filters) {
            if (Object.prototype.hasOwnProperty.call(
                this.current_records.active_filters, filter)) {
                var val = this.current_records.active_filters[filter];
                if (val !== null && val.length > 0) {
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

CollectionList.prototype.refresh = function(config, offset, updating) {
    var self = this;
    self.setLoading(true);
    self.limits.offset = offset || 0;
    var url = self.constructUrl(config, updating || false);

    djangosherd.storage.get(
        {
            type: 'asset',
            url: url
        },
        false,
        function(the_records) {
            self.updateAssets(the_records);
        });
};

CollectionList.prototype.appendItems = function(config) {
    var self = this;
    self.loading = true;
    self.limits.offset += self.limits.limit;

    var url = self.constructUrl(config, true);

    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function(the_records) {
        self.appendAssets(the_records);
        self.loading = false;

        if (self.current_annotation) {
            let $elt = jQuery('#selectionCollapse-' + self.current_annotation);
            $elt.collapse({toggle: true});

            $elt = jQuery('#annotation-' + self.current_annotation);
            jQuery('html, body').animate(
                {scrollTop: $elt.offset().top - 50}, 100);
            delete self.current_annotation;
        }
    });
};

CollectionList.prototype.editAsset = function(asset_id) {
};

CollectionList.prototype.deleteAsset = function(asset_id) {
    var url = MediaThread.urls['asset-delete'](asset_id);
    return ajaxDelete(null, 'record-' + asset_id, {
        'href': url,
        'item': true,
        'success': function() {
            jQuery(window).trigger('asset.on_delete', [asset_id]);
        }
    });
};

CollectionList.prototype.deleteAnnotation = function(annotation_id) {
    var asset_id = jQuery('#annotation-' + annotation_id)
        .parents('div.record').children('input.record')
        .attr('value');
    var url = MediaThread.urls['annotation-delete'](asset_id, annotation_id);
    return ajaxDelete(null, 'annotation-' + annotation_id, {'href': url});
};

// Linkable tags within the Project-level composition view
CollectionList.prototype.filterByTag = function(tag) {
    var self = this;
    self.setLoading(true);
    var active_modified = ('modified' in self.current_records.active_filters) ?
        self.current_records.active_filters.modified : null;
    djangosherd.storage.get({
        type: 'asset',
        url: self.getSpaceUrl(tag, active_modified, self.citable)
    },
    false,
    function(the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

// Linkable tags within the Item View/References page
CollectionList.prototype.filterByClassTag = function(tag) {
    var self = this;
    self.setLoading(true);
    djangosherd.storage.get({
        type: 'asset',
        url: MediaThread.urls['all-space'](tag, null, self.citable)
    },
    false,
    function(the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

//Linkable vocabulary within the Item View/References page
CollectionList.prototype.filterByVocabulary = function(srcElement) {
    var self = this;
    self.setLoading(true);
    var url = MediaThread.urls['all-space'](null, null, self.citable);
    var $srcElement = jQuery(srcElement);
    url += $srcElement.data('vocabulary-id') + '=' +
        $srcElement.data('term-id');
    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function(the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

CollectionList.prototype.filter = function() {
    var self = this;
    self.setLoading(true);

    self.$el.find('select.course-tags, select.vocabulary')
        .select2('enable', false);

    var url = self.getSpaceUrl();

    for (var filter in self.current_records.active_filters) {
        if (Object.prototype.hasOwnProperty.call(
            self.current_records.active_filters, filter)) {
            var val = self.current_records.active_filters[filter];
            if (val !== null && val.length > 0) {
                url += '&' + filter + '=' + escape(val.toString());
            }
        }
    }
    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function(the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

CollectionList.prototype.getShowingAllItems = function(json) {
    return !Object.prototype.hasOwnProperty.call(json, 'space_owner') ||
        json.space_owner === null;
};

CollectionList.prototype.getSpaceUrl = function(active_tag, active_modified) {
    var self = this;
    if (self.getShowingAllItems(self.current_records)) {
        return MediaThread.urls['all-space'](
            active_tag, active_modified, self.citable);
    } else {
        return MediaThread.urls['your-space'](
            self.current_records.space_owner.username,
            active_tag, active_modified, self.citable);
    }
};

CollectionList.prototype.createAssetThumbs = function(assets) {
    var self = this;
    djangosherd.thumbs = [];
    var isThumb = function(s) {
        return s.label === 'thumb';
    };
    for (var i = 0; i < assets.length; i++) {
        var asset = assets[i];
        djangosherd_adaptAsset(asset); //in-place

        var $targetParent = self.$el.find('.gallery-item-' + asset.id);

        if (!asset.thumbable) {
            if ($targetParent.hasClass('static-height')) {
                var thumbs = jQuery.grep(asset.sources, isThumb);
                if (thumbs.length && thumbs[0].height > 240) {
                    $targetParent.css({
                        height: (thumbs[0].height + 50) + 'px'
                    });
                } else {
                    $targetParent.css({height: '222px'});
                }
            }
        } else {
            var view;
            switch (asset.type) {
            case 'image':
                view = new Sherd.Image.OpenLayers();
                break;
            case 'fsiviewer':
                view = new Sherd.Image.FSIViewer();
                break;
            }
            djangosherd.thumbs.push(view);

            // scale the height
            var width = $targetParent.width();
            var height = (width / asset.width * asset.height + 85) + 'px';
            if ($targetParent.hasClass('static-height')) {
                $targetParent.css({height: height});
            }

            var objDiv = document.createElement('div');
            $targetParent.find('.asset-thumb').append(objDiv);

            asset.presentation = 'gallery';
            asset.x = 0;
            asset.y = 0;
            asset.zoom = 1;

            /* eslint-disable no-empty */
            try {
                view.html.push(objDiv, {asset: asset});
                view.setState(asset);
            } catch (e) {
                console.error(e);
            }
            /* eslint-enable no-empty */
        }
    }
};

CollectionList.prototype.createThumbs = function(assets) {
    var self = this;
    djangosherd.thumbs = [];
    for (var i = 0; i < assets.length; i++) {
        var asset = assets[i];
        djangosherd_adaptAsset(asset); //in-place
        if (asset.thumbable && asset.annotations.length > 0) {
            for (var j = 0; j < asset.annotations.length; j++) {
                try {
                    var annotation = asset.annotations[j];

                    var view;
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
                    }
                    djangosherd.thumbs.push(view);
                    var objDiv = document.createElement('div');
                    objDiv.setAttribute('class', 'annotation-thumb');

                    var t = self.$el.find(
                        '.annotation-thumb-' + annotation.id);
                    if (t.length > 0) {
                        t[0].appendChild(objDiv);
                    } else {
                        // eslint-disable-next-line no-console
                        console.error('CollectionList error!');
                    }

                    // should probably be in .view
                    asset.presentation = 'thumb';

                    annotation.asset = asset;
                    view.html.push(objDiv, annotation);
                    view.setState(annotation.annotation);
                } catch (err) {
                    console.error(err);
                }
            }
        }
    }
};

CollectionList.prototype.updateSwitcher = function() {
    var self = this;
    self.switcher_context.display_switcher_extras =
        !self.switcher_context.showing_my_items;

    var context =
        jQuery.extend({}, self.switcher_context, MediaThread.mustacheHelpers);

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
                        self.current_records.space_owner = null;
                    } else {
                        self.current_records.space_owner = {'username': {}};
                        self.current_records.space_owner.username.id = '';
                        self.current_records.space_owner.username.public_name =
                            '';
                        self.current_records.space_owner.username = username;
                    }
                    return self.filter();
                });

            self.$el.find('select.course-tags')
                .select2({
                    placeholder: 'Select tag'
                });
            if ('tag' in self.current_records.active_filters &&
                self.current_records.active_filters.tag.length > 0) {
                self.$el.find('select.course-tags').select2(
                    'val',
                    self.current_records.active_filters.tag.split(','));
            }

            var vocabulary = self.$el.find('select.vocabulary')[0];
            jQuery(vocabulary).select2({
                placeholder: 'Select terms'
            });

            var values = [];
            for (var key in self.current_records.active_filters) {
                if (Object.prototype.hasOwnProperty.call(
                    self.current_records.active_filters, key) &&
                    self.current_records.active_filters[key].length > 0) {
                    var val = self.current_records.active_filters[key]
                        .split(',');
                    self.current_records.active_filters[key] = val;
                    values = values.concat(val);
                }
            }
            jQuery(vocabulary).select2('val', values);
        });
};

CollectionList.prototype.getAssets = function() {
    var self = this;
    return self.$el.find('.asset-table').get(0);
};

CollectionList.prototype.updateAssets = function(the_records) {
    var self = this;
    self.switcher_context.owners = self.owners;
    self.switcher_context.space_viewer = the_records.space_viewer;
    self.switcher_context.selected_view = self.selected_view;

    if (self.getShowingAllItems(the_records)) {
        self.switcher_context.selected_label = 'All Class Members';
        self.switcher_context.showing_all_items = true;
        self.switcher_context.showing_my_items = false;
        the_records.showing_all_items = true;
    } else if (the_records.space_owner.username ===
               the_records.space_viewer.username) {
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

    var $elt = jQuery(self.$el).find('.asset-table');
    $elt.hide();
    jQuery.when.apply(
        this,
        MediaThread.loadTemplates([
            self.config.template,
            self.config.template + '_assets'
        ])
    ).then(function() {
        var renderedMain = Mustache.render(
            MediaThread.templates[self.config.template],
            jQuery.extend({}, the_records, MediaThread.mustacheHelpers)
        );
        self.$el.html(renderedMain);

        var rendered = Mustache.render(
            MediaThread.templates[self.config.template + '_assets'],
            jQuery.extend({}, the_records, MediaThread.mustacheHelpers)
        );
        $elt = jQuery(self.$el).find('.asset-table');
        $elt.html(rendered);
        self.assetPostUpdate($elt, the_records);
    });
};

CollectionList.prototype.assetPostUpdate = function($elt, the_records) {
    // Initialize PDF views
    the_records.assets.forEach(function(asset) {
        if (asset.primary_type === 'pdf' && asset.pdf) {
            // Get pdf DOM container
            const containerEl = document.getElementById(
                'pdf-container-' + asset.id);
            if (!containerEl) {
                return;
            }

            const canvasEl = containerEl.querySelector('canvas');

            // https://mozilla.github.io/pdf.js/examples/
            const loadingTask = pdfjsLib.getDocument(asset.pdf);
            loadingTask.promise.then(function(pdf) {
                pdf.getPage(1).then(function(page) {
                    renderPage(page, canvasEl, 192);
                });
            });
        }
    });

    var self = this;

    if (self.create_annotation_thumbs) {
        self.createThumbs(the_records.assets);
    } else if (self.create_asset_thumbs) {
        self.createAssetThumbs(the_records.assets);
    }

    self.updateSwitcher();

    self.appendItems(self.current_records);

    jQuery('.filter-widget').show();

    $elt.fadeIn('slow');

    if (self.view_callback) {
        self.view_callback(the_records.assets.length);
    }

    self.setLoading(false);
};

CollectionList.prototype.appendAssets = function(the_records) {
    var self = this;
    if (the_records.assets.length > 0) {
        var html = jQuery(Mustache.render(
            MediaThread.templates[self.config.template + '_assets'],
            jQuery.extend({}, the_records, MediaThread.mustacheHelpers)
        ));
        var $container = self.$el.find('div.asset-table');
        $container.append(html);

        if (self.create_annotation_thumbs) {
            self.createThumbs(the_records.assets);
        } else if (self.create_asset_thumbs) {
            self.createAssetThumbs(the_records.assets);
        }

        jQuery(window).trigger('assets.refresh', [html]);
    }
};

// TODO: Remove the window export when fully converted to ES modules.
window.CollectionList = CollectionList;

export {CollectionList};
