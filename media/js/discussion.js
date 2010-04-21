addLoadEvent(function discussion_init() {
    var next_response_loc = false;
    var frm = $('comment-form');

    function open_comment_form(evt) {
        var respond = evt.src();
        frm.elements['parent'].value = respond.getAttribute("data-comment");
        if (!next_response_loc) {
	    next_response_loc = respond;
            respond.nextSibling.appendChild(frm);
            showElement(frm);
            $('id_comment').focus();
            tinyMCE.execCommand("mceAddControl", false, "id_comment");
            } else {
		if (next_response_loc == respond) {
		    next_response_loc = false;
		} else {
                    next_response_loc = respond;
		}
                tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
                tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
            }
    }

    function hide_comment_form() {
        next_response_loc = false;
        tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
        tinyMCE.execCommand("mceRemoveControl", false, "id_comment");
    }

    forEach($$('.respond_prompt'), function(elt) {
        connect(elt,'onclick', open_comment_form);
    });

    tinyMCE.onRemoveEditor.add(function(manager, ed) {
        //logDebug("third focus");
	if (next_response_loc) {
            next_response_loc.nextSibling.appendChild(document.forms[0]);
            tinyMCE.execCommand("mceAddControl", false, "id_comment");
	} else {
            hideElement('comment-form');
	}
    });
    tinyMCE.onAddEditor.add(function(manager, ed) {
        ed.onInit.add(function(editor) {
            tinyMCE.execCommand("mceFocus", false, "id_comment");//win.document is null
        });
    });

    if (window.djangosherd) {
        djangosherd.onOpenCitation = function(id,ann_obj,options,targets) {
            if (targets.top == 'videoclipbox') {
                updateVerticalHeight(null,{'materials':260});
            }
        }
    }

function AjaxComment(form) {
    this.form = form;
    this.username = $('logged_in_name').textContent;

    connect(form,'onsubmit',this, 'submit');
    
}

AjaxComment.prototype.submit = function(evt) {
    tinyMCE.triggerSave();
    evt.preventDefault();
    var form_val_array = formContents(this.form);

    var def = doXHR(this.form.action,
        {method:'POST',
        sendContent:queryString(form_val_array),
        headers:[["Content-type","application/x-www-form-urlencoded"]]
        }
                   );
    //frm.elements['timestamp'].value = '';
    //frm.elements['security_hash'].value = '';
    def.addBoth(bind(this.oncomplete,this,form_val_array),
                this.onfail);
}
var sky;
AjaxComment.prototype.oncomplete = function(form_val_array, func, xhr) {
    var form_vals = {};
    for (var i=0;i<form_val_array[0].length;i++) {
        form_vals[form_val_array[0][i]] = form_val_array[1][i];
    }

    var res = this.parseResponse(xhr);
    if (xhr.status ==200) {
        if (res.comment_id) {
            ///1. insert new comment into DOM
            var html_comment = this.create(
                {'id':res.comment_id,
                 'comment':form_vals.comment,
                 'name':this.username
                });
            parent_html = $('comment-' +form_vals['parent']);
            var ul = document.createElement('ul');
            ul.setAttribute('class','comment-thread');
            parent_html.appendChild(ul);
            ul.innerHTML = html_comment.text;
            ///2. decorate citations and respond link
            DjangoSherd_decorate_citations(
                getElementsByTagAndClassName('a','materialCitation',ul));

            var respond_elt = getFirstElementByTagAndClassName('span','respond_prompt',ul);
            connect(respond_elt, 'onclick', open_comment_form);
            ///3. reset form and set new validation key
            
            frm.elements['comment'] ='';
            tinyMCE.execInstanceCommand('id_comment','mceSetContent',false,'<p></p>',false);
            frm.elements['timestamp'].value = res.timestamp;
            frm.elements['security_hash'].value = res.security_hash;
            ///4. hide form
            hide_comment_form();
            document.location = '#comment-'+res.comment_id;

        }
    }
}

AjaxComment.prototype.onfail = function(func, xhr) {
    alert("There was an error submitting your comment!  Please report this to the system administrator.");
    console.log('error');
    console.log(xhr);    
}

AjaxComment.prototype.parseResponse = function(xhr) {
    var rv = {};
    var new_comment = String(xhr.responseText).match(/#comment-(\d+)/);
    if (new_comment != null) {
        rv["comment_id"] = new_comment[1];
    }
    var timestamp = String(xhr.responseText).match(/name="timestamp"\s+value="(\d+)"/);
    if (timestamp != null) {
        rv["timestamp"] = timestamp[1];
    }
    var security = String(xhr.responseText).match(/name="security_hash"\s+value="(\w+)"/);
    if (security != null) {
        rv["security_hash"] = security[1];
    }
    return rv;
}

AjaxComment.prototype.read = function() {

}

AjaxComment.prototype.create = function(obj,doc) {
    //microformat for a comment.  SYNC with templates/discussion/show_discussion.html

    '<ul class="comment-thread">';
    //{{current_comment.id}}
    //{{current_comment.name}}
    //{{current_comment.comment|safe}}
    var html = '<li id="comment-{{current_comment.id}}"\
                class="comment-thread"\
                >\
              <div class="comment new-comment">\
                <div class="threaded_comment_author">{{current_comment.name}} \
                  <a class="comment-anchor" href="#comment-{{current_comment.id}}">said:</a>\
                </div>\
                <div class="threaded_comment_text">\
                  {{current_comment.comment|safe}}\
                </div>\
                <div class="respond_to_comment_form_div" id="respond_to_comment_form_div_id_{{current_comment.id}}">\
                  <span class="respond_prompt" data-comment="{{current_comment.id}}" title="Click to show or hide the comment form">\
                    Respond<!-- to comment {{current_comment.id}}: -->\
                    </span><div class="comment_form_space"></div><!-- must be neighbor-->\
                </div>\
              </div>\
            </li>';
    '</ul>';
    var text = html
    .replace(/\{\{current_comment\.id\}\}/g,obj.id)
    .replace(/\{\{current_comment.name\}\}/g,obj.name)
    .replace(/\{\{current_comment\.comment\|safe\}\}/g,obj.comment);
    return {htmlID:'comment-'+obj.id,
            object:obj,
            text: text
           };
}

    var commenter = new AjaxComment(frm);

});
