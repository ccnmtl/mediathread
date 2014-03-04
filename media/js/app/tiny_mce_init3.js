var tiny_mce_settings = {
        theme: "advanced",
        content_css: "/media/css/project.css",
        mode: "specific_textareas",
        editor_selector: "mceEditor",
        entity_encoding : "numeric",
        /*CUSTOM CCNMTL: added 'citation' and 'editorwindow' --see bottom for explicit loading from a location */
        plugins: "searchreplace,table,-citation,inlinepopups,-editorwindow,xhtmlxtras,paste",
        /* CUSTOM CCNMTL: visual is set to false, so anchor tags don't get messed up.  This is probably a bug
            to be reported to tinyMCE */
        visual: false,
        theme_advanced_styles: "Even=even;Odd=odd;Highlight=visualHighlight;Discreet=discreet;Image Right=imageRight;Image Inline=imageInline;Image Left=imageLeft;Sidebar=contentSideBar",
        theme_advanced_blockformats: "p,h1,h2,h3,h4,h5,h6,address,pre",
        theme_advanced_toolbar_location: "top",
        theme_advanced_toolbar_align: "left",
        /* CUSTOM CCNMTL: peared down the UI buttons available */
        /* Safari doesn't support buttons, so turn them off */
        theme_advanced_buttons1: "bold, italic, underline, spacer, bullist, numlist, spacer, outdent, indent, spacer, undo, redo, spacer, link, unlink, image, spacer, code, pasteword",
        theme_advanced_buttons2: "",
        theme_advanced_path: false,
        ///CCNMTL: ENABLED IN DISCUSSIONS, see discussionpanel.js
        //theme_advanced_statusbar_location: "bottom",
        theme_advanced_resizing: true,
        theme_advanced_resize_horizontal: false,
        theme_advanced_resize_vertical: false,
        theme_advanced_resizing_max_height: 325,
        remove_linebreaks: true,
        convert_urls: false,
        gecko_spellcheck: true,
        init_instance_callback: function (inst) {
            // broadcast initialized message using the textarea
            jQuery(window).trigger('tinymce_init_instance', [ inst ]);
        },
        //setupcontent_callback : "plugin_regexrep_setup",
        //save_callback : "plugin_regexrep_save",
        //setupcontent_regex : regexes,
        //save_regex : regexes,
        paste_auto_cleanup_on_paste: true,
        paste_create_paragraphs: true,
        paste_create_linebreaks: true,
        paste_use_dialog: false,
        paste_convert_middot_lists: true,
        paste_strip_class_attributes: 'mso',
        setup: function (inst) {
            ///tab and shift-tab indent/outdent for Brie
            ///http://tinymce.moxiecode.com/punbb/viewtopic.php?pid=44170#p44170
            inst.onKeyDown.add(
                    function (ed, e) {
                        if (e.keyCode === 9 && !e.altKey && !e.ctrlKey) {
                            if (e.shiftKey) {
                                ed.execCommand('Outdent');
                            } else {
                                ed.execCommand('Indent');
                            }
                            return tinymce.dom.Event.cancel(e);
                        }
                    });
        },
        valid_elements: "" +
            "a[class|href|id|name|tabindex|title|target]," +
            "abbr[class|id|title]," +
            "acronym[class|id|title]," +
            "address[class|align|id|title]," +
            "bdo[class|id|title]," +
            "big[class|id|title]," +
            "blockquote[dir|cite|class|id|title]," +
            "br[class|clear<all?left?none?right|id|title]," +
            "button[accesskey|class|disabled<disabled|id|name|tabindex|title|type|value]," +
            "caption," +
            "center[class|id|title]," +
            "cite[class|id|title]," +
            "code[class|id|title]," +
            "col[off|class|id|span|title|valign<baseline?bottom?middle?top|width]," +
            "colgroup[off|class|id|span|title|valign<baseline?bottom?middle?top|width]," +
            "dd[class|id|title]," +
            "del[cite|class|datetime|id|title]," +
            "dfn[class|id|title]," +
            "dir[class|compact<compact|id|title]," +
            "div[align<center?right?justify|class|id|style|title]," +
            "dl[class|compact<compact|id|title]," +
            "dt[class|id|title]," +
            "em/i[class|id|title]," +
            "fieldset[class|id|title]," +
            "form[accept|accept-charset|action|class|enctype|id|method<get?post|name|title|target]," +
            "h1[class|id|title]," +
            "h2[class|id|title]," +
            "h3[class|id|title]," +
            "h4[class|id|title]," +
            "h5[class|id|title]," +
            "h6[class|id|title]," +
            "hr[align<center?right|class|id|noshade<noshade|size|title|width]," +
            "iframe[align<bottom?left?middle?right?top|class|frameborder|height|id|longdesc|marginheight|marginwidth|name|scrolling<auto?no?yes|src|title|width]," +
            "img[alt|border|class|height|hspace|id|longdesc|name|src|title|width]," +
            "input[accept|accesskey|alt|checked<checked|class|disabled<disabled|id|maxlength|name|readonly<readonly|size|src|tabindex|title|type<button?checkbox?file?hidden?image?password?radio?reset?submit?text|value|onclick]," +
            "ins[cite|class|datetime|id|title]," +
            "isindex[class|id|prompt|title]," +
            "kbd[class|id|title]," +
            "label[accesskey|class|for|id|title]," +
            "legend[accesskey|class|id|title]," +
            "li[class|id|title|type|value]," +
            "link[class|href|hreflang|id|media|rel|rev|title|target|type]," +
            "map[class|id|name|title]," +
            "menu[class|compact<compact|id|title]," +
            "noframes[class|id|title]," +
            "noscript[class|id|title]," +
            "ol[class|compact<compact|id|start|title|type]," +
            "optgroup[class|disabled<disabled|id|label|title]," +
            "option[class|disabled<disabled|id|label|selected<selected|title|value]," +
            "p[align<center?right?justify|class|id|style|title]," +
            "param[id|name|type|value|valuetype<DATA?OBJECT?REF]," +
            "pre/listing/plaintext/xmp[align<center?right?justify|class|id|title|width]," +
            "q[cite|class|id|title]," +
            "s[class|id|title]," +
            "samp[class|id|title]," +
            "select[class|disabled<disabled|id|multiple<multiple|name|size|tabindex|title]," +
            "small[class|id|title]," +
            "span[align<center?right?justify|class|class|id|style|title]," +
            "strike[class|class|id|title]," +
            "strong/b," +
            "sub[class|id|title]," +
            "sup[class|id|title]," +
            "table[class|id|rules|summary|title]," +
            "tbody[class|id|title]," +
            "td[class|colspan|id|rowspan|title|nowrap]," +
            "textarea[accesskey|class|cols|disabled<disabled|id|name|readonly<readonly|rows|tabindex|title]," +
            "tfoot[off|class|id|title|valign<baseline?bottom?middle?top]," +
            "th[class|id|title|nowrap]," +
            "thead[class|id|title]," +
            "title[dir<ltr?rtl]," +
            "tr[class|id|title]," +
            "tt[class|id|title]," +
            "u[class|id|title]," +
            "ul[class|compact<compact|id|title|type]"
    };

tinymce.PluginManager.load('citation', '/media/js/sherdjs/lib/mcePlugin_citation/editor_plugin.js');
tinymce.PluginManager.load('editorwindow', '/media/js/sherdjs/lib/mcePlugin_editorwindow/editor_plugin.js');
tinyMCE.init(tiny_mce_settings);


