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
    var FIELDS_TO_DISABLE = {
	'annotation-title':true,
	'annotation-tags':true,
	'annotation-body':true,
	'save-clip-annotation':true
    }

    var clip_form = null;
    //enable form to 'copy' the annotation
    global.copyAnnotation = function copyAnnotation() {
	for (a in FIELDS_TO_DISABLE) {
       if (clip_form.elements[a].type == 'textarea') {
           clip_form.elements[a].readOnly = false; // IE
           clip_form.elements[a].readonly = "";
        } else {
            clip_form.elements[a].disabled = false;
        }
	}
	jQuery('#copy-annotation').remove();
	jQuery('#disableform').attr('id','previously-disabled-form');
    }

    function validateNoteForm(evt) {
	var form = this;//jQuery
	var tag_field = form.elements['annotation-tags'];
	if (tag_field) {//is this null?
	    var tags = tag_field.value.split(',');
	    for (var i=0;i<tags.length;i++) {
		if (tags[i].length > 50) {
		    alert('You are trying to add a tag with greater than the maximum 50 character-limit.  Be sure to separate your tags with commas.  Also, tags are best used as single words that you would tag other assets with.  Try using the Notes field for longer expressions.');
		    evt.preventDefault();
		    return;
		}
	    }
	}
    }

    jQuery(function(){
	///Clip form disabling
	clip_form = document.forms['clip-form'];
	if (document.getElementById('disableform')!=null) {
	    var elts = clip_form.elements;
	    for (a in FIELDS_TO_DISABLE) {
	        if (elts[a].type == 'textarea') {
	            elts[a].readOnly = true; // IE
	            elts[a].readonly = "readonly";
	        } else {
	            elts[a].disabled = true;
	        }
	    }
	    var copy_btn = document.createElement('input');

            var copy_attrs = {
		type:'button',
		id:'copy-annotation',
		onclick:'copyAnnotation()',
		value:'Copy'
	    };
            for (a in copy_attrs) {
                copy_btn.setAttribute(a,copy_attrs[a]);
            }
	    clip_form.appendChild(copy_btn);
	}
	///validate notes
        jQuery(clip_form).bind('submit',validateNoteForm);
        jQuery(document.forms['not-clip-form']).bind('submit',validateNoteForm);
    });

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


    window.AnnotationList = new (function AnnotationListAbstract(){
        var self = this;
        this.layers = {}; //should we really store layers here?
        this.grouping = null;
        this.highlight_layer = null;

        this.asset_id = null;
        this.annotation_id = null;
        //this.global_annotation = {};//unused
        
        // populated objects
        this.active_annotation = null;
        this.active_asset = null;

        //active_annotation
        //mock_mode -- from page state
        //storage
        this.init = function(config) {
            for (a in config) {
                // @todo -- where does this come from?
                this[a] = config[a]; //asset_id, annotation_id
            }
            jQuery.ajax({
                url:'/site_media/templates/annotations.mustache?nocache=v2',
                dataType:'text',
                success:function(text){
                    MediaThread.templates['annotations'] = Mustache.template('annotations',text);
                    
                    if (self.asset_id) {
                        // Retrieve the full asset w/annotations from storage
                        // Do I need the full asset?
                        djangosherd.storage.get({
                                id:self.asset_id,
                                type:'asset',
                                url:MediaThread.urls['asset-json'](self.asset_id,/*annotations=*/true)
                            },
                            false,
                            function(asset_full) {
                                self.active_asset = asset_full;
                                self.setActiveAnnotation(self.annotation_id); 
                    
                                // Update the annotation add/edit form with the active_annotation
                                var context = { 'annotation': self.active_annotation };
                                Mustache.update('asset-annotations', context, { post:function(elt) {
                                    if (self.active_annotation) {
                                        // push the clipform into the template
                                        // @todo verify this is all cool with Sky
                                        djangosherd.assetview.clipform.html.push('clipform-display', {
                                            asset : {}
                                        });
                                    }
                                }});
                                
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
            if (/#whole-form/.test(document.location.hash)) {
                showWholeForm();
            }
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
            if (this.grouping == grouping || !this.asset_id) 
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
                id:this.asset_id,
                type:'asset',
                url:MediaThread.urls['asset-json'](this.asset_id,/*annotations=*/true)
            },
            false,
            function(asset_full) {
                var grouping = self.grouping;
                var context = {'annotation_list':[]};
                var cats = {};
                var user_listing = false;
                self.active_asset = asset_full; // @todo -- necessary?
                self.layers[grouping].removeAll();
                DjangoSherd_Colors.reset(grouping);
                for (var i=0;i<asset_full.annotations.length;i++) {
                    var ann = asset_full.annotations[i];
                    ///TODO: WILL BREAK when we ajax this
                    ann.active_annotation = (ann.id === self.annotation_id)
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
            self.setActiveAnnotation(annotation_id);
            
            var context = { 'annotation': self.active_annotation };
            Mustache.update('annotation-current', context, { post:function(elt) {
                if (self.active_annotation) {
                    djangosherd.assetview.clipform.html.push('clipform-display', {
                        asset : {}
                    });

                    djangosherd.assetview.clipform.setState({ 'start': self.active_annotation.range1, 'end': self.active_annotation.range2 });
                }
            }});
            
            jQuery('.annotation-active').removeClass('annotation-active');
            jQuery('.annotation-listitem-'+annotation_id).addClass('annotation-active');
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
                
                djangosherd.assetview.clipform.setState({ 'start': 0, 'end': 0 });
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

                    djangosherd.assetview.clipform.setState({ 'start': self.active_annotation.range1, 'end': self.active_annotation.range2 });
                }
            }});
        }
        
        ///Annotation Save
        //  - update list items
        //  - replace with 'new' annotation
        this.saveAnnotation = function() {
            // Push clipform state into local storage 
            // @todo -- this is clearly not the right place for this. Discuss with Sky. 
            // clipform > update > pushes to storage within .html. I think this is replaced by the new storage system?
            var obj = djangosherd.assetview.clipform.getState();
            djangosherd.assetview.clipform.storage.update(obj, true);
            
            var frm = document.forms['edit-annotation-form'];
            
            var url = frm.elements['annotation_id'] ?
                url = MediaThread.urls['edit-annotation'](this.asset_id, this.annotation_id) : 
                url = MediaThread.urls['create-annotation'](this.asset_id);
            
            djangosherd.storage.set({ id: frm.elements['annotation_id'], 
                                      type: 'annotations',
                                      url: url,
                                      data: jQuery(frm).serialize() },
                                     function(data) {
                                          self.asset_id = data.asset.id;
                                          self.annotation_id = data.annotation.id;
                                          self.active_annotation = data.annotation;
                                          
                                          Mustache.update('annotation-current', data);
                                          
                                          jQuery('.annotation-active').removeClass('annotation-active');
                                          jQuery('.annotation-listitem-' + self.annotation_id).addClass('annotation-active');
                                          
                                          //@todo -- saved messaging. something that fades out?
                                          
                                          self.updateAnnotationList();
                                     });
        }
        
        ///Annotation Cancel
        //  - revert any outstanding changes. Close add form if open.
        this.cancelAnnotation = function() {
            var context = { 'annotation': self.active_annotation };
            Mustache.update('annotation-current', context, { post:function(elt) {
                if (self.active_annotation) {
                    
                    djangosherd.assetview.clipform.html.push('clipform-display', {
                        asset : {}
                    });
                    
                    djangosherd.assetview.clipform.setState({ 'start': self.active_annotation.range1, 'end': self.active_annotation.range2 });
                }
            }});
        }
        
        this.setActiveAnnotation = function(annotation_id) {
            self.annotation_id = annotation_id;
            for (var i=0;i< self.active_asset.annotations.length;i++) {
                var ann = self.active_asset.annotations[i];
                if (ann.id === self.annotation_id) {
                    self.active_annotation = ann;
                }
            }
        }
        
    })();

})();


// @todo -- is the whole/portion concept going away?
function showWholeForm() {
    jQuery('#portion-asset-form').hide();
    jQuery('#whole-asset-form').show();
    jQuery(document.forms['clip-type'].elements['clipType']).each(function() {
        if (this.value == 'Whole') this.checked = true;
    });
}

function showPortionForm() {
    jQuery('#whole-asset-form').hide();
    jQuery('#portion-asset-form').show();
    jQuery(document.forms['clip-type'].elements['clipType']).each(function() {
        if (this.value == 'Portion') this.checked = true;
    });
}
