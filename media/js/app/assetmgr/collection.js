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

var CollectionList = function (config) {
    var self = this;
    self.template_label = config.template_label;    
    self.view_callback = config.view_callback;
    self.create_annotation_thumbs = config.create_annotation_thumbs;
    self.create_asset_thumbs = config.create_asset_thumbs;
    self.parent = config.parent;
    self.selected_view = config.hasOwnProperty('selectedView') ? config.selectedView : 'Medium';
    self.citable = config.hasOwnProperty('citable') ? config.citable : false;
    self.owners = config.owners;    
    self.limits = {offset: 0, limit: 20};
    self.loading = false;
    self.current_asset = config.current_asset;
    
    self.el = jQuery(self.parent).find("div." + self.template_label)[0];
    
    // setup some ajax progress indicator
    jQuery(self.el).bind("ajaxStart", function(){
        if (!self.loading) {
            jQuery("div.ajaxloader").show();
        }
     }).bind("ajaxStop", function(){  
        jQuery("div.ajaxloader").hide();
     });
    
    self.switcher_context = {};
    
    jQuery(window).bind('asset.on_delete', { 'self': self }, function (event) {
        var self = event.data.self;
        var div = jQuery(self.el).find("div.collection-assets");
        if (!self.citable && div.length > 0) {
            self.scrollTop = jQuery(div[0]).scrollTop();
            event.data.self.refresh();
        }
    });
    jQuery(window).bind('annotation.on_create', { 'self': self }, function (event) {
        var self = event.data.self;
        self.scrollTop = jQuery(self.el).find("div.collection-assets").scrollTop();
        event.data.self.refresh();
    });
    jQuery(window).bind('annotation.on_delete', { 'self': self }, function (event) {
        var self = event.data.self;
        if (!self.citable) {
            self.scrollTop = jQuery(self.el).find("div.collection-assets").scrollTop();
            event.data.self.refresh();
        }
    });
    jQuery(window).bind('annotation.on_save', { 'self': self }, function (event) {
        var self = event.data.self;
        self.scrollTop = jQuery(self.el).find("div.collection-assets").scrollTop();
        event.data.self.refresh();
    });
    
    jQuery.ajax({
        url: '/media/templates/' + config.template + '.mustache?nocache=v2',
        dataType: 'text',
        cache: false, // Chrome && Internet Explorer has aggressive caching policies.
        success: function (text) {
            MediaThread.templates[config.template] = Mustache.template(config.template, text);
            
            var url = null;
            
            self.refresh(config);
        }
    });
    
    return this;
};

CollectionList.prototype.constructUrl = function(config, updating) {
    var self = this;
    var url;
    
    if (config && config.parent) {
        // Retrieve the full asset w/annotations from storage
        if (config.view === 'all' || !config.space_owner) {
            url = MediaThread.urls['all-space'](config.tag, null, self.citable);
        } else {
            url = MediaThread.urls['your-space'](config.space_owner, config.tag, null, self.citable);
        }
    } else {
        var active_modified = ('modified' in self.current_records.active_filters) ? self.current_records.active_filters.modified : null;
        var active_tag = ('tag' in self.current_records.active_filters) ? self.current_records.active_filters.tag : null;
        
        url = self.getSpaceUrl(active_tag, active_modified);
    }
    
    if (updating) {
        url += "&offset=" + self.limits.offset + "&limit=" + self.limits.limit;
    }
    return url;
};

CollectionList.prototype.refresh = function (config) {
    var self = this;
    self.limits.offset = 0;
    var url = self.constructUrl(config, false);

    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function (the_records) {
        self.updateAssets(the_records);
    });
};

CollectionList.prototype.appendItems = function (config) {
    var self = this;
    self.limits.offset += self.limits.limit;

    var url = self.constructUrl(config, true);

    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function (the_records) {
        self.appendAssets(the_records);
        self.loading = false;
    });
};

CollectionList.prototype.editAsset = function (asset_id) {
    var self = this;
};

