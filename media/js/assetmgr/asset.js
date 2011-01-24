function MediaThread(){}
MediaThread.templates = {};

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
		value:'Copy Clip'
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
        'asset-json':function(asset_id, with_annotations) {
            return '/asset/json/'+asset_id+(with_annotations ? '/?annotations=true' :'/');
        }
    }

    Mustache.Renderer.prototype.filters_supported['url'] = function(name,context,args) {
        var url_args = this.map(args,function(a){return this.get_object(a,context,this.context)},this);
        return MediaThread.urls[name].apply(this,url_args);
    }


    function AnnotationList(){}
    AnnotationList.prototype = {
        grouping: null,
        current_asset_id: null,
        //current_annotation
        //mock_mode -- from page state
        //storage
        init:function() {
            jQuery.ajax({
                url:'/site_media/templates/annotations.mustache',
                dataType:'text',
                success:function(text){
                    MediaThread.templates['annotations'] = Mustache.template('annotations',text);
                    
                }
            })
            return this;
        },
        GroupBy: function(grouping) {
            if (this.grouping == grouping) 
                return;
            if (!this.current_asset_id) 
                return;
            djangosherd.storage.get(
                {
                    id:this.current_asset_id,
                    type:'asset',
                    url:MediaThread.urls['asset-json'](this.current_asset_id,/*annotations=*/true)
                },
                false,
                function(asset_full) {
                    for (var i=0;i<asset_full.annotations.length;i++) {
                        var a = asset_full.annotations[i];
                        if (a.annotation) {
                            lay.add(a.annotation,{id:a.id});
                        }
                    }
                }
            );
        }
        ///Groupby('author')
        ///Groupby('tag')
        //  - get, group
        //  - replace/hide-show Layer, group-by color
        //  - decorate

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
        
        //decorateLink
        //decorateForm

    }
    

})();