/**
 * $Id
 *
 * @author Schuyler Duveen at Columbia Center for New Media Teaching and Learning
 * @copyright Copyright (C) 2009, Columbia University
 * @license LGPL 2.1 and any later version
 */

(function() {
    var Event = tinymce.dom.Event, DOM = tinymce.DOM, is = tinymce.is;

    tinymce.create('tinymce.plugins.EditorWindow', {
        getInfo : function() {
            return {
                longname : 'EditorWindow',
                author : 'Schuyler Duveen at Columbia Center for New Media Teaching and Learning',
                authorurl : 'http://ccnmtl.columbia.edu/compiled/',
                infourl : 'http://ccnmtl.columbia.edu/projects/vital/',
                version : '0.8'
            };
        },
        init : function(ed,url) {
            var self = this;
            DOM.loadCSS(url + '/skins/' + (ed.settings.editorwindow_skin || 'minimalist') + "/window.css");
            //ed.dom.loadCSS(....)
            ed.onNodeChange.add(this._nodeChanged,this);
            ed.onKeyDown.add(function(ed,evt){self._closeOnEscape(evt);});

            ed.addCursorWindow = function(obj) {
                if (obj && typeof obj.test == 'function') {
                    if (typeof obj.content == 'function') {
                        self._listeners.push(obj);
                    }
                }
                else throw 'addCursorWindow object must have a .test function!';
            }
        },
        _closeOnEscape: function(evt) {
            //ESCAPE KEY
            if (evt.keyCode==27 && this.opened) {
                this._closeWindow();
                Event.cancel(evt);
            }
        },
        _listeners: [
            {
                name:'link',
                test:function(current_elt) {//A tag and not anchor
                    var parent = DOM.getParent(current_elt, 'A');
                    if (parent && !parent.name) return parent;
                },
                content:function(a_tag) {
                    return DOM.create('a',{href:a_tag.href,
                                           target:'_blank'
                                          },'open link');
                }
            }
        ],
        _nodeChanged: function(ed, cm/*control manager*/, current_elt, collapsed, opt) {
            if (typeof opt === 'object' && opt.initial === true) {
                // Don't show the editor window on page load.
                return false;
            }

            var self = this;
            var i = self._listeners.length;//last wins
            while (--i >=0) {
                var parent = self._listeners[i].test(current_elt);
                if (parent) {
                    if (this.opened) {
                        if (parent == this.tag_for_window) {
                            this._positionWindow(ed,current_elt, parent);
                        } else {
                            ///superceded by another listeners
                            ///TODO: maybe we should do this based on
                            ///closeness to child, but then we assume
                            ///they're both parents
                            ///- also impedes real supercession (e.g. A.cls beats link)
                            this._closeWindow();
                        }
                    }

                    //retest this.opened in case it was just closed above
                    if (!this.opened && parent != this.tag_for_window) {
                        this.opened = self._listeners[i];
                        this.tag_for_window = parent;
                        this._openWindow(ed, current_elt, parent);
                    }
                    break;
                }
            }
            if (i < 0) { //no results
                this._closeWindow();
                this.tag_for_window = false;
            }
        },
        getAbsoluteCursorPos: function(ed,current_elt,/*optional*/parent) {
            //parent determines the x-pos, which can stabilize positioning
            var pos = {container:ed.getContentAreaContainer()};
            var p1 = DOM.getPos(current_elt);
            var p2 = (parent) ? DOM.getPos(parent) : p1;
            var cp = DOM.getPos(pos.container);
            //Q:viewport scroll an issue? A:somehow, no
            ///use current_elt, not parent because parent might be multi-line
            pos.x = p2.x+cp.x;
            pos.y = p1.y+cp.y;
            return pos;
        },
        _positionWindow: function(ed,current_elt,parent) {
            var pos = this.getAbsoluteCursorPos(ed,current_elt,parent);
            var rect = DOM.getRect(this.win);
            var viewport = DOM.getViewPort(window);

            DOM.setStyles(this.win,{
                top:(pos.y +20) +'px',
                left:Math.min(pos.x +10, Math.max(0,viewport.w-rect.w-20)) +'px'
            });
        },
        _newWindow:function(id) {
            var win = DOM.create('div',{
                'class':'mce_editorwindow',
                'id':id
            });
            this._addAll(win, ['div',{id:id+'_top'},
                               ['a', {id:id+'_close','class' : 'mce_editorwindow_closebtn', tabindex : '-1', href : 'javascript:;', onmousedown : 'return false;'},'x'],
                               ['div',{id:id+'_content'}]
                              ]
                        );
            //a little much?  but that's where the key events are :-(
            //any changes should also update removal in _closeWindow
            Event.add(window,'keydown',this._closeOnEscape,this);
            return win;
        },
        _openWindow: function(ed,current_elt,parent) {
            var self = this;
            ///TODO: we could wait here, and wrap this in a setTimeout
            /// make sure that someone 'settled' onto the element, but
            /// that could get complicated.

            var id = DOM.uniqueId();
            this.win = this._newWindow(id);

            document.body.appendChild(this.win);
            /*** after adding to document, so we can getbyID ***/
            //custom content
            DOM.get(id+'_content').appendChild( this.opened.content(parent) );

            this._positionWindow(ed,current_elt,parent);

            Event.add(id+'_close', 'mousedown', function(evt){
                self._closeWindow(ed,current_elt);
            });
        },
        _closeWindow: function(ed,current_elt) {
            if (this.opened && typeof this.opened.onUnload == 'function') {
                this.opened.onUnload(this.win);
            }
            this.opened = false;
            if (this.win) {
                Event.remove(window,'keydown',this._closeOnEscape,this);
                DOM.remove(this.win);
                delete this.win;
            }
        },
        ///copied from inlinepopups plugin
        _addAll : function(te, ne) {
            var i, n, t = this;

            if (is(ne, 'string'))
                te.appendChild(DOM.doc.createTextNode(ne));
            else if (ne.length) {
                te = te.appendChild(DOM.create(ne[0], ne[1]));

                for (i=2; i<ne.length; i++)
                    t._addAll(te, ne[i]);
            }
        }
    });

    // Register plugin
    tinymce.PluginManager.add('editorwindow', tinymce.plugins.EditorWindow);
})();