CollectionList.prototype.deleteAsset = function (asset_id) {
    var self = this;
    var url = MediaThread.urls['asset-delete'](asset_id);
    return ajaxDelete(null, 'record-' + asset_id, {
        'href': url,
        'item': true,
        'success': function () {
            try {
                jQuery(window).trigger("asset.on_delete", [ asset_id ]);
            } catch (e) {}
        }
    });
};

CollectionList.prototype.deleteAnnotation = function (annotation_id) {
    var self = this;
    var asset_id = jQuery('#annotation-' + annotation_id).parents("div.record").children("input.record").attr("value");
    var url = MediaThread.urls['annotation-delete'](asset_id, annotation_id);
    return ajaxDelete(null, 'annotation-' + annotation_id, { 'href': url });
};

// Linkable tags within the Project-level composition view
CollectionList.prototype.filterByTag = function (tag) {
    var self = this;
    var active_modified = ('modified' in self.current_records.active_filters) ? 
            self.current_records.active_filters.modified
            : null;
    djangosherd.storage.get({
        type: 'asset',
        url: self.getSpaceUrl(tag, active_modified, self.citable)
    },
    false,
    function (the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

// Linkable tags within the Item View/References page
CollectionList.prototype.filterByClassTag = function (tag) {
    var self = this;
    djangosherd.storage.get({
        type: 'asset',
        url: MediaThread.urls['all-space'](tag, null, self.citable)
    },
    false,
    function (the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

//Linkable vocabulary within the Item View/References page
CollectionList.prototype.filterByVocabulary = function (srcElement) {
    var self = this;
    var url = MediaThread.urls['all-space'](null, null, self.citable);
    url += jQuery(srcElement).data("vocabulary-id") + "=" + 
        jQuery(srcElement).data("term-id");
    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function (the_records) {
        self.updateAssets(the_records);
    });

    return false;
};

CollectionList.prototype.filter = function () {
    var self = this;
    var filters = {};
    
    jQuery(self.el).find("select.course-tags, select.vocabulary")
        .select2("enable", false);    

    var url = self.getSpaceUrl();
    
    for (var filter in self.current_records.active_filters) {
        if (self.current_records.active_filters.hasOwnProperty(filter)) {
            var val = self.current_records.active_filters[filter];
            if (val !== null && val.length > 0) {
                url += "&" + filter + "=" + val.toString();
            }
        }
    }
    djangosherd.storage.get({
        type: 'asset',
        url: url
    },
    false,
    function (the_records) {
        self.updateAssets(the_records);
    });
    
    return false;
};

CollectionList.prototype.getShowingAllItems = function (json) {
    return !json.hasOwnProperty('space_owner') || json.space_owner === null;
};

CollectionList.prototype.getSpaceUrl = function (active_tag, active_modified) {
    var self = this;
    if (self.getShowingAllItems(self.current_records)) {
        return MediaThread.urls['all-space'](active_tag, active_modified, self.citable);
    } else {
        return MediaThread.urls['your-space'](self.current_records.space_owner.username, active_tag, active_modified, self.citable);
    }
};

CollectionList.prototype.createAssetThumbs = function (assets) {
    var self = this;
    djangosherd.thumbs = [];
    for (var i = 0; i < assets.length; i++) {
        var asset = assets[i];
        djangosherd_adaptAsset(asset); //in-place
        
        var target_parent = jQuery(self.el).find(".gallery-item-" + asset.id)[0];
        
        if (!asset.thumbable) {
            if (jQuery(target_parent).hasClass("static-height")) {
                var thumbs = jQuery.grep(asset.sources, function(s) {
                   return s.label == 'thumb'; }); 
                if (thumbs.length && thumbs[0].height > 240) {
                    jQuery(target_parent).css({
                        height: (thumbs[0].height + 75) + 'px'
                    });
                } else {
                    jQuery(target_parent).css({height: '240px'});
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
            var width = jQuery(target_parent).width();
            var height = (width / asset.width * asset.height + 85) + 'px';
            if (jQuery(target_parent).hasClass("static-height")) {
                jQuery(target_parent).css({ height: height });
            }
            
            var obj_div = document.createElement('div');
            jQuery(target_parent).find('.asset-thumb').append(obj_div);
            
            asset.presentation = 'gallery';
            asset.x = 0;
            asset.y = 0;
            asset.zoom = 1;

            try {
                view.html.push(obj_div, {asset: asset});
                view.setState(asset);
            } catch (e) {
            }
        }
    }
};

CollectionList.prototype.createThumbs = function (assets) {
    var self = this;
    djangosherd.thumbs = [];
    for (var i = 0; i < assets.length; i++) {
        var asset = assets[i];
        djangosherd_adaptAsset(asset); //in-place
        if (asset.thumbable && asset.annotations) {
            for (var j = 0; j < asset.annotations.length; j++) {
                var ann = asset.annotations[j];
                
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
                var obj_div = document.createElement('div');
                obj_div.setAttribute('class', 'annotation-thumb');

                var target_div = jQuery(self.el).find(".annotation-thumb-" + ann.id)[0];
                target_div.appendChild(obj_div);
                // should probably be in .view
                asset.presentation = 'thumb';

                ann.asset = asset;
                view.html.push(obj_div, ann);
                view.setState(ann.annotation);
            }
        }
    }
};

CollectionList.prototype.updateSwitcher = function () {
    var self = this;
    self.switcher_context.display_switcher_extras = !self.switcher_context.showing_my_items;
    Mustache.update("switcher_collection_chooser", self.switcher_context, { parent: self.parent });
    
    // hook up switcher choice owner behavior
    jQuery(self.el).find("a.switcher-choice.owner").unbind('click').click(function (evt) {
        var srcElement = evt.srcElement || evt.target || evt.originalTarget;
        var bits = srcElement.href.split("/");
        var username = bits[bits.length - 1];
        
        if (username === "all-class-members") {
            self.current_records.space_owner = null;
        } else {
            self.current_records.space_owner = {'username': {}};
            self.current_records.space_owner.username.id = "";
            self.current_records.space_owner.username.public_name = ""; 
            self.current_records.space_owner.username = username;                 
        } 
        return self.filter();
    });
    
    jQuery(self.el).find("select.course-tags")
        .select2({
            placeholder: "Select tag"
        });    
    if ('tag' in self.current_records.active_filters &&
            self.current_records.active_filters.tag.length > 0) {

        jQuery(self.el).find("select.course-tags").select2("val",
            self.current_records.active_filters.tag.split(","));
    }
    
    jQuery(self.el).find("select.vocabulary").select2({});
    jQuery(self.el).find("select.vocabulary").each(function(idx, elt) {
        var name = jQuery(elt).attr("name");
        if (name in self.current_records.active_filters &&
                self.current_records.active_filters[name].length > 0) {
           
            jQuery(self.el).find("select[name='" + name + "']").select2("val",
                   self.current_records.active_filters[name].split(","));
        }
    });
};

CollectionList.prototype.getAssets = function () {
    var self = this;
    return jQuery(self.el).find('.asset-table').get(0);
};

CollectionList.prototype.updateAssets = function (the_records) {
    var self = this;
    self.switcher_context.owners = self.owners;
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
            if (self.create_annotation_thumbs) {
                self.createThumbs(the_records.assets);
            } else if (self.create_asset_thumbs) {
                self.createAssetThumbs(the_records.assets);
            }
            
            self.updateSwitcher();
            
            if (self.current_asset === null) {
                // handles the maximized view
                jQuery(window).scroll(function () { 
                    if (!self.loading &&
                        jQuery(window).scrollTop() >= jQuery(document).height() -
                            jQuery(window).height() - 300) {
                        self.loading = true;
                        self.appendItems(self.current_records);
                    }
                });
            } else {
                // handle the minimized view
                var container = jQuery(self.el).find("div.collection-assets")[0];
                jQuery(container).scroll(function () { 
                    if (!self.loading &&
                        container.scrollTop + jQuery(container).innerHeight() >= 
                            container.scrollHeight - 300) {
                        self.loading = true;
                        self.appendItems(self.current_records);
                    }
                });
            }
            
            jQuery(elt).fadeIn("slow");
            
            jQuery(self.el).find("a.switcher-choice.filterbydate").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.href.split("/");
                var filterName = bits[bits.length - 1];
                
                if (filterName === "all") {
                    self.current_records.active_filters.modified = "";
                } else {
                    self.current_records.active_filters.modified = filterName;
                }
                return self.filter();
            });
            
            jQuery(self.el).find("select.vocabulary").on('change select2-removed', function(evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var name = jQuery(srcElement).attr("name");
                self.current_records.active_filters[name] = jQuery(srcElement).val();
                return self.filter();
            });

            jQuery(self.el).find("select.course-tags").on('change select2-removed', function() {
                var elt = jQuery(self.el).find("select.course-tags");
                self.current_records.active_filters.tag = jQuery(elt).val();
                return self.filter();
            });
            
            jQuery(self.parent).find("a.switcher-choice.filterbytag").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.href.split("/");
                return self.filterByTag(bits[bits.length - 1]);
            });
            
            jQuery(self.el).find("a.collection-choice.edit-asset").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.parentNode.href.split("/");
                var asset_id = bits[bits.length - 1];
                jQuery(window).trigger('asset.edit', [ asset_id ]);
                return false;
            });
            
            jQuery(self.el).find("a.collection-choice.delete-asset").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.parentNode.href.split("/");
                var asset_id = bits[bits.length - 1];
                self.deleteAsset(asset_id);
                return false;
            });
            
            jQuery(self.el).find("a.collection-choice.delete-annotation").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.parentNode.href.split("/");
                return self.deleteAnnotation(bits[bits.length - 1]);
            });
            
            jQuery(self.el).find("a.collection-choice.create-annotation").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.parentNode.href.split("/");
                var asset_id = bits[bits.length - 1];
                jQuery(window).trigger('annotation.create', [ asset_id ]);
                return false;
            });
            
            jQuery(self.el).find("a.collection-choice.edit-annotation").unbind('click').click(function (evt) {
                var srcElement = evt.srcElement || evt.target || evt.originalTarget;
                var bits = srcElement.parentNode.href.split("/");
                var annotation_id = bits[bits.length - 1];
                var asset_id = jQuery('#annotation-' + annotation_id).parents("div.record").children("input.record").attr("value");
                jQuery(window).trigger('annotation.edit', [ asset_id, annotation_id ]);
                return false;
            });
            
            jQuery("#collection-help-button").unbind('click').click(function() {
                jQuery("#collection-overlay, #collection-help, #collection-help-tab").show();
                return false;
            });
            
            jQuery(self.el).find(".dismiss-help").unbind('click').click(function() {
                jQuery("#collection-overlay, #collection-help, #collection-help-tab").hide();
                return false;
            });            
            
            if (self.view_callback) {
                self.view_callback(the_records.assets.length);
            }
            
            if (self.scrollTop) {
                jQuery(self.el).find("div.collection-assets").scrollTop(self.scrollTop);
                self.scrollTop = undefined;
            }

            jQuery(window).trigger("resize");

        }
    });    
};
    
CollectionList.prototype.appendAssets = function (the_records) {
    var self = this;
    if (the_records.assets.length > 0) {
        var html = jQuery(Mustache.render_partial("assets", the_records));
        var container = jQuery(self.el).find("div.asset-table");
        jQuery(container).append(html);
        
        if (self.create_annotation_thumbs) {
            self.createThumbs(the_records.assets);
        } else if (self.create_asset_thumbs) {
            self.createAssetThumbs(the_records.assets);
        }
        
        jQuery(window).trigger("assets.refresh", [html]);
    }
};
    