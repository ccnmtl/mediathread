#!/bin/bash
cd ../lib/tiny_mce3
ant
#http://kodos.ccnmtl.columbia.edu:13086/media/js/sherdjs/lib/tiny_mce3/
cat jscripts/tiny_mce/tiny_mce_jquery.js jscripts/tiny_mce/themes/advanced/editor_template.js jscripts/tiny_mce/plugins/paste/editor_plugin.js jscripts/tiny_mce/plugins/searchreplace/editor_plugin.js jscripts/tiny_mce/plugins/table/editor_plugin.js jscripts/tiny_mce/plugins/inlinepopups/editor_plugin.js jscripts/tiny_mce/plugins/xhtmlxtras/editor_plugin.js > ../tiny_mce3_min.js
