function plugin_regexrep_setup(editor_id, node) {
  node.innerHTML = plugin_regexrep_replace(node.innerHTML, 'setupcontent_regex');
}
function plugin_regexrep_save(editor_id, content, node) {
  return plugin_regexrep_replace(content, 'save_regex');
}
function plugin_regexrep_replace(content, tiny_param) {
  var re_string = tinyMCE.getParam(tiny_param);
  if (typeof(re_string) == "undefined" || re_string == "" || re_string == null) {
    return;
  }
  var re_array = re_string.split(/[*][*]/g);
  for (i=0; i<re_array.length; i++) {
    if (typeof(re_array[i]) == "undefined" || re_array[i] == "" || re_array[i] == null) {
      continue;
    }
    var tokens = re_array[i].split(/\+\+/g);
    if (tokens[0] == null) { return; }
    var replace = ((tokens[1] == null || typeof tokens[1] == "undefined") ? '' : tokens[1] );
    var flags = ((tokens[2] == null || typeof tokens[2] == "undefined") ? 'g' : tokens[2] );
    var re = new RegExp(tokens[0], flags);
    content = content.replace(re, replace);
  }
  return content;
}
/* Table Regular Expression (Mangles tables under IE)
**(?:<(?!t[dhr]|a\\b)[^>]*?>)*(?=(?:(?!<t[dhr]\\b).)*?<\\/t[dh]>)++++ig
*/
var regexes="class\\s*=?\\s*\"?(?:Mso[^\"]*?)\"?++++gi**<![-]-.*?--\\s*>++++g";


var tiny_mce_settings_for_vital = {
  theme:"advanced",
  /* content_css:"tinyContent.css", CUSTOM CCNMTL--commenting out*/
  content_css:"/site_media/css/project.css",
  mode:"specific_textareas",
	    /*CUSTOM CCNMTL: added 'citation' */
  entity_encoding : "numeric",
	    /*CUSTOM CCNMTL: added 'citation' */
  plugins:"searchreplace,table,citation",
	    /* CUSTOM CCNMTL: visual is set to false, so anchor tags don't get messed up.  This is probably a bug
	       to be reported to tinyMCE */
  visual:false,
  theme_advanced_styles:"Even=even;Odd=odd;Highlight=visualHighlight;Discreet=discreet;Image Right=imageRight;Image Inline=imageInline;Image Left=imageLeft;Sidebar=contentSideBar",
  theme_advanced_blockformats:"p,h1,h2,h3,h4,h5,h6,address,pre",
  theme_advanced_toolbar_location:"top",
  theme_advanced_toolbar_align:"left",
	    /* CUSTOM CCNMTL: peared down the UI buttons available */
	    /* Safari doesn't support buttons, so turn them off */
  theme_advanced_buttons1:"bold, italic, underline, spacer, bullist, numlist, spacer, outdent, indent, spacer, undo, redo, spacer, link, unlink, image, spacer, code",
  theme_advanced_buttons2:"",
  theme_advanced_path_location:"",
  remove_linebreaks:true,
  setupcontent_callback : "plugin_regexrep_setup",
  save_callback : "plugin_regexrep_save",
  setupcontent_regex : regexes,
  save_regex : regexes,
  valid_elements:""
  +"a[class|href|id|name|tabindex|title|target],"
  +"abbr[class|id|title],"
  +"acronym[class|id|title],"
  +"address[class|align|id|title],"
  +"bdo[class|id|title]," 
  +"big[class|id|title]," 
  +"blockquote[dir|cite|class|id|title]," 
  +"br[class|clear<all?left?none?right|id|title],"
  +"button[accesskey|class|disabled<disabled|id|name|tabindex|title|type|value]," 
  +"caption," 
  +"center[class|id|title]," 
  +"cite[class|id|title]," 
  +"code[class|id|title]," 
  +"col[off|class|id|span|title|valign<baseline?bottom?middle?top|width]," 
  +"colgroup[off|class|id|span|title|valign<baseline?bottom?middle?top|width]," 
  +"dd[class|id|title],"
  +"del[cite|class|datetime|id|title],"
  +"dfn[class|id|title],"
  +"dir[class|compact<compact|id|title],"
  +"div[align<center?right?justify|class|id|style|title]," 
  +"dl[class|compact<compact|id|title]," 
  +"dt[class|id|title]," 
  +"em/i[class|id|title],"
  +"fieldset[class|id|title]," 
  +"form[accept|accept-charset|action|class|enctype|id|method<get?post|name|title|target]," 
  +"h1[class|id|title]," 
  +"h2[class|id|title]," 
  +"h3[class|id|title]," 
  +"h4[class|id|title]," 
  +"h5[class|id|title]," 
  +"h6[class|id|title]," 
  +"hr[align<center?right|class|id|noshade<noshade|size|title|width]," 
  +"iframe[align<bottom?left?middle?right?top|class|frameborder|height|id|longdesc|marginheight|marginwidth|name|scrolling<auto?no?yes|src|title|width]," 
  +"img[alt|border|class|height|hspace|id|longdesc|name|src|title|width]," 
  +"input[accept|accesskey|alt|checked<checked|class|disabled<disabled|id|maxlength|name|readonly<readonly|size|src|tabindex|title|type<button?checkbox?file?hidden?image?password?radio?reset?submit?text|value|onclick]," 
  +"ins[cite|class|datetime|id|title],"
  +"isindex[class|id|prompt|title],"
  +"kbd[class|id|title],"
  +"label[accesskey|class|for|id|title],"
  +"legend[accesskey|class|id|title],"
  +"li[class|id|title|type|value],"
  +"link[class|href|hreflang|id|media|rel|rev|title|target|type],"
  +"map[class|id|name|title],"
  +"menu[class|compact<compact|id|title],"
  +"noframes[class|id|title],"
  +"noscript[class|id|title],"
  +"ol[class|compact<compact|id|start|title|type],"
  +"optgroup[class|disabled<disabled|id|label|title],"
  +"option[class|disabled<disabled|id|label|selected<selected|title|value],"
  +"p[align<center?right?justify|class|id|style|title],"
  +"param[id|name|type|value|valuetype<DATA?OBJECT?REF],"
  +"pre/listing/plaintext/xmp[align<center?right?justify|class|id|title|width],"
  +"q[cite|class|id|title],"
  +"s[class|id|title],"
  +"samp[class|id|title],"
  +"select[class|disabled<disabled|id|multiple<multiple|name|size|tabindex|title],"
  +"small[class|id|title],"
  +"span[align<center?right?justify|class|class|id|style|title],"
  +"strike[class|class|id|title],"
  +"strong/b,"
  +"sub[class|id|title]," 
  +"sup[class|id|title]," 
  +"table[class|id|rules|summary|title]," 
  +"tbody[class|id|title],"
  +"td[class|colspan|id|rowspan|title|nowrap],"
  +"textarea[accesskey|class|cols|disabled<disabled|id|name|readonly<readonly|rows|tabindex|title]," 
  +"tfoot[off|class|id|title|valign<baseline?bottom?middle?top],"
  +"th[class|id|title|nowrap],"
  +"thead[class|id|title],"
  +"title[dir<ltr?rtl],"
  +"tr[class|id|title],"
  +"tt[class|id|title],"
  +"u[class|id|title],"
  +"ul[class|compact<compact|id|title|type]"
};


if ( typeof (check_length_callbacks) != "undefined" ) {
    update (tiny_mce_settings_for_vital, check_length_callbacks);
}

tinyMCE.init(tiny_mce_settings_for_vital);


