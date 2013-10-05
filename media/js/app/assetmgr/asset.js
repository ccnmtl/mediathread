(function () {

    window.AnnotationList = new (function AnnotationListAbstract() {
        var self = this;
       
        this.init = function (config) {
            this.layers = {}; //should we really store layers here?

            this.active_annotation = null;
            this.active_asset = null;
            this.vocabulary = config.vocabulary;
            this.config = config;
            this.view_callback = config.view_callback;
            this.update_history = config.update_history !== undefined ? config.update_history : true;
            this.user_settings = { 'help_item_detail_view': true };
            
            this.eltsAssetDisplay = "#asset-header, #annotation-current, " +
                "#annotations-organized-container, " +
                "#asset-view-help-button," +
                "#asset-global-annotation div.actions";
            this.eltsAnnotationDisplay = "#asset-view-help-button," +
                "#asset-global-annotation, #annotations-organized";            
            
            if (String(window.location.hash).match(/edit_state=new/)) {
                self.config.edit_state = "annotation.create";
                window.location.hash = '';
            }
            
            djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 }, { 'mode': 'reset' });
            
            this.refresh(config);
            
            if (this.update_history) {
                // setup url rewriting for HTML5 && HTML4 browsers
                jQuery(window).bind("popstate", function (event) {
                    if (event.originalEvent.state) {
                        window.AnnotationList._update({ 'annotation_id': event.originalEvent.state.annotation_id }, "annotation-current");
                    }
                });
                
                jQuery(window).bind("hashchange", function () {
                    var asset_id = null;
                    var annotation_id = null;
                    var xywh = null;
                    
                    // parse out parameters on the command line
                    var params = window.location.pathname.split('/');
                    for (var i = 0; i < params.length; i++) {
                        var prev = i - 1;
                        if (prev > -1) {
                            if (params[prev] === 'asset') {
                                asset_id = params[i];
                            } else if (params[prev] === 'annotations') {
                                annotation_id = params[i];
                            }
                        }
                    }
                    
                    // parse out the annotation id in the hashtag (if it exists)
                    // hashtags override a urls embedded annotation_id
                    var config = {};
                    if (window.location.hash) {
                        var annotation_query = djangosherd.assetview.queryformat.find(document.location.hash);
                        if (annotation_query.length) {
                            config.xywh = annotation_query[0];
                        } else {
                            var annid = String(window.location.hash).match(/annotation_id=([.\d]+)/);
                            if (annid !== null) {
                                config.annotation_id = Number(annid[1]);
                            }
                        }
                    }
    
                    window.AnnotationList._update(config, "annotation-current", xywh);
                });
                return this;
            }
        };
        
        this.processAsset = function(asset_full) {
            self.asset_full_json = asset_full;
            self.user_settings = asset_full.user_settings;
             
            var theAsset;
            for (var key in asset_full.assets) {
                if (asset_full.assets.hasOwnProperty(key)) {
                    theAsset = asset_full.assets[key];
                    break;
                }
            }
            self.active_asset = theAsset;
        };
        
        this.refresh = function (config) {
            if (config.asset_id) {
                this.grouping = null;
                this.highlight_layer = null;
                
                // Retrieve the full asset w/annotations from storage
                djangosherd.storage.get({
                        id: config.asset_id,
                        type: 'asset',
                        url: MediaThread.urls['asset-json'](config.asset_id, /*annotations=*/true)
                    },
                    false,
                    function (asset_full) {
                        self.processAsset(asset_full);
                        
                        // window.location.hash
                        // #annotation_id=xxxx
                        // #xywh=pixel:x,y,w,h (MediaFragment syntax)
                        if (window.location.hash) {
                            var annotation_query = djangosherd.assetview.queryformat.find(document.location.hash);
                            if (annotation_query.length) {
                                config.xywh = annotation_query[0];
                            } else {
                                var annid = String(window.location.hash).match(/annotation_id=([.\d]+)/);
                                if (annid !== null) {
                                    config.annotation_id = Number(annid[1]);
                                }
                            }
                        }
                        
                        self._update(config, "asset-view-details");
                        self._addHistory(/*replace=*/true);
                        
                        // Saved Annotations Form -- setup based on showAll/Group preferences in local storage
                        var frm = document.forms['annotation-list-filter'];
                        if (frm) {
                            frm.elements.showall.checked = retrieveData('annotation-list-filter__showall');
                            jQuery(frm.elements.groupby).val(
                                    retrieveData('annotation-list-filter__group') || 'author');
        
                            jQuery(frm.elements.showall).change(self.showHideAnnotations);
                            jQuery(frm.elements.groupby).change(function () {
                                var val = jQuery(this).val();
                                storeData('annotation-list-filter__group', val);
                                self.groupBy(val);
                            });
                            self.groupBy(jQuery(frm.elements.groupby).val());                            
                        }
                    }
                );
            }
        };

        this.showHideAnnotations = function () {
            var show = document.forms['annotation-list-filter'].elements.showall.checked;
            storeData('annotation-list-filter__showall', show || '');
            if (show) {
                self.layers[self.grouping].show();
            } else {
                self.layers[self.grouping].hide();
            }
        };
        
        ///Groupby('author')
        ///Groupby('tag')
        //  - get, group
        //  - replace/hide-show Layer, group-by color
        //  - decorate
        this.groupBy = function (grouping) {
            ///Do nothing if we can't or don't need to.
            if (this.grouping === grouping || !(self.active_asset && self.active_asset.id)) {
                return;
            }

            ///hide previous grouping so we can show the new one.
            if (this.grouping) {
                this.layers[this.grouping].hide();
            }
            
            //show (and create) the new grouping
            if (!this.layers[grouping]) {
                this.layers[grouping] = djangosherd.assetview.layer();
                if (!this.layers[grouping]) {
                    //stub if it doesn't exist.
                    this.layers[grouping] = {
                        removeAll: function () {},
                        add: function () {},
                        remove: function () {},
                        show: function () {},
                        hide: function () {}
                    };
                } else {
                    this.layers[grouping].create(grouping, {
                        //onclick:function (feature) {},
                        title: ' ',//hide grouping title for the video view
                        onmouseenter: function (id, name) {
                            self.highlight(id);
                        },// */
                        onmouseleave: function (id, name) {
                            self.unhighlight();
                        },
                        zIndex: 300 //above highlight
                    });
                }
            }
            this.grouping = grouping;
            this.showHideAnnotations();
            this.resetHighlightLayer();

            switch (grouping) {
            case 'tag':
                this.layers[grouping].color_by = function (ann) {
                    if (ann.metadata.tags.length) {
                        var tags = [];
                        for (var k = 0; k < ann.metadata.tags.length; k++) {
                            tags.push(ann.metadata.tags[k].name);
                        }
                        return tags;
                    } else {
                        //127 ensures that None is last
                        return [String.fromCharCode(127) + 'No Tags'];
                    }
                };
                break;
            case 'author':
                this.layers[grouping].color_by = function (ann) {
                    return [ann.author.public_name];
                };
                break;
            }

            self.updateAnnotationList();
        };
        
        this.updateAnnotationList = function () {
            var frm = document.forms['annotation-list-filter'];
            if (!frm) {
                return;
            }
            
            var grouping = self.grouping;
            var context = {'annotation_list': []};
            var cats = {};
            var user_listing = false;
            self.layers[grouping].removeAll();
            DjangoSherd_Colors.reset(grouping);
            for (var i = 0; i < self.active_asset.annotations.length; i++) {
                var ann = self.active_asset.annotations[i];
                ///TODO: WILL BREAK when we ajax this
                if (self.active_annotation) {
                    ann.active_annotation = (ann.id === self.active_annotation.id);
                }
                if (ann.metadata) {
                    var titles = self.layers[grouping].color_by(ann);
                    for (var j = 0; j < titles.length; j++) {
                        var title = titles[j];
                        var color = DjangoSherd_Colors.get(title);
                        /// add the annotation onto the layer in the right color
                        if (ann.annotation) {
                            self.layers[grouping].add(
                                ann.annotation, { 'id': ann.id,
                                                 'color': color
                                                }
                            );
                        }
                        ///..and setup the category for the AnnotationList
                        if (!cats[title]) {
                            cats[title] = {'title': title,
                                           'color': color,
                                           'annotations': []
                                          };
                            if (title && title === MediaThread.user_full_name) {
                                user_listing = title;
                            } else {
                                context.annotation_list.push(title);
                            }
                        }
                        cats[title].annotations.push(ann);
                    }
                }
            }
            
            ///sort and build the annotation_list
            ///TODO: if by_author, then sort the owner to the top.
            context.annotation_list.sort();
            if (user_listing) {
                context.annotation_list.unshift(user_listing);
            }
            
            for (var k = 0; k < context.annotation_list.length; k++) {
                context.annotation_list[k] = { 'category': cats[context.annotation_list[k]] };
            }
            
            
            Mustache.update('annotation-list', context, {
                pre: function (elt) {
                    jQuery(elt).hide();
                    jQuery("div.accordion").accordion("destroy");
                },
                post: function (elt) {
                    var options = {
                        autoHeight: false,
                        collapsible: true,
                        active: false
                    };
                    
                    jQuery(elt).show();
                    jQuery('li.annotation-listitem', elt).each(self.decorateLink);
                    
                    // active the current annotation if it exists
                    jQuery("div.accordion").accordion(options);
                    if (self.active_annotation) {
                        var active = jQuery("#accordion-" + self.active_annotation.id)[0];
                        var parent = jQuery(active).parents("div.accordion");
                        jQuery(parent).accordion("activate", active);
                        
                        jQuery(active).find('input.annotation-listitem-icon').show();
                        
                        setTimeout(function () {
                            var list = jQuery(active).offsetParent()[0];
                            jQuery(list).scrollTop(jQuery(list).scrollTop() + jQuery(active).position().top);
                        }, 200);
                    }
                    
                    // Wait to hook up the changestart to prevent default 'showAnnotation'
                    // behavior on initial activation
                    jQuery("div.accordion").accordion({ 'changestart': self.showAnnotation });
                }
            });
        };
        
        this.resetHighlightLayer = function () {
            if (this.highlight_layer) {
                this.highlight_layer.destroy();
            }
            this.highlight_layer = djangosherd.assetview.layer();
            if (this.highlight_layer) {
                this.highlight_layer.create('focus', { zIndex: 200, title: ' ' });
            }
        };
        
        this.unhighlight = function () {
            if (self.highlighted_nodes) {
                jQuery(self.highlighted_nodes).removeClass('highlight');
            }
            if (self.highlight_layer) {
                self.highlight_layer.removeAll();
            } else {
                self.resetHighlightLayer();
            }
        };

        this.highlight = function (ann_id) {
            self.unhighlight();
            //highlight on list
            self.highlighted_nodes = jQuery('.annotation-listitem-' + ann_id).addClass('highlight').toArray();

            if (self.highlight_layer) {
                djangosherd.storage.get({
                    'id': ann_id,
                    'type': 'annotations'
                }, function (ann) {
                    self.highlight_layer
                        .add(ann.annotation, { id: ann.id,
                                               color: 'black',
                                               bgcolor: 'highlight',
                                               pointerEvents: 'none',
                                               zIndex: 1
                                             });
                });
            }//end if (self.highlight_layer)
        }; //end function highlight()

        this.decorateLink = function (li) {
            if (self.highlight_layer) {
                jQuery(this)
                .mouseenter(function (evt) {
                    self.highlight(jQuery(this).attr('data-id'));
                })
                .mouseleave(function (evt) {
                    self.unhighlight();
                });
            }
        };
        
        this.showExportDialog = function (anchor, asset_id) {
            var self = this;
            var element = jQuery(".export-finalcutpro")[0];
            var list  = jQuery(element).find("ul.selections")[0];
            jQuery(list).find('li').remove();
            
            if (this.hasOwnProperty('active_asset')) {
                for (var i = 0; i < this.active_asset.annotations.length; i++) {
                    var ann = this.active_asset.annotations[i];
                    if (ann.annotation) {
                        var li = "<li>" +
                            "<span class='ui-icon-reverse ui-icon-arrowthick-2-n-s'></span>" +
                            "<input readonly='readonly' type='text' name='" + ann.id + "' value='" + ann.metadata.title + "'></input></li>";
                        
                        jQuery(list).append(li);
                    }
                }
            }
            
            jQuery(list).sortable({ containment: 'parent' }).disableSelection();
            
            jQuery(element).dialog({
                buttons: [{ text: "Export",
                    click: function () {
                        jQuery("form[name=export-finalcutpro]").trigger('submit');
                        jQuery(this).dialog("close");
                    }
                }],
                draggable: true,
                resizable: true,
                modal: true,
                width: 425,
                position: "top",
                zIndex: 10000
            });
            
            return false;
        };
        
        this.onExportSubmit = function (evt) {
            var selections = jQuery('ul.selections li input[type=text]');
            for (var i = 0; i < selections.length; i++) {
                var id = jQuery(selections[i]).attr('name');
                jQuery(selections[i]).attr("name", i);
                jQuery(selections[i]).attr("value", id);
            }
            return true;
        };
        
        this.showHelp = function () {
            jQuery("#asset-view-overlay, #asset-view-help, #asset-view-help-tab").show();
            return false;
        };
        
        this.dismissHelp = function () {
            jQuery("#asset-view-overlay, #asset-view-help, #asset-view-help-tab").hide();
            var checked = jQuery("#asset-view-show-help").is(":checked");
            updateHelpSetting(MediaThread.current_username, 'help_item_detail_view', !checked);
            return false;
        };
        
        this.showAsset = function () {
            self._update({ 'level': 'item', 'asset_id': self.active_asset.id }, "annotation-current");
            self._addHistory(/*replace=*/false);
        };

        ///Item Edit -- global annotation
        this.editItem = function () {
            jQuery(self.eltsAssetDisplay)
                .fadeOut()
                .promise()
                .done(function () {
                    var elt = jQuery("#edit-global-annotation-form");
                    jQuery(elt).fadeIn();
                });
        };
        
        this.cancelItem = function () {
            jQuery(window).trigger("annotation.on_cancel", []);
            
            var form = jQuery("#edit-global-annotation-form");
            
            jQuery(form).fadeOut(function () {
                jQuery(self.eltsAssetDisplay).fadeIn();
            });
            
            return false;
        };
        
        this.deleteItem = function (event, record, asset_id) {
            event.stopPropagation();
            
            var url = MediaThread.urls['asset-delete'](asset_id);
            ajaxDelete(null, null, {
                'href': url,
                'item': true,
                'success': function () {
                    jQuery(window).trigger("asset.on_delete", [ asset_id ]);
                }
            });

            return false;
        };
        
        ///Item Save -- global annotation
        this.saveItem = function (saveButton) {
            var frm = jQuery(saveButton).parents('form')[0];
            
            // Validate the title, if it is editable
            var newTitle = null;
            if ('asset-title' in frm.elements) {
                newTitle = frm.elements['asset-title'].value;
                if (newTitle.length < 1) {
                    showMessage('Please specify an item title',
                                undefined,
                                'Error',
                                {my: "center",
                                 at: "center",
                                 of: jQuery("div.asset-view-tabs")});
                    return false;
                }
            }                    
            
            // Validate the tag fields...should be in djangosherd?
            var tag_field = frm.elements['annotation-tags'];
            if (tag_field) {//is this null?
                var tags = tag_field.value.split(',');
                for (var i = 0; i < tags.length; i++) {
                    if (tags[i].trim().length > 25) {
                        showMessage('The ' + tags[i] + ' is too long. Tags should be less than 25 characters. ' +
                              'And, be sure to separate your tags with commas.');
                        return false;
                    }
                }
            }
            
            jQuery(saveButton).attr("disabled", "disabled").attr("value", "Saving...").addClass("saving");
            
            
            jQuery.ajax({
                type: 'POST',
                url: frm.action,
                data: jQuery(frm).serializeArray(),
                dataType: 'json',
                error: function () {
                    jQuery(saveButton).removeAttr("disabled").attr("value", "Save").removeClass("saving");
                    showMessage('There was an error saving your changes.');
                },
                success: function (json, textStatus, xhr) {
                    // Repopulate the cache & refresh the asset view
                    // @todo -- if asset_json could be moved over to djangosherd:views.py,
                    // then create_annotation, edit_annotation could just return the full asset json
                    // And eliminate this extra call.
                    djangosherd.storage.get({
                        id: json.asset.id,
                        type: 'asset',
                        url: MediaThread.urls['asset-json'](json.asset.id,/*annotations=*/true)
                    },
                    false,
                    function (asset_full) {
                        if (json.annotation.creating) {
                            jQuery(window).trigger("annotation.on_create", []);
                        } else {
                            jQuery(window).trigger("annotation.on_save", []);
                        }
                        
                        self.processAsset(asset_full);
                        
                        jQuery(saveButton).removeAttr("disabled");
                        jQuery(saveButton).removeClass("saving");
                        jQuery(saveButton).attr("value", "Save");
                        
                        var context = {
                            'asset-current': self.active_asset,
                            'vocabulary': self.vocabulary
                        };
                        
                        Mustache.update("asset-view-header", context);
                         
                        Mustache.update("asset-global-annotation", context, {
                            pre: function (elt) { jQuery(elt).hide(); },
                            post: function (elt) {
                                jQuery(elt).fadeIn("slow", function () {
                                    jQuery("#annotations-organized-container, #annotation-current")
                                    .fadeIn()
                                    .promise()
                                    .done(function() {
                                        self._initTags();
                                        self._initConcepts();
                                        self._initReferences();
                                        jQuery(window).trigger("resize");
                                    });                                    
                                });
                            }
                        });
                    });
                }
            });
            
            return false;
        };
        
        this.showAnnotation = function (event, ui) {
            if (ui.newHeader.length > 0) {
                jQuery('input.annotation-listitem-icon').hide();
                
                jQuery(ui.newHeader).find('input.annotation-listitem-icon').show();
                
                var new_annotation_id = jQuery(ui.newHeader).data("id");
                self._update({ 'annotation_id': new_annotation_id }, "annotation-current");
                self._addHistory(/*replace=*/false);
                
                var group = jQuery(ui.newHeader).parents('li.annotation-group')[0];
                jQuery(group).siblings().find('div.accordion').accordion("activate", false);

                setTimeout(function () {
                    var list = jQuery(ui.newHeader).offsetParent()[0];
                    jQuery(list).scrollTop(jQuery(list).scrollTop() + jQuery(ui.newHeader).position().top - 10);
                }, 200);

            }
        };

        this.deleteAnnotation = function (event, record, annotation_id) {
            event.stopPropagation();
            
            var self = this;
            if (annotation_id === self.active_annotation.id) {
                var url = MediaThread.urls['annotation-delete'](self.active_asset.id, annotation_id);
                ajaxDelete(null, "accordion-" + annotation_id,
                    {'href': url, 'success': this.deleteAnnotationComplete });
            }
            return false;
        };
        
        this.deleteAnnotationComplete = function () {
            self.refresh({ asset_id: self.active_asset.id });
            jQuery(window).trigger("annotation.on_delete", []);
        };
        
        this.cancelAnnotation = function () {
            jQuery(window).trigger("annotation.on_cancel", []);
            
            var annotation_id = self.active_annotation ? self.active_annotation.id : null;
            jQuery("#asset-details-annotations-current").fadeOut(function () {
                self._update({ 'annotation_id' : annotation_id, 'editing': false }, "annotation-current");
                
                if (self.active_annotation) {
                    var active = jQuery("#accordion-" + self.active_annotation.id)[0];
                    var parent = jQuery(active).parents("div.accordion");
                    jQuery(parent).accordion("activate", active);
                }
                jQuery(self.eltsAnnotationDisplay).fadeIn();
            });
            return false;
        };
        
        ///Annotation Add Form
        //  - author === current_user
        this.newAnnotation = function () {
            var context = {
                'vocabulary': self.vocabulary,
                'annotation': {
                    'editing': true,
                    'metadata': {
                        'author': { 'id': MediaThread.current_user },
                        'author_name': MediaThread.user_full_name
                }
            }};
            
            jQuery(self.eltsAnnotationDisplay)
                .fadeOut()
                .promise()
                .done(function () {
                    Mustache.update('annotation-current', context, { post: function (elt) {
                        djangosherd.assetview.clipform.html.push('clipform-display', {
                            asset : {}
                        });
                        
                        // Preserve zoom level on 'new selection'
                        //djangosherd.assetview.setState({});
                        // Let's see if just not setting state will work.
                        djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 }, { 'mode': 'create' });
                        
                        self._initTags();
                        self._initReferences();
                        jQuery("select.vocabulary").select2({});
                        jQuery("#asset-details-annotations-current").fadeIn();
                        jQuery(window).trigger("resize");
                    }});
            });
        };
        
        ///Annotation Edit
        // - new annotation with properties of current annotation minus id
        this.editAnnotation = function () {
            jQuery(self.eltsAnnotationDisplay)
                .fadeOut()
                .promise()
                .done(function () {
                    self._update({
                        'annotation_id': self.active_annotation.id,
                        'editing': true },
                        "annotation-current"); 
                    jQuery(window).trigger("resize");
                });
            return false;
        };
        
        ///Annotation Copy
        // - new annotation with properties of current annotation minus id
        this.copyAnnotation = function () {
            // Add template...but with all the properties of this annotation.
            var context = {
                'vocabulary': self.vocabulary,
                'annotation': {
                    'editing': true,
                    'copying': true,
                    'metadata': {
                        'body': self.active_annotation.metadata.body,
                        'tags': self.active_annotation.metadata.tags,
                        'title': self.active_annotation.metadata.title,
                        'author': { 'id': MediaThread.current_user },
                        'author_name': MediaThread.user_full_name
                    },
                    'range1': self.active_annotation.range1,
                    'range2': self.active_annotation.range2,
                    'annotation_data': self.active_annotation.annotation_data
                }};
            
            jQuery(self.eltsAnnotationDisplay)
                .fadeOut()
                .promise()
                .done(function () {
                    Mustache.update('annotation-current', context, {
                        pre: function (elt) {
                            jQuery(elt).hide();
                        },
                        post: function (elt) {
                            if (self.active_annotation) {
                                djangosherd.assetview.clipform.html.push('clipform-display', {
                                    asset : {}
                                });
            
                                djangosherd.assetview.setState(self.active_annotation.annotation);
                                djangosherd.assetview.clipform.setState(self.active_annotation.annotation, { 'mode': 'copy' });
                                
                                self._initTags();
                                self._initConcepts();
                                self._initReferences();
                                jQuery(elt).fadeIn();
                                jQuery(window).trigger("resize");
                            }
                        }
                    });
            });
            
            return false;
        };
        
        ///Annotation Save
        //  - update list items
        //  - replace with 'new' annotation
        this.saveAnnotation = function (saveButton) {
            jQuery(saveButton).attr("disabled", "disabled").attr("value", "Saving...").addClass("saving");
            
            var frm = document.forms['edit-annotation-form'];

            // Push clipform or assetview state into "local storage", i.e. the form that is posted to the server.
            // @todo -- Unsure if this is the best spot for this...
            var obj = djangosherd.assetview.clipform.getState();
            if (_propertyCount(obj) > 0) {
                djangosherd.assetview.clipform.storage.update(obj, true);
            } else {
                obj = djangosherd.assetview.getState();
                if (_propertyCount(obj) > 0) {
                    djangosherd.assetview.clipform.storage.update(obj, true);
                }
            }
            
            if (frm.elements['annotation-title'].value === '') {
                showMessage('Please specify a selection title',
                    function() {
                        jQuery(saveButton).removeAttr("disabled");
                        jQuery(saveButton).removeClass("saving");
                        jQuery(saveButton).attr("value", "Save");
                    },
                    'Error',
                    {my: "center",
                     at: "center",
                     of: jQuery("div.asset-view-tabs")});
                return;
            }
            
            // Save the results up on the server
            var url, creating;
            
            if (frm.elements['annotation-id']) {
                url = MediaThread.urls['annotation-edit'](self.active_asset.id, frm.elements['annotation-id'].value);
                creating = false;
            } else {
                url = MediaThread.urls['annotation-create'](self.active_asset.id);
                creating = true;
            }
                
            jQuery.ajax({
                type: 'POST',
                url: url,
                data: jQuery(frm).serialize(),
                dataType: 'json',
                cache: false, // Chrome && Internet Explorer has aggressive caching policies.
                success: function (json, textStatus, jqXHR) {
                    // Repopulate the cache & refresh the annotation view
                    // @todo -- if asset_json could be moved over to djangosherd:views.py,
                    // then create_annotation, edit_annotation could just return the full asset json
                    // And eliminate this extra call.
                    djangosherd.storage.get({
                        id: json.asset.id,
                        type: 'asset',
                        url: MediaThread.urls['asset-json'](json.asset.id,/*annotations=*/true)
                    },
                    false,
                    function (asset_full) {
                        if (creating) {
                            jQuery(window).trigger("annotation.on_create", []);
                        } else {
                            jQuery(window).trigger("annotation.on_save", []);
                        }
                        
                        self.refresh({asset_id: self.active_asset.id,
                                      annotation_id: json.annotation.id});
                    });
                }
            });
        };
        
        // Push annotation_ids on the history stack as a user views them.
        // If an annotation is missing (deleted?) -- revert to the asset view.
        // HTML 5.0 browsers: https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
        // < HTML 5.0 browsers: Hashtag implementation
        this._addHistory = function (replace) {
            if (self.update_history === false) {
                return;
            }
            
            if (window.history.pushState) {
                var action = replace ? window.history.replaceState : window.history.pushState;
                var currentState = { asset_id: ((self.active_asset) ? self.active_asset.id : self.config.asset_id) };
                if (self.active_annotation) {
                    currentState.annotation_id = self.active_annotation.id;
                    action.apply(window.history, [currentState, self.active_annotation.title, "/asset/" + currentState.asset_id + "/annotations/" + self.active_annotation.id + "/"]);
                } else {
                    action.apply(window.history, [currentState, self.active_asset.title, "/asset/" + self.active_asset.id + "/"]);
                }
            } else if (!replace) {
                // hashtag implementation. only needed for push
                if (self.active_annotation) {
                    window.location.hash = "annotation_id=" + self.active_annotation.id;
                } else {
                    window.location.hash = '';
                }
            }
        };
        
        this._initConcepts = function() {
            jQuery("select.vocabulary").select2({});

            var elt;
            if (self.active_asset && self.active_asset.global_annotation) {
                elt = jQuery("#edit-global-annotation-form");
                self._selectConcepts(elt,
                    self.active_asset.global_annotation.vocabulary);
            }
            if (self.active_annotation) {
                elt = jQuery("#edit-annotation-form");
                self._selectConcepts(elt, self.active_annotation.vocabulary);
            }
        };
        
        this._selectConcepts = function(elt, vocabulary) {
            for (var i=0; i < vocabulary.length; i++) {
                var selector = 'select[name="vocabulary-' + vocabulary[i].id + '"]'; 
                var selectBox = jQuery(elt).find(selector)[0];
                var terms = [];
                for (var j=0; j < vocabulary[i].terms.length; j++) {
                    terms.push(vocabulary[i].terms[j].id);
                }
                jQuery(selectBox).select2("val", terms);
            }
        };
        
        this._initReferences = function() {
            jQuery.ajax({
                type: 'GET',
                url: MediaThread.urls.references(self.active_asset),
                dataType: 'json',
                error: function () {},
                success: function (json, textStatus, xhr) {
                    Mustache.update("asset-references", json);                
                }
            });
        };
        
        this._initTags = function() {
            jQuery.ajax({
                type: 'GET',
                url: MediaThread.urls.tags(),
                dataType: 'json',
                error: function () {},
                success: function (json, textStatus, xhr) {
                    var tags = [];
                    for (i=0; i < json.objects.length; i++) {
                        tags.push(json.objects[i].name);
                    }
                    jQuery("input[name='annotation-tags']").select2({
                        tags: tags,
                        tokenSeparators: [","],
                        maximumInputLength: 20
                    });            
                }
            });            
        };

        this._update = function (config, template_label) {
            // Set the active annotation
            self.active_annotation = null;
            self.xywh = null;
            
            var context = {
                'asset-current': self.active_asset,
                'vocabulary': self.vocabulary
            };
            
            if (config.annotation_id) {
                var annotation_id = parseInt(config.annotation_id, 10);

                for (var i = 0; i < self.active_asset.annotations.length; i++) {
                    var ann = self.active_asset.annotations[i];
                    if (ann.id === annotation_id) {
                        self.active_annotation = ann;
                        break;
                    }
                }
                if (self.active_annotation) {
                    context.annotation = self.active_annotation;
                    if (self.config.edit_state === "annotation.edit") {
                        context.annotation.editing = true;
                    } else {
                        context.annotation.editing = config.editing;
                    }
                }
            } else if (config.xywh) {
                self.xywh = config.xywh;
                context.annotation = {
                    'editing': true,
                    'metadata': {
                        'author': { 'id': MediaThread.current_user },
                        'author_name': MediaThread.user_full_name
                    }
                };
            } else if (self.config.edit_state === "annotation.create") {
                context.annotation = {
                    'editing': true,
                    'metadata': {
                        'author': { 'id': MediaThread.current_user },
                        'author_name': MediaThread.user_full_name
                    }
                };
            } else if (self.active_asset && (self.active_asset.user_analysis === undefined ||
                       self.active_asset.user_analysis < 1)) {
                context.show_help = self.user_settings.help_item_detail_view;
            }
            context.show_help_checked = !self.user_settings.help_item_detail_view;
            
            Mustache.update(template_label, context, {
                pre: function (elt) { jQuery(elt).hide(); },
                post: function (elt) {
                    var i;
                    self.edit_state = null;
                    
                    djangosherd.assetview.clipform.html.push('clipform-display', {
                        asset: {}
                    });
                    
                    Mustache.update("asset-view-help", context);
                    Mustache.update("asset-view-header", context);
                    Mustache.update("asset-global-annotation", context);                    
                    
                    if (template_label === "asset-view-details") {
                        Mustache.update("asset-sources", context);
                    }
                    
                    if (self.active_annotation) {
                        djangosherd.assetview.setState(self.active_annotation.annotation);
                    } else if (self.xywh) {
                        djangosherd.assetview.setState(self.xywh);
                    } else {
                        // #default initialization. no annotation defined.
                        djangosherd.assetview.setState();
                    }
                    
                    self._initTags();
                    self._initConcepts();
                    self._initReferences();
                    
                    jQuery(elt).fadeIn("slow", function () {
                        if (self.active_annotation) {
                            djangosherd.assetview.clipform.setState(self.active_annotation.annotation,
                                    { 'mode': context.annotation.editing ? 'edit' : 'browse',
                                      'tool_play': jQuery('#annotation-body-' + self.active_annotation.id + ' input.videoplay')[0] });
                        } else if (self.xywh) {
                            if (djangosherd.assetview.clipform) {
                                djangosherd.assetview.clipform.setState(self.xywh, {'mode': 'create' });
                            }
                        } else {
                            // #default initialization. no annotation defined.
                            djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 },
                                { 'mode': context.annotation && context.annotation.editing ? 'create' : 'browse' });
                        }
                        if (self.view_callback) {
                            self.view_callback();
                        }
                    });
                }
            });
        };
    })();
})();
