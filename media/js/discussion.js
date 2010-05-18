addLoadEvent(function discussion_init() {
    var next_response_loc = false;
    var frm = jQuery('#comment-form').get(0);

    function open_comment_form(evt) {
        var respond = evt.target;
        frm.elements['parent'].value = respond.getAttribute("data-comment");
        if (!next_response_loc) {
	    next_response_loc = respond;
            respond.nextSibling.appendChild(frm);
            jQuery(frm).show();
            jQuery('#id_comment').focus();
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

    jQuery('.respond_prompt').click(open_comment_form);

    tinyMCE.onRemoveEditor.add(function(manager, ed) {
        //logDebug("third focus");
	if (next_response_loc) {
            next_response_loc.nextSibling.appendChild(document.forms[0]);
            tinyMCE.execCommand("mceAddControl", false, "id_comment");
	} else {
            jQuery('#comment-form').hide();
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
    this.username = jQuery('#logged_in_name').text();

    jQuery(form).bind('submit',this,this.submit);
}

AjaxComment.prototype.submit = function(evt) {
    var self = evt.data;
    tinyMCE.triggerSave();
    evt.preventDefault();

    var frm = jQuery(self.form);
    form_val_array = frm.serializeArray();

    jQuery.ajax({
        type: 'POST',
        url: self.form.action,
        data: form_val_array,//default will serialize?
        dataType: 'html',
        success: self.oncomplete,
        error: self.onfail,
        context: {'self':self,'form_val_array':form_val_array}
    });
    //frm.elements['timestamp'].value = '';
    //frm.elements['security_hash'].value = '';
}

AjaxComment.prototype.oncomplete = function(responseText, textStatus, xhr) {
    var self = this.self;
    var form_vals = {};
    for (var i=0;i<this.form_val_array.length;i++) {
        form_vals[this.form_val_array[i].name] = this.form_val_array[i].value;
    }
    var res = self.parseResponse(xhr);
    if (xhr.status ==200) {
        if (res.comment_id) {
            ///1. insert new comment into DOM
            var html_comment = self.create(
                {'id':res.comment_id,
                 'comment':form_vals.comment,
                 'name':self.username
                });
            parent_html = $('comment-' +form_vals['parent']);
            var ul = document.createElement('ul');
            ul.setAttribute('class','comment-thread');
            parent_html.appendChild(ul);
            ul.innerHTML = html_comment.text;
            ///2. decorate citations and respond link
            DjangoSherd_decorate_citations( 
                //passing to Mochi forEach so needs to be an array
                jQuery('a.materialCitation',ul).toArray()
            );

            jQuery('span.respond_prompt',ul).click(open_comment_form);

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

AjaxComment.prototype.onfail = function(xhr, textStatus, errorThrown) {
    alert("There was an error submitting your comment!  Please report this to the system administrator.");
    console.log('error:'+errorThrown);
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
