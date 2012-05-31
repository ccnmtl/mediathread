(function () {

    window.AnnotationList = new (function AnnotationListAbstract() {
        var self = this;
       
        this.init = function (config) {
            this.layers = {}; //should we really store layers here?
            this.grouping = null;
            this.highlight_layer = null;

            this.active_annotation = null;
            this.active_asset = null;
            this.active_asset_annotations = null;
            this.config = config;
            
            jQuery("#edit-item-form").submit(function () {
                return self.saveItem();
            });
            
            window.onbeforeunload = config.level === "item" ? this.saveItemPrompt : null;

            jQuery.ajax({
                url: '/site_media/templates/annotations.mustache?nocache=v2',
                dataType: 'text',
                cache: false, // Chrome && Internet Explorer has aggressive caching policies.
                success: function (text) {
                    MediaThread.templates.annotations = Mustache.template('annotations', text);
                    
                    if (config.asset_id) {
                        // Retrieve the full asset w/annotations from storage
                        djangosherd.storage.get({
                                id: config.asset_id,
                                type: 'asset',
                                url: MediaThread.urls['asset-json'](config.asset_id, /*annotations=*/true)
                            },
                            false,
                            function (asset_full) {
                                var theAsset;
                                for (var key in asset_full.assets) {
                                    if (asset_full.assets.hasOwnProperty(key)) {
                                        theAsset = asset_full.assets[key];
                                        break;
                                    }
                                }
                                self.active_asset = theAsset;
                                self.active_asset_annotations = asset_full.annotations;
                                
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
                                
                                self._update(config, "asset-annotations");
                                self._addHistory(/*replace=*/true);
                                
                                // Saved Annotations Form -- setup based on showAll/Group preferences in local storage
                                var frm = document.forms['annotation-list-filter'];
            
                                frm.elements.showall.checked = hs_DataRetrieve('annotation-list-filter__showall');
                                jQuery(frm.elements.groupby).val(
                                        hs_DataRetrieve('annotation-list-filter__group') || 'author');
            
                                jQuery(frm.elements.showall).change(self.showHideAnnotations);
                                jQuery(frm.elements.groupby).change(function () {
                                    var val = jQuery(this).val();
                                    hs_DataStore('annotation-list-filter__group', val);
                                    self.groupBy(val);
                                });
                                self.groupBy(jQuery(frm.elements.groupby).val());
                            }
                        );
                    }
                }
            });
            
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
        };

        this.showHideAnnotations = function () {
            var show = document.forms['annotation-list-filter'].elements.showall.checked;
            hs_DataStore('annotation-list-filter__showall', show || '');
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
                        return [String.fromCharCode(127) + '(None)'];
                    }
                };
                break;
            case 'author':
                this.layers[grouping].color_by = function (ann) {
                    return [ann.metadata.author_name];
                };
                break;
            }

            self.updateAnnotationList();
        };
        
        this.updateAnnotationList = function () {
            djangosherd.storage.get({
                id: self.active_asset.id,
                type: 'asset',
                url: MediaThread.urls['asset-json'](self.active_asset.id, /*annotations=*/true)
            },
            false,
            function (asset_full) {
                var grouping = self.grouping;
                var context = {'annotation_list': []};
                var cats = {};
                var user_listing = false;
                self.layers[grouping].removeAll();
                DjangoSherd_Colors.reset(grouping);
                for (var i = 0; i < asset_full.annotations.length; i++) {
                    var ann = asset_full.annotations[i];
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
                    pre: function (elt) { jQuery(elt).hide(); },
                    post: function (elt) {
                        jQuery(elt).fadeIn("slow");
                        jQuery('li.annotation-listitem', elt).each(self.decorateLink);
                    }
                });
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
        
        this.showAnnotation = function (annotation_id) {
            self._update({ 'annotation_id': annotation_id }, "annotation-current");
            self._addHistory(/*replace=*/false);
        };
        
        this.cancelAnnotation = function () {
            var annotation_id = self.active_annotation ? self.active_annotation.id : null;
            self._update({ 'annotation_id' : annotation_id }, "annotation-current");
            jQuery("#annotations-organized").show();
        };
        
        ///Annotation Add Form
        //  - author === current_user
        this.newAnnotation = function () {
            var context = { 'annotation': {
                'editing': true,
                'showCancel': true,
                'metadata': {
                    'author': { 'id': MediaThread.current_user },
                    'author_name': MediaThread.user_full_name
                }
            }};
            
            Mustache.update('annotation-current', context, { post: function (elt) {
                djangosherd.assetview.clipform.html.push('clipform-display', {
                    asset : {},
                    extra : { 'tools' : 'clipform-tools' }
                });
                
                djangosherd.assetview.setState({});
                djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 }, { 'mode': 'create' });
                jQuery("#annotations-organized").hide();
            }});
        };
        
        ///Annotation Edit
        // - new annotation with properties of current annotation minus id
        this.editAnnotation = function () {
            self._update({ 'annotation_id': self.active_annotation.id, 'editing': true }, "annotation-current");
            return false;
        };
        
        ///Annotation Copy
        // - new annotation with properties of current annotation minus id
        this.copyAnnotation = function () {
            // Add template...but with all the properties of this annotation.
            var context = { 'annotation': {
                    'editing': true,
                    'showCancel': true,
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
            
            Mustache.update('annotation-current', context, { post: function (elt) {
                if (self.active_annotation) {
                    djangosherd.assetview.clipform.html.push('clipform-display', {
                        asset : {},
                        extra : { 'tools' : 'clipform-tools' }
                    });

                    djangosherd.assetview.setState(self.active_annotation.annotation);
                    djangosherd.assetview.clipform.setState(self.active_annotation.annotation, { 'mode': 'copy' });
                    jQuery("#annotations-organized").hide();
                }
            }});
            
            return false;
        };
        
        ///Item Save
        this.saveItem = function () {
            var frm = document.forms['edit-item-form'];
            if (frm.elements['annotation-tags'].value === "" && frm.elements['annotation-body'].value === "") {
                alert("Please specify tags and notes before saving.");
                frm.elements['annotation-tags'].focus();
                return false;
            } else {
                window.onbeforeunload = null;
                return true;
            }
        };
        
        ///Item Save Prompt
        this.saveItemPrompt = function () {
            var frm = document.forms['edit-item-form'];
            if (frm.elements['annotation-tags'].value === "" && frm.elements['annotation-body'].value === "") {
                return "Add tags and notes to place this item in your collection.";
            }
        };
        
        ///Annotation Save
        //  - update list items
        //  - replace with 'new' annotation
        this.saveAnnotation = function () {
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
            
            // Validate the tag fields...should be in djangosherd?
            var tag_field = frm.elements['annotation-tags'];
            if (tag_field) {//is this null?
                var tags = tag_field.value.split(',');
                for (var i = 0; i < tags.length; i++) {
                    if (tags[i].length > 50) {
                        alert('You are trying to add a tag with greater than the maximum 50 character-limit.  Be sure to separate your tags with commas.  Also, tags are best used as single words that you would tag other assets with.  Try using the Notes field for longer expressions.');
                        return;
                    }
                }
            }
            
            if (frm.elements['annotation-title'].value === '') {
                alert('Please specify a selection title');
                return;
            }
            
            // Save the results up on the server
            var url =  frm.elements['annotation-id'] ?
                url = MediaThread.urls['edit-annotation'](self.active_asset.id, frm.elements['annotation-id'].value) :
                url = MediaThread.urls['create-annotation'](self.active_asset.id);
                
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
                        var theAsset;
                        for (var key in asset_full.assets) {
                            if (asset_full.assets.hasOwnProperty(key)) {
                                theAsset = asset_full.assets[key];
                                break;
                            }
                        }
                        self.active_asset = theAsset;
                        self.active_asset_annotations = asset_full.annotations;
                         
                        self._update({ 'annotation_id': json.annotation.id }, "annotation-current");
                        self.updateAnnotationList();
                        self._addHistory(/*replace=*/false);
                        jQuery("#annotations-organized").show();
                        window.onbeforeunload = null;
                    });
                }
            });
        };
        
        // Push annotation_ids on the history stack as a user views them.
        // If an annotation is missing (deleted?) -- revert to the asset view.
        // HTML 5.0 browsers: https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
        // < HTML 5.0 browsers: Hashtag implementation
        this._addHistory = function (replace) {
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

        this._update = function (config, template_label) {
            // Set the active annotation
            self.active_annotation = null;
            self.xywh = null;
            
            var context = {};
            
            if (config.annotation_id) {
                var annotation_id = parseInt(config.annotation_id, 10);

                for (var i = 0; i < self.active_asset_annotations.length; i++) {
                    var ann = self.active_asset_annotations[i];
                    if (ann.id === annotation_id) {
                        self.active_annotation = ann;
                        break;
                    }
                }
                if (self.active_annotation) {
                    context.annotation = self.active_annotation;
                    context.annotation.editing = config.editing;
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
            } else if (!self.active_asset_annotations.length || self.active_asset_annotations.length <= 1) {
                context.annotation = {
                    'editing': true,
                    'metadata': {
                        'author': { 'id': MediaThread.current_user },
                        'author_name': MediaThread.user_full_name
                    }
                };
            }
            
            context.showNewAnnotation = !context.annotation || (context.annotation && !context.annotation.editing);
            
            if (context.annotation) {
                context.annotation.showCancel = self.active_asset_annotations.length > 1;
            }
            
            Mustache.update(template_label, context, {
                pre: function (elt) { jQuery(elt).hide(); },
                post: function (elt) {
                    djangosherd.assetview.clipform.html.push('clipform-display', {
                        asset: {},
                        extra: { 'tools' : 'clipform-tools' }
                    });
                    jQuery('.annotation-active').removeClass('annotation-active');
                    
                    if (self.active_annotation) {
                        djangosherd.assetview.setState(self.active_annotation.annotation);
                        
                        djangosherd.assetview.clipform.setState(self.active_annotation.annotation,
                                { 'mode': context.annotation.editing ? 'edit' : 'browse' });
                        
                        jQuery('.annotation-listitem-' + self.active_annotation.id).addClass('annotation-active');
                    } else if (self.xywh) {
                        djangosherd.assetview.setState(self.xywh);
                        
                        if (djangosherd.assetview.clipform) {
                            djangosherd.assetview.clipform.setState(self.xywh, {'mode': 'create' });
                        }
                    } else {
                        // /#default initialization. no annotation defined.
                        // don't need to set state on clipstrip/form as there is no state
                        djangosherd.assetview.setState();
                        djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 }, { 'mode': 'create' });
                    }
                    
                    if (context.annotation && context.annotation.editing) {
                        jQuery("#annotations-organized").hide();
                    } else {
                        jQuery("#annotations-organized").show();
                    }
                    
                    jQuery(elt).fadeIn("slow");
                    
                    if (self.config.edit_state === "new") {
                        self.config.edit_state = "";
                        return self.newAnnotation();
                    }
                }
            });
        };
    })();

})();
