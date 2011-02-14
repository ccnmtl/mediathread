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

        ////SETUP SOMEHOW!!!
        this.asset_id = null;
        this.global_annotation = {};//unused
        this.annotation_id = null;//unused

        //current_annotation
        //mock_mode -- from page state
        //storage
        this.init = function(config) {
            for (a in config) {
                //asset_id, annotation_id
                this[a] = config[a];
            }
            jQuery.ajax({
                url:'/site_media/templates/annotations.mustache?nocache=v2',
                dataType:'text',
                success:function(text){
                    MediaThread.templates['annotations'] = Mustache.template('annotations',text);
                    
                    Mustache.update('annotations-organized', {
                        'annotation':null,
                        'annotation_list':[]
                    })
                    //now that the form exists...
                    var frm = document.forms['annotation-list-filter'];

                    frm.elements['showall'].checked = hs_DataRetrieve('annotation-list-filter__showall');

                    jQuery(frm.elements['showall']).change(self.showHide);
                    jQuery(frm.elements['groupby']).change(function() {
                        self.GroupBy(jQuery(this).val());
                    });
                    self.GroupBy(jQuery(frm.elements['groupby']).val());
                    
                }
            })
            return this;
        }

        this.showHide = function() {
            var show = document.forms['annotation-list-filter'].elements['showall'].checked;
            hs_DataStore('annotation-list-filter__showall', show || '');
            if (show)
                self.layers[self.grouping].show()
            else
                self.layers[self.grouping].hide()
        }
        this.clearAnnotation = function(ann_id) {
            ///TODO: make this updateAnnotation(ann_id, obj)
            if (!ann_id) {
                if (this.annotation_id)
                    ann_id = this.annotation_id;
                else return;
            }
            for (a in this.layers) {
                this.layers[a].remove(ann_id);
            }
        }
        ///Groupby('author')
        ///Groupby('tag')
        //  - get, group
        //  - replace/hide-show Layer, group-by color
        //  - decorate
        this.GroupBy = function(grouping) {
            ///Do nothing if we can't or don't need to.
            if (this.grouping == grouping) 
                return;
            if (!this.asset_id) 
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
                        show:function(){}, hide:function(){}
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
            this.showHide();
            this.resetHighlightLayer();
            var color_by;

            switch (grouping) {
            case 'tag':
                color_by = function(ann,cats) {
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
                color_by = function(ann,cats) {
                    return [ann.metadata.author_name];
                }
                break;
            }
            
            djangosherd.storage.get(
                {
                    id:this.asset_id,
                    type:'asset',
                    url:MediaThread.urls['asset-json'](this.asset_id,/*annotations=*/true)
                },
                false,
                function(asset_full) {
                    var context = {'annotation_list':[]};
                    var cats = {};
                    var user_listing = false;
                    self.layers[grouping].removeAll();
                    DjangoSherd_Colors.reset(grouping);
                    for (var i=0;i<asset_full.annotations.length;i++) {
                        var ann = asset_full.annotations[i];
                        ///TODO: WILL BREAK when we ajax this
                        ann.active_annotation = (ann.id === self.annotation_id)
                        if (ann.metadata) {
                            var titles = color_by(ann);
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
                    Mustache.update('annotation-list',context,{post:function(elt){
                        jQuery('li.annotation-listitem',elt).each(self.decorateLink);
                    }});
                }
            );
        };

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

        ///Annotation Copy
        //  - get, clone, remove id, editable = true, replace

        ///Annotation Save
        //  - update list items
        //  - replace with 'new' annotation
        //
        ///Annotation Open
        //  - highlight on view
        //  - 
        ///Asset Save
        //  - storage.update

        
    })();
    

})();