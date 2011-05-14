/*
  function error(req) {  };
  function styleRelated(req) {
    res = req.responseText;
    
  };
  function foo(hrefs) {
    return A({'href':hrefs[0]}, IMG({'src':hrefs[1]}));
  };
  function parseRelated() {
    var related_links = eval($("metadata-related").innerHTML);
    var img_links = [];
    for( var i = 0; i < related_links.length; ++i ) {
      var link = related_links[i];
      var uid = link.substr(link.search("wgbh:"));
      var img_link = "http://openvaultresearch.wgbh.org:8080/fedora/get/"+uid+"/sdef:THUMBNAIL/get"
      img_links[img_links.length] = [link, img_link];
    };
    var div = DIV(null, map(foo, img_links));
    replaceChildNodes($("metadata-related"), div);
  };
  addLoadEvent(parseRelated);
*/
(function() {
    var global = this;

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
            'your-space':function(user_id) {
                return '/yourspace/'+user_id+'/asset/';
            },
            'asset-view':function(asset_id) {
                return '/asset/'+asset_id+'/';
            },
            'asset-json':function(asset_id, with_annotations) {
                return '/asset/json/'+asset_id+(with_annotations ? '/?annotations=true' :'/');
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


    // setup url rewriting for HTML5 && HTML4 browsers
    jQuery(window).bind("onpopstate", function(stateObj) {
        if (stateObj.state) {
            self._updateAnnotation(stateObj.annotation_id, "annotation-current");
        }
    });


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
            
            jQuery.ajax({
                url:'/site_media/templates/annotations.mustache?nocache=v2',
                dataType:'text',
                success:function(text){
                    MediaThread.templates['annotations'] = Mustache.template('annotations',text);
                    
                    if (config.asset_id) {
                        // Retrieve the full asset w/annotations from storage
                        // Do I need the full asset?
                        djangosherd.storage.get({
                                id:config.asset_id,
                                type:'asset',
                                url:MediaThread.urls['asset-json'](config.asset_id,/*annotations=*/true)
                            },
                            false,
                            function(asset_full) {
                                self.active_asset = asset_full.asset;
                                self.active_asset_annotations = asset_full.annotations;
                                var annotation_id = config.annotation_id;
                                
                                // parse out the annotation id in the hashtag (if it exists)
                                // hashtags override a urls embedded annotation_id
                                if (window.location.hash)
                                    annotation_id = window.location.hash.split("=")[1];
                                
                                self._updateAnnotation(annotation_id, "asset-annotations");
                                self._replaceHistory();
                                
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
            

            
            jQuery(window).bind("hashchange", function() {
                var asset_id = null;
                var annotation_id = null;
                
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
                if (window.location.hash)
                    annotation_id = window.location.hash.split("=")[1];

                window.AnnotationList._updateAnnotation(annotation_id, "annotation-current");
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
            if (this.grouping == grouping || !self.active_asset.id) 
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
                    var tags = ann.metadata.tags.split(/\s*,\s*/);
                    for (var i=0;i<tags.length;i++) {
                        //remove empty front tag
                        if (! /\w/.test(tags[i])) {
                            tags.splice(i,1);
                            --i;//set the counter back
                        }
                    }
                    if (tags.length) {
                        return tags
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
            self._updateAnnotation(annotation_id, "annotation-current");
            self._pushHistory();
        }
        
        ///Annotation Add Form
        //  - author == current_user
        this.newAnnotation = function() {
            var context = { 'annotation': {   
                'editable': true,
                'metadata': {
                  'author': { 'id': MediaThread.current_user },
                  'author_name': MediaThread.user_full_name
                },
                'range1': 0, // @todo -- null?
                'range2': 0 // @todo -- null?
            }};
            
            Mustache.update('annotation-current', context, { post:function(elt) {
                djangosherd.assetview.clipform.html.push('clipform-display', {
                    asset : {}
                });
                
                djangosherd.assetview.setState({});
                djangosherd.assetview.clipform.setState({ 'mode': 'create', 'start': 0, 'end': 0 });
            }});
        }
        
        ///Annotation Copy
        // - new annotation with properties of current annotation minus id
        this.copyAnnotation = function() {
            // Add template...but with all the properties of this annotation.
            var context = { 'annotation': {   
                    'editable': true,
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
                        asset : {}
                    });

                    djangosherd.assetview.setState(self.active_annotation.annotation);
                    djangosherd.assetview.clipform.setState({ 'mode': 'copy', 'start': self.active_annotation.range1, 'end': self.active_annotation.range2 });
                }
            }});
        }
        
        ///Annotation Save
        //  - update list items
        //  - replace with 'new' annotation
        this.saveAnnotation = function() {
            var frm = document.forms['edit-annotation-form'];

            // Push clipform state into local storage 
            // @todo -- this is clearly not the right place for this. Discuss with Sky. 
            // clipform > update > pushes to storage within .html. I think this is replaced by the new storage system?
            var obj = djangosherd.assetview.clipform.getState();
            if (obj.length > 0)
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
            
            var url = frm.elements['annotation_id'] ?
                url = MediaThread.urls['edit-annotation'](self.active_asset.id, self.active_annotation.id) : 
                url = MediaThread.urls['create-annotation'](self.active_asset.id);
            
            djangosherd.storage.set({ id: frm.elements['annotation_id'], 
                                      type: 'annotations',
                                      url: url,
                                      data: jQuery(frm).serialize() },
                                      function(data) {
                                          self.active_annotation = data.annotation;
                                          
                                          Mustache.update('annotation-current', data, { post:function(elt) {
                                              if (self.active_annotation) {
                                                  djangosherd.assetview.clipform.html.push('clipform-display', {
                                                      asset : {}
                                                  });

                                                  djangosherd.assetview.setState(self.active_annotation.annotation);
                                                  djangosherd.assetview.clipform.setState({ 'mode': 'copy', 'start': self.active_annotation.range1, 'end': self.active_annotation.range2 });
                                                  
                                                  jQuery('.annotation-active').removeClass('annotation-active');
                                                  jQuery('.annotation-listitem-' + self.active_annotation.id).addClass('annotation-active');
                                                  
                                                  //@todo -- saved messaging. something that fades out?
                                                  
                                                  self.updateAnnotationList();
                                              }
                                          }});
                                     });
        }
        
        // Push annotation_ids on the stack as a user views them.
        // If an annotation is missing (deleted?) -- revert to the asset view.
        this._pushHistory = function() {
            if (window.history.pushState) {
                var currentState = { annotation_id : self.active_annotation.id, asset_id: self.active_asset.id }
                if (self.active_annotation) {
                    window.history.pushState(currentState, self.active_annotation.title, "/asset/" + self.active_asset.id + "/annotations/" + self.active_annotation.id + "/");
                } else {
                    window.history.pushState(currentState, self.active_asset.title, "/asset/" + self.active_asset.id + "/");
                }
            } else if (self.active_annotation) {
                window.location.hash = "annotationid=" + self.active_annotation.id;
            } else {
                window.location.hash = '';
            }
        }
        
        // On an init -- replace the current history to ensure the information is on the stack
        this._replaceHistory = function() {
            if (window.history.replaceState) {
                var currentState = { asset_id: self.active_asset.id };
                if (self.active_annotation) {
                    currentState["annotation_id"] = current_state.active_annotation.id;
                    window.history.replaceState(currentState, self.active_annotation.title, "/asset/" + self.active_asset.id + "/annotations/" + self.active_annotation.id + "/");
                } else {
                    window.history.replaceState(currentState, self.active_asset.title, "/asset/" + self.active_asset.id + "/");
                }
            } else {
                // @todo -- hashtag implementation
            }
        }
        
        this._updateAnnotation = function(annotation_id, template_label) {
            self.active_annotation = null;
            
            if (annotation_id)
                annotation_id = parseInt(annotation_id);
            
            for (var i=0;i< self.active_asset_annotations.length;i++) {
                var ann = self.active_asset_annotations[i];
                if (ann.id === annotation_id) {
                    self.active_annotation = ann;
                }
            }
            
            var context = { 'annotation': self.active_annotation };
            Mustache.update(template_label, context, { post:function(elt) {
                djangosherd.assetview.clipform.html.push('clipform-display', { asset : {} });
                
                if (self.active_annotation) {
                    djangosherd.assetview.setState(self.active_annotation.annotation);
                    
                    var mode = self.active_annotation.editable ? 'edit' : 'browse';
                    djangosherd.assetview.clipform.setState({ 'mode': mode, 'start': self.active_annotation.range1, 'end': self.active_annotation.range2 });
    
                    jQuery('.annotation-active').removeClass('annotation-active');
                    jQuery('.annotation-listitem-' + self.active_annotation.id).addClass('annotation-active');
                } else {
                    djangosherd.assetview.setState(null);
                }
            }});
        }

    })();

})();
