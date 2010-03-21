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
	    clip_form.elements[a].disabled = false;
	}
	removeElement('copy-annotation');
	$('disableform').id = 'previously-disabled-form';
    }

    function validateNoteForm(mochi_evt) {
	var form = mochi_evt.src();
	var tag_field = form.elements['annotation-tags'];
	if (tag_field) {//is this null?
	    var tags = tag_field.value.split(',');
	    for (var i=0;i<tags.length;i++) {
		if (tags[i].length > 50) {
		    alert('You are trying to add a tag with greater than the maximum 50 character-limit.  Be sure to separate your tags with commas.  Also, tags are best used as single words that you would tag other assets with.  Try using the Notes field for longer expressions.');
		    mochi_evt.stop();
		    return;
		}
	    }
	}
    }

    addLoadEvent(function(){
	///Clip form disabling
	clip_form = document.forms['clip-form'];
	if ($('disableform')!=null) {
	    var elts = clip_form.elements;
	    for (a in FIELDS_TO_DISABLE) {
	        if (elts[a].type == 'textarea') {
	            elts[a].readOnly = true; // IE
	            elts[a].readonly = "readonly";
	        } else {
	            elts[a].disabled = true;
	        }
	    }
	    var copy_btn = INPUT({
		type:'button',
		id:'copy-annotation',
		onclick:'copyAnnotation()',
		value:'Copy Clip'
	    });
	    clip_form.appendChild(copy_btn);
	}
	///delete comment on focus
	forEach(document.getElementsByTagName('input'),
		function(elt) {
		    if (elt.name == 'comment') {
			connect(elt,'onfocus',function(evt) {
			    if (evt.src().value=='Enter your comment here and press return') {
				evt.src().value = '';
			    }
			});
		    }
		});
	///validate notes
	if (clip_form) {
	    connect(clip_form,'onsubmit',validateNoteForm);
	} 
	var noteform = document.forms['not-clip-form'];
	if (noteform) {
	    connect(noteform,'onsubmit',validateNoteForm);
	}
	
    });

})();