/* global Sherd: true */
//jQuery dependencies
if (!Sherd) { Sherd = {}; }
if (!Sherd.Image) { Sherd.Image = {}; }
if (!Sherd.Image.FSIViewer) {
    Sherd.Image.FSIViewer = function () {
        var self = this;
        Sherd.Base.AssetView.apply(this, arguments); //inherit

        this.ready = false;
        this.current_state = {type: 'fsiviewer'};
        this.intended_states = [];
        this.presentation = null;
        
        this.valid_attributes = { 'bottom': 0, 'left': 0, 'right': 0, 'top': 0,
            'rotation': 0, 'imageUrl': '', 'scene': 0, 'set': 0, 'type': '',
            'wh_ratio': 0 };
        
        this.events.connect(window, 'resize', function () {
            if (self.presentation) {
                self.presentation.resize();
            }
        });

        this.getState = function () {
            ///see this.initialize() for function that updates current_state
            return self.current_state;
        };

        this._setState = function (obj) {
            try {
                if (obj && obj.set && obj.top) {
                    var clip_string = self.obj2arr(obj).join(', ');
                    self.components.top.SetVariable('FSICMD', 'Goto:' + clip_string);
                } else {
                    self.components.top.SetVariable('FSICMD', 'Reset');
                }
            }  catch (e) {
                /* ignore for the moment */
            }
        };

        this.setState = function (obj) {
            if (obj) {
                for (var a in obj) {
                    if (obj.hasOwnProperty(a) &&
                            self.valid_attributes.hasOwnProperty(a)) {
                        self.current_state[a] = obj[a];
                    }
                }
            }
            self.intended_states.push(obj);
            if (self.ready) {
                this._setState(obj);
            } //else see InitComplete below
        };
        //called when you click on the dots-icon next to the save icon
        ///ArtStor custom button functions
        window.saveToImageGroup = function (clip_string, maybe_name, clip_embed_url) {
            //could be: set, scene, left, top, right, bottom, rotation
            //example: asset-level: 1, 1, 0, 0, 1, 1, 0
            //example:  1,   1,     0.53, 0.43,0.711, 0.6114, 0
            /*
            console.log(clip_string);
            console.log(maybe_name);
            console.log(clip_embed_url);
             */
        };
        window.saveImage = function (clip_embed_url) {
            //console.log(clip_embed_url);
        };
        window.printImage = function (clip_embed_url) {
            //console.log(clip_embed_url);
        };

        ///utility functions to move from between array/obj repr
        this.obj2arr = function (o) {
            return [o.set, o.scene, o.left, o.top, o.right, o.bottom, o.rotation];
        };
        this.arr2obj = function (a) {
            return {
                'set': a[0],
                'scene': a[1],
                'left': a[2],
                'top': a[3],
                'right': a[4],
                'bottom': a[5],
                'rotation': a[6]
            };
        };

        this.presentations = {
            'thumb': {
                height: function () { return '100px'; },
                width: function () { return '100px'; },
                extra: 'CustomButton_buttons=&amp;NoNav=true&amp;MenuAlign=TL&amp;HideUI=true',
                resize: function () {}
            },
            'gallery': {
                height: function (obj, presenter) {
                    // scale the height
                    return parseInt(this.width(obj, presenter), 10) / obj.width * obj.height + 'px';
                },
                width: function (obj, presenter) { return '200px'; },
                extra: 'CustomButton_buttons=&amp;NoNav=true&amp;MenuAlign=TL&amp;HideUI=true',
                resize: function () {}
            },
            'default': {
                height: function (obj, presenter) { return Sherd.winHeight() + 'px'; },
                width: function (obj, presenter) { return '100%'; },
                extra: 'CustomButton_buttons=&amp;NoNav=undefined&amp;MenuAlign=TL&amp;HideUI=false',
                resize: function () {
                    var top = self.components.top;
                    top.setAttribute('height', Sherd.winHeight() + 'px');
                    self.current_state.wh_ratio = (top.offsetWidth / (top.offsetHeight - 30));
                }
            },
            'medium': {
                height: function (obj, presenter) {
                    var height = self.components.winHeight ? self.components.winHeight() : Sherd.winHeight();
                    return height + 'px';
                },
                width: function (obj, presenter) { return '100%'; },
                extra: 'CustomButton_buttons=&amp;NoNav=undefined&amp;MenuAlign=TL&amp;HideUI=false',
                resize: function () {
                    var top = self.components.top;
                    var height = self.components.winHeight ? self.components.winHeight() : Sherd.winHeight();
                    top.setAttribute('height', height + 'px');
                    self.current_state.wh_ratio = (top.offsetWidth / (top.offsetHeight - 30));
                }
            },
            'small': {
                height: function () { return '240px'; },
                width: function () { return '320px'; },
                extra: 'CustomButton_buttons=&amp;NoNav=undefined&amp;MenuAlign=BL&amp;HideUI=false',
                resize: function () {/*noop*/}
            }
        };

        this.initialize = function (create_obj) {
            ///copied from openlayers code:
            switch (typeof create_obj.object.presentation) {
            case 'string':
                self.presentation = self.presentations[create_obj.object.presentation];
                break;
            case 'object':
                self.presentation = create_obj.object.presentation;
                break;
            case 'undefined':
                self.presentation = self.presentations['default'];
                break;
            }

            var top = self.components.top;
            self.current_state.wh_ratio = (top.offsetWidth / (top.offsetHeight - 30));

            var state_listener = function (fsi_event, params) {
                //console.log('FSI EVENT:'+fsi_event);
                //console.log(params);
                switch (fsi_event) {
                case 'View':
                    if (self.ready) {
                        var o = self.arr2obj(params.split(', '));
                        for (var a in o) {
                            if (o.hasOwnProperty(a)) {
                                self.current_state[a] = o[a];
                            }
                        }
                    }
                    break;
                case 'ImageUrl':
                    ///replace '[width]' and '[height]' for desired size of image.
                    if (self.ready) {
                        self.current_state.imageUrl = params;
                    }
                    break;
                case 'LoadingComplete':
                    self.ready = true;
                    var s;
                    if (self.intended_states.length) {
                        setTimeout(function () {
                            self._setState(self.intended_states[self.intended_states.length - 1]);
                        }, 100);
                    }
                    break;
                case 'InitComplete':
                case 'Zoom':
                case 'Reset': //zoom all the way out and center
                case 'LoadProgress': //of the image
                case 'TooTip': //more or less == hover
                    ///and more
                }
            };
            window[create_obj.htmlID + '_DoFSCommand'] = state_listener;
            window[create_obj.htmlID + '_embed_DoFSCommand'] = state_listener;

            if (self.components.top.attachEvent) {
                ///Is this hacky or what?! IE SUX!
                /// http://code.google.com/p/swfobject/wiki/faq#5._Why_doesn't_fscommand_work_in_Internet_Explorer_with_dyn
                /// http://www.phpied.com/dynamic-script-and-style-elements-in-ie/
                var script = document.createElement('script');
                script.setAttribute('type', 'text/javascript');
                script.setAttribute('event', 'FSCommand(command,args)');
                script.setAttribute('for', create_obj.htmlID);
                script.text = create_obj.htmlID + '_DoFSCommand(command,args);';

                document.getElementsByTagName('head')[0].appendChild(script);
            }
        };
        this.microformat = {};
        this.microformat.components = function (html_dom, create_obj) {
            return {
                'top': html_dom,
                'winHeight': create_obj.winHeight
            };
        };
        this.microformat.create = function (obj, doc, options) {
            ///NOTE: we need underscores because this will become a javascript function name
            var fsi_object_id = Sherd.Base.newID('fsiviewer_wrapper');

            var broken_url;
            var fpx;
            if (obj.hasOwnProperty('image_fpx')) {
                broken_url = obj.image_fpx.split('/');
                fpx = obj["image_fpx-metadata"];
            } else {
                broken_url = obj.image_fpxid.split('/');
                fpx = obj["image_fpxid-metadata"];
            }
            var presentation = self.presentations[obj.presentation || 'default'];
            obj.image_fpx_base = broken_url.slice(0, 3).join('/') + '/';
            obj.image_fpx_src = broken_url.slice(3).join('/');

            obj.fsiviewer = obj.fsiviewer.replace('http://', 'https://');
            obj.image_fpx_base =
                obj.image_fpx_base.replace('http://', 'https://');

            var full_fpx_url = obj.fsiviewer +
                '?FPXBase=' + obj.image_fpx_base +
                '&amp;FPXSrc=' + obj.image_fpx_src +
                '&amp;FPXWidth=' + fpx.width +
                '&amp;FPXHeight=' + fpx.height + '&amp;' + presentation.extra;

            var html = '<object width="' + presentation.width(obj, self) + '" height="' + presentation.height(obj, self) + '" ' +
            'type="application/x-shockwave-flash" data="' + full_fpx_url + '" ' +
            //MS IE SUX !!!  this might break Opera--that's what you get for falsifying browser strings
            ((/MSIE/.test(navigator.userAgent)) ? ' classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" ' : '') +
            'id="' + fsi_object_id + '" name="' + fsi_object_id + '">' +
            '<param name="wmode" value="opaque"/><param name="allowScriptAccess" value="always"/><param name="swliveconnect" value="true"/><param name="menu" value="false"/><param name="quality" value="high"/><param name="scale" value="noscale"/><param name="salign" value="LT"/><param name="bgcolor" value="FFFFFF"/>' +
            '<param name="Movie" value="' + full_fpx_url + '" />' + ///required for IE to display movie
            '</object>';
            return {
                object: obj,
                htmlID: fsi_object_id,
                text: html,
                winHeight: options && options.functions && options.functions.winHeight ? options.functions.winHeight : Sherd.winHeight
            };
        };
    };
}
