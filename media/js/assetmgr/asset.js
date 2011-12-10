(function() {
    var global = this;
    
    _propertyCount = function(obj) {
        var count = 0;
        for (k in obj) if (obj.hasOwnProperty(k)) count++;
        return count;
    }

    ///MUSTACHE CODE
    if (window.Mustache) {
        Mustache.set_pragma_default('EMBEDDED-PARTIALS',true);
        Mustache.set_pragma_default('FILTERS',true);
        Mustache.set_pragma_default('DOT-SEPARATORS',true);
        Mustache.set_pragma_default('?-CONDITIONAL',true);
        
        MediaThread.urls = {
            'annotation-form':function(asset_id,annotation_id) {
                return '/asset/'+asset_id+'/annotations/'+annotation_id;
            },
            'home-space':function(username) {
                return '/?username='+username;
            },
            'your-space':function(username, tag, modified) {
                return '/yourspace/'+username+'/asset/?annotations=true' + (tag ? '&tag=' + tag : '') + (modified ? '&modified=' + modified : '');
            },
            'all-space':function(tag, modified) {
                return '/yourspace/all/asset/?' + (tag ? '&tag=' + tag : '') + (modified ? '&modified=' + modified : '');
            },
            'asset-delete':function(username, asset_id) {
                return '/yourspace/'+username+'/asset/'+asset_id+ '/?delete';
            },
            'annotation-delete':function(asset_id, annotation_id) {
                return '/asset/'+asset_id+'/annotations/'+annotation_id+'/?delete';
            },
            'asset-view':function(asset_id) {
                return '/asset/'+asset_id+'/';
            },
            'asset-json':function(asset_id, with_annotations) {
                return '/asset/json/'+asset_id+(with_annotations ? '/?annotations=true' :'/');
            },
            'assets':function(username, with_annotations) {
                return '/annotations/'+(username ? username+'/' : '');
            },
            'create-annotation':function(asset_id) {
                // a.k.a. server-side annotation-containers
                return '/asset/'+asset_id+'/annotations/';
            },
            'edit-annotation':function(asset_id,annotation_id) {
                // a.k.a server-side annotation-form assetmgr:views.py:annotationview
                return '/asset/'+asset_id+'/annotations/'+annotation_id+'/';
            }
        }

        Mustache.Renderer.prototype.filters_supported['url'] = function(name,context,args) {
            var url_args = this.map(args,function(a){return this.get_object(a,context,this.context)},this);
            return MediaThread.urls[name].apply(this,url_args);
        }
        Mustache.Renderer.prototype.filters_supported['default'] = function(name,context,args) {
            var lookup = this.get_object(name,context,this.context);
            if (lookup) return lookup
            else return args[0];
        }
    }//END MUSTACHE CODE

    window.CollectionList = new (function CollectionListAbstract() {
        var self = this;
                
        this.init = function(config) {
            self.template_label = config.template_label;
            self.view_callback = config.view_callback;
            self.create_annotation_thumbs = config.create_annotation_thumbs;
            
            jQuery.ajax({
                url:'/site_media/templates/' + config.template + '.mustache?nocache=v2',
                dataType:'text',
                cache: false, // Chrome && Internet Explorer has aggressive caching policies.
                success:function(text) {
                    MediaThread.templates[config.template] = Mustache.template(config.template,text);
                    // Retrieve the full asset w/annotations from storage
                    if (config.view == 'all' || !config.space_owner) {
                        url = MediaThread.urls['all-space'](config.tag)
                    } else {
                        url = MediaThread.urls['your-space'](config.space_owner, config.tag)
                    }  
                    djangosherd.storage.get({
                            type:'asset',
                            url: url
                        },
                        false,
                        function(your_records) {
                            self._updateAssets(your_records);
                        });
                    }
                });
        }

        this.selectOwner = function(username) {
            djangosherd.storage.get({
                type:'asset',
                url: username ? MediaThread.urls['your-space'](username) : MediaThread.urls['all-space']()
            },
            false,
            function(the_records) {
                self._updateAssets(the_records);
            });
            
            return false;
        }
        
        this.deleteAsset = function(asset_id) {
            var url = MediaThread.urls['asset-delete'](self.current_records.space_viewer.username, asset_id);
            return ajaxDelete(null, 'record-' + asset_id, { 'href': url });
        }
        
        this.deleteAnnotation = function(annotation_id) {
            var asset_id = jQuery('#annotation-' + annotation_id).parents("div.record").children("input.record").attr("value");
            var url = MediaThread.urls['annotation-delete'](asset_id, annotation_id);
            return ajaxDelete(null, 'annotation-' + annotation_id, { 'href': url });
        }
        
        this.clearFilter = function(filterName) {
            var active_tag = null;
            var active_modified = null;
                
            if (filterName == 'tag')
                active_modified = ('modified' in self.current_records.active_filters) ? self.current_records.active_filters.modified : null;
            else if (filterName == 'modified')
                active_tag = ('tag' in self.current_records.active_filters) ? self.current_records.active_filters.tag : null;
            
            djangosherd.storage.get({
                type:'asset',
                url: self.getSpaceUrl(active_tag, active_modified)
            },
            false,
            function(your_records) {
                self._updateAssets(your_records);
            });
            
            return false;
        }
        
        this.filterByDate = function(modified) {
            var active_tag = ('tag' in self.current_records.active_filters) ? self.current_records.active_filters.tag : null;
            djangosherd.storage.get({
                type:'asset',
                url:self.getSpaceUrl(active_tag, modified)
            },
            false,
            function(your_records) {
                self._updateAssets(your_records);
            });
            
            return false;
        }
        
        this.filterByTag = function(tag) {
            var active_modified = ('modified' in self.current_records.active_filters) ? self.current_records.active_filters.modified : null;
            djangosherd.storage.get({
                type:'asset',
                url:self.getSpaceUrl(tag, active_modified)
            },
            false,
            function(your_records) {
                self._updateAssets(your_records);
            });
            
            return false;
        }

        this.getShowingAllItems = function(json) {
            return !json.hasOwnProperty('space_owner'); 
        }
        
        this.getSpaceUrl = function(active_tag, active_modified) {
           if (self.getShowingAllItems(self.current_records))
                return MediaThread.urls['all-space'](active_tag, active_modified)
           else
                return MediaThread.urls['your-space'](self.current_records.space_owner.username, active_tag, active_modified)
        }
        
        this.createThumbs = function(assets) {
            for (var i = 0; i < assets.length; i++) {
                var asset = assets[i];
                DjangoSherd_adaptAsset(asset); //in-place
                if (asset.thumbable) {
                    for (var j = 0; j < asset.annotations.length; j++) {
                        ann = asset.annotations[j];
                        
                        var view;
                        switch(asset.type) {
                        case 'image':
                            view = new Sherd.Image.OpenLayers();
                            break;
                        case 'fsiviewer':
                            view = new Sherd.Image.FSIViewer();
                            break;
                        }
                        djangosherd.thumbs.push(view);
                        var obj_div = document.createElement('div');
                        obj_div.setAttribute('class','thumb');
        
                        var target_div = document.getElementById("annotation-thumb-" + ann.id);
                        target_div.appendChild(obj_div);
                        // should probably be in .view
                        asset.presentation = 'thumb';

                        ann.asset = asset;
                        view.html.push(obj_div, ann);
                        view.setState(ann.annotation);
                    }
                }
            }
        }
        
        this._updateAssets = function(your_records) {
            self.current_records = your_records;
            
            if (self.getShowingAllItems(your_records)) {
                your_records.selected_label = "All Class Members";
                your_records.showing_all_items = true;
            } else if (your_records.space_owner.username == your_records.space_viewer.username) {
                your_records.selected_label = "Me";
                your_records.showing_my_items = true;
            } else {
                your_records.selected_label = your_records.space_owner.public_name;
            }
            
            n = _propertyCount(your_records.active_filters);
            if (n > 0)
                your_records.active_filter_count = n;
            
            Mustache.update(self.template_label, your_records, { post:function(elt) {
                    if (self.create_annotation_thumbs)
                        self.createThumbs(your_records.assets);
                    
                    if (self.view_callback) 
                        self.view_callback();
                } 
            });
        }
    })();

    window.AnnotationList = new (function AnnotationListAbstract(){
        var self = this;
        
        //active_annotation
        //mock_mode -- from page state
        //storage
        this.init = function(config) {
            this.layers = {}; //should we really store layers here?
            this.grouping = null;
            this.highlight_layer = null;

            this.active_annotation = null;
            this.active_asset = null;
            this.active_asset_annotations = null;
            this.config = config;
            
            jQuery("#edit-item-form").submit(function() {
                return self.saveItem();
            });
            
            window.onbeforeunload = config.level == "item" ? this.saveItemPrompt : null;

            jQuery.ajax({
                url:'/site_media/templates/annotations.mustache?nocache=v2',
                dataType:'text',
                cache: false, // Chrome && Internet Explorer has aggressive caching policies.
                success:function(text){
                    MediaThread.templates['annotations'] = Mustache.template('annotations',text);
                    
                    if (config.asset_id) {
                        // Retrieve the full asset w/annotations from storage
                        djangosherd.storage.get({
                                id:config.asset_id,
                                type:'asset',
                                url:MediaThread.urls['asset-json'](config.asset_id,/*annotations=*/true)
                            },
                            false,
                            function(asset_full) {
                                var theAsset;
                                for (var key in asset_full.assets) {
                                    theAsset = asset_full.assets[key];
                                    break;
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
            
                                frm.elements['showall'].checked = hs_DataRetrieve('annotation-list-filter__showall');
                                jQuery(frm.elements['groupby']).val(hs_DataRetrieve('annotation-list-filter__group')
                                                                    || 'author');
            
                                jQuery(frm.elements['showall']).change(self.showHideAnnotations);
                                jQuery(frm.elements['groupby']).change(function() {
                                    var val = jQuery(this).val();
                                    hs_DataStore('annotation-list-filter__group', val);
                                    self.groupBy(val);
                                });
                                self.groupBy(jQuery(frm.elements['groupby']).val());
                        });
                    }
                }
            });
            
            // setup url rewriting for HTML5 && HTML4 browsers
            jQuery(window).bind("popstate", function(event) {
                if (event.originalEvent.state) {
                    window.AnnotationList._update({ 'annotation_id': event.originalEvent.state.annotation_id }, "annotation-current");
                }
            });
            
            jQuery(window).bind("hashchange", function() {
                var asset_id = null;
                var annotation_id = null;
                var xywh = null;
                
                // parse out parameters on the command line
                var params = window.location.pathname.split('/');
                for (var i=0; i < params.length; i++) {
                    var prev = i-1;
                    if (prev > -1) {
                        if (params[prev] == 'asset') {
                            asset_id = params[i];
                        } else if (params[prev] == 'annotations') {
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

        this.showHideAnnotations = function() {
            var show = document.forms['annotation-list-filter'].elements['showall'].checked;
            hs_DataStore('annotation-list-filter__showall', show || '');
            if (show)
                self.layers[self.grouping].show()
            else
                self.layers[self.grouping].hide()
        }
        
        ///Groupby('author')
        ///Groupby('tag')
        //  - get, group
        //  - replace/hide-show Layer, group-by color
        //  - decorate
        this.groupBy = function(grouping) {
            ///Do nothing if we can't or don't need to.
            if (this.grouping == grouping || !(self.active_asset && self.active_asset.id)) 
                return;

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
                        removeAll:function(){},
                        add:function(){},
                        remove:function(){},
                        show:function(){}, 
                        hide:function(){}
                    }
                } else {
                    this.layers[grouping].create(grouping,{
                        //onclick:function(feature) {},
                        title:' ',//hide grouping title for the video view
                        onmouseenter:function(id, name) {
                            self.highlight(id);
                        },// */
                        onmouseleave:function(id, name) {
                            self.unhighlight();
                        },
                        zIndex:300 //above highlight
                    });
                }
            }
            this.grouping = grouping;
            this.showHideAnnotations();
            this.resetHighlightLayer();

            switch (grouping) {
            case 'tag':
                this.layers[grouping].color_by = function(ann) {
                    if (ann.metadata.tags.length) {
                        var tags = [];
                        for (var k=0; k < ann.metadata.tags.length; k++)
                            tags.push(ann.metadata.tags[k].name);
                        return tags;
                    } else {
                        //127 ensures that None is last
                        return [String.fromCharCode(127)+'(None)']
                    }
                }
                break;
            case 'author':
                this.layers[grouping].color_by = function(ann) {
                    return [ann.metadata.author_name];
                }
                break;
            }

            self.updateAnnotationList();
        }
        
        this.updateAnnotationList = function() {
            djangosherd.storage.get({
                id:self.active_asset.id,
                type:'asset',
                url:MediaThread.urls['asset-json'](self.active_asset.id,/*annotations=*/true)
            },
            false,
            function(asset_full) {
                var grouping = self.grouping;
                var context = {'annotation_list':[]};
                var cats = {};
                var user_listing = false;
                self.layers[grouping].removeAll();
                DjangoSherd_Colors.reset(grouping);
                for (var i=0;i<asset_full.annotations.length;i++) {
                    var ann = asset_full.annotations[i];
                    ///TODO: WILL BREAK when we ajax this
                    if (self.active_annotation)
                        ann.active_annotation = (ann.id === self.active_annotation.id)
                    if (ann.metadata) {
                        var titles = self.layers[grouping].color_by(ann);
                        for (var j=0;j<titles.length;j++) {
                            var title = titles[j];
                            var color = DjangoSherd_Colors.get(title);
                            /// add the annotation onto the layer in the right color
                            if (ann.annotation) {
                                self.layers[grouping].add(
                                    ann.annotation,{'id':ann.id,
                                                    'color':color
                                                   }
                                );
                            }
                            ///..and setup the category for the AnnotationList
                            if (!cats[title]) {
                                cats[title] = {'title':title,
                                               'color':color,
                                               'annotations':[]
                                              };
                                if (title && title == MediaThread.user_full_name) {
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
                
                for (var i=0;i<context.annotation_list.length;i++) {
                    context.annotation_list[i] = {'category':cats[context.annotation_list[i]]};
                }
                
                Mustache.update('annotation-list', context, { post:function(elt) {
                    jQuery('li.annotation-listitem',elt).each(self.decorateLink);
                }});
            });
        }
        
        this.resetHighlightLayer = function() {
            if (this.highlight_layer) {
                this.highlight_layer.destroy();
            }
            this.highlight_layer = djangosherd.assetview.layer();
            if (this.highlight_layer) {
                this.highlight_layer.create('focus',{zIndex:200,title:' '});
            }
        }
        
        this.unhighlight = function() {
            if (self.highlighted_nodes) {
                jQuery(self.highlighted_nodes).removeClass('highlight');
            }
            if (self.highlight_layer) {
                self.highlight_layer.removeAll();
            } else {
                self.resetHighlightLayer();
            }
        }

        this.highlight = function(ann_id) {
            self.unhighlight();
            //highlight on list
            self.highlighted_nodes = jQuery('.annotation-listitem-'+ann_id).addClass('highlight').toArray()

            if (self.highlight_layer) {
                djangosherd.storage.get({
                    'id':ann_id,
                    'type':'annotations'
                }, function(ann) {
                    self.highlight_layer
                        .add(ann.annotation,{id:ann.id,
                                             color:'black',
                                             bgcolor:'highlight',
                                             pointerEvents:'none',
                                             zIndex:1
                                            });
                });
            }//end if (self.highlight_layer)
        }//end function highlight()


        this.decorateLink = function(li) {
            if (self.highlight_layer) {
                jQuery(this)
                .mouseenter(function(evt) {
                    self.highlight(jQuery(this).attr('data-id'));
                })
                .mouseleave(function(evt) {
                    self.unhighlight();
                })
            }
        }
        //decorateForm 
        
        this.showAnnotation = function(annotation_id) {
            self._update( { 'annotation_id': annotation_id }, "annotation-current");
            self._addHistory(/*replace=*/false);
        }
        
        this.cancelAnnotation = function() {
            var annotation_id = self.active_annotation ? self.active_annotation.id : null;
            self._update({ 'annotation_id' : annotation_id }, "annotation-current");
            jQuery("#annotations-organized").show();
        }
        
        ///Annotation Add Form
        //  - author == current_user
        this.newAnnotation = function() {
            var context = { 'annotation': {   
                'editing': true,
                'showCancel': true,
                'metadata': {
                  'author': { 'id': MediaThread.current_user },
                  'author_name': MediaThread.user_full_name
                }
            }};
            
            Mustache.update('annotation-current', context, { post:function(elt) {
                djangosherd.assetview.clipform.html.push('clipform-display', {
                    asset : {},
                    extra : { 'tools' : 'clipform-tools' }
                });
                
                djangosherd.assetview.setState({});
                djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 }, { 'mode': 'create' });
                jQuery("#annotations-organized").hide();
            }});
        }
        
        ///Annotation Edit
        // - new annotation with properties of current annotation minus id
        this.editAnnotation = function() {
            self._update( { 'annotation_id': self.active_annotation.id, 'editing': true }, "annotation-current");
            return false;
        }
        
        ///Annotation Copy
        // - new annotation with properties of current annotation minus id
        this.copyAnnotation = function() {
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
            
            Mustache.update('annotation-current', context, { post:function(elt) {
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
        }
        
        ///Item Save
        this.saveItem = function() {
            var frm = document.forms['edit-item-form'];
            if (frm.elements['annotation-tags'].value == "" && frm.elements['annotation-body'].value == "") {
                alert("Please specify tags and notes before saving.");
                frm.elements['annotation-tags'].focus();
                return false;
            } else {
                window.onbeforeunload = null;
                return true;
            }
        }
        
        ///Item Save Prompt
        this.saveItemPrompt = function() {
            var frm = document.forms['edit-item-form'];
            if (frm.elements['annotation-tags'].value == "" && frm.elements['annotation-body'].value == "") {
                // @todo -- switch selected tab back to Item
                frm.elements['annotation-tags'].focus();
                return "Save tags and notes to place this item in your collection.";
            }
        }
        
        ///Annotation Save
        //  - update list items
        //  - replace with 'new' annotation
        this.saveAnnotation = function() {
            var frm = document.forms['edit-annotation-form'];

            // Push clipform or assetview state into "local storage", i.e. the form that is posted to the server.
            // @todo -- Unsure if this is the best spot for this...
            var obj = djangosherd.assetview.clipform.getState();
            if (_propertyCount(obj) > 0)
                djangosherd.assetview.clipform.storage.update(obj, true);
            else
                obj = djangosherd.assetview.getState();
                if (_propertyCount(obj) > 0)
                    djangosherd.assetview.clipform.storage.update(obj, true);
            
            // Validate the tag fields...should be in djangosherd?
            var tag_field = frm.elements['annotation-tags'];
            if (tag_field) {//is this null?
                var tags = tag_field.value.split(',');
                for (var i=0;i<tags.length;i++) {
                    if (tags[i].length > 50) {
                        alert('You are trying to add a tag with greater than the maximum 50 character-limit.  Be sure to separate your tags with commas.  Also, tags are best used as single words that you would tag other assets with.  Try using the Notes field for longer expressions.');
                        return;
                    }
                }
            }
            
            if (frm.elements['annotation-title'].value == '') {
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
                success: function(json, textStatus, jqXHR) {
                    // Repopulate the cache & refresh the annotation view
                    // @todo -- if asset_json could be moved over to djangosherd:views.py, 
                    // then create_annotation, edit_annotation could just return the full asset json
                    // And eliminate this extra call.
                    djangosherd.storage.get({
                        id: json.asset.id,
                        type:'asset',
                        url:MediaThread.urls['asset-json'](json.asset.id,/*annotations=*/true)
                    },
                    false,
                    function(asset_full) {
                        var theAsset;
                        for (var key in asset_full.assets) {
                            theAsset = asset_full.assets[key];
                            break;
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
        }
        
        // Push annotation_ids on the history stack as a user views them.
        // If an annotation is missing (deleted?) -- revert to the asset view.
        // HTML 5.0 browsers: https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history
        // < HTML 5.0 browsers: Hashtag implementation
        this._addHistory = function(replace) {
            if (window.history.pushState) {
                var action = replace ? window.history.replaceState : window.history.pushState;
                var currentState = { asset_id: ((self.active_asset)?self.active_asset.id:self.config.asset_id) };
                if (self.active_annotation) {
                    currentState["annotation_id"] = self.active_annotation.id;
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
        }

        this._update = function(config, template_label) {
            // Set the active annotation
            self.active_annotation = null;
            self.xywh = null;
            
            var context = {};
            
            if (config.annotation_id) {
                var annotation_id = parseInt(config.annotation_id);
            
                for (var i=0;i< self.active_asset_annotations.length;i++) {
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
            } else if (self.active_asset_annotations.length <= 1) {
                context.annotation = {   
                    'editing': true,
                    'metadata': {
                      'author': { 'id': MediaThread.current_user },
                      'author_name': MediaThread.user_full_name
                    }
                };
            }
            
            context.showNewAnnotation = !context.annotation || (context.annotation && !context.annotation.editing);
            
            if (context.annotation)
                context.annotation.showCancel = self.active_asset_annotations.length > 1; 
            
            Mustache.update(template_label, context, { post:function(elt) {
                djangosherd.assetview.clipform.html.push('clipform-display', { 
                    asset : {},
                    extra : { 'tools' : 'clipform-tools' } 
                });
                jQuery('.annotation-active').removeClass('annotation-active');
                
                if (self.active_annotation) {
                    djangosherd.assetview.setState(self.active_annotation.annotation);
                    
                    djangosherd.assetview.clipform.setState(self.active_annotation.annotation, 
                            { 'mode': context.annotation.editing ? 'edit' : 'browse' });
                    
                    jQuery('.annotation-listitem-' + self.active_annotation.id).addClass('annotation-active');
                } else if (self.xywh) {
                    djangosherd.assetview.setState(self.xywh);
                    
                    if (djangosherd.assetview.clipform)
                        djangosherd.assetview.clipform.setState(self.xywh, {'mode': 'create' });
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
            }});
        }
    })();

})();
