/* global Sherd: true, MochiKit: true, $f: true, djangosherd: true */

if (typeof Sherd === 'undefined' || !Sherd) {
    Sherd = {};
}

//?wrap in module?
function hasAttr(obj, key) {
    try {
        return (typeof (obj[key]) !== 'undefined');
    } catch (e) {
        return false;
    }
}
var new_id = 0;
Sherd.Base = {
    'hasAttr' : hasAttr,
    'newID' : function (prefix) {
        prefix = prefix || 'autogen';
        var new_id = 1;
        while (document.getElementById(prefix + new_id) !== null) {
            new_id = Math.floor(Math.random() * 10000);
        }
        return prefix + new_id;
    },
    'log' : function () {
        try {
            window.console.log(arguments);
        } catch (e) {
            var args = [];
            var m = arguments.length;
            while (--m >= 0) {
                args.unshift(arguments[m]);
            }
            document.body.appendChild(Sherd.Base
                    .html2dom('<div class="log">' + String(args) + '</div>'));
        }
    },
    'html2dom' : function (html_text, doc) {
        // @html_text MUST have no leading/trailing whitespace, and only be one
        // element
        doc = (doc) ? doc : document;
        var temp_div = doc.createElement('div');
        temp_div.innerHTML = html_text;
        if (temp_div.childNodes.length === 1) {
            return temp_div.firstChild;
        }
    },
    'Observer' : function () {
        // the real work is done by connect/signal stuff below
        // this just keeps track of the stuff that needs to be destroyed
        var _listeners = {};
        var _named_listeners = {};
        var _nextListener = 0;
        this.addListener = function (obj, slot) {
            if (slot && _named_listeners[slot]) {
                this.removeListener(slot);
                _named_listeners[slot] = obj;
                return slot;
            } else {
                _listeners[++_nextListener] = obj;
                return _nextListener;
            }
        };
        this.removeListener = function (slot_or_pos) {
            var stor = (_named_listeners[slot_or_pos]) ? _named_listeners
                    : _listeners;
            if (stor[slot_or_pos]) {
                stor[slot_or_pos].disconnect();
                delete stor[slot_or_pos];
            }
        };
        this.clearListeners = function () {
            for (var a in _named_listeners) {
                if (_named_listeners.hasOwnProperty(a)) {
                    this.removeListener(a);
                }
            }
            for (var b in _listeners) {
                if (_listeners.hasOwnProperty(b)) {
                    this.removeListener(b);
                }
            }
        };
        this.events = {
            signal : Sherd.Base.Events.signal,
            connect : Sherd.Base.Events.connect
        };
    },// Observer
    'DomObject' : function () {
        // must override
        Sherd.Base.Observer.call(this);// inherit
        var self = this;

        this.components = {}; // all html refs should go in here
        this.get = function () {
            throw new Error("get() not implemented");
        };
        this.microformat = function () {
            throw new Error("microformat() not implemented");
        };
        this.idPrefix = function () {
            return 'domObj';
        };
        this.id = function () {
            var _dom = this.get();
            if (!_dom.id) {
                _dom.id = Sherd.Base.newID(this.idPrefix());
            }
            return _dom.id;
        };

        // var _microformat;
        // this.microformat = function () {return _microformat;}
        this.attachMicroformat = function (microformat) {
            this.microformat = microformat;
        };
        this.html = {
            get : function (part) {
                part = (part) ? part : 'media';
                return self.components[part];
            },
            put : function (dom, create_obj) {
                // maybe should update instead of clobber,
                // /but we should have it clobber
                // /until we need it
                if (self.microformat && self.microformat.components) {
                    var possiblePromise = self.microformat.components(dom, create_obj);

                    if (possiblePromise &&
                        typeof possiblePromise.done === 'function'
                       ) {
                        possiblePromise.done(function(components) {
                            self.components = components;
                        });
                    } else if (typeof possiblePromise === 'object') {
                        self.components = possiblePromise;
                    } else {
                        window.console.error('components error:', possiblePromise);
                    }
                } else {
                    self.components = {
                        'top' : dom
                    };
                }

                // Do self configuration post create
                if (self.initialize) {
                    self.initialize(create_obj);
                }
            },
            remove : function () {
                self.clearListeners();
                if (self.deinitialize) {
                    self.deinitialize();
                }

                for (var part in self.components) {
                    if (typeof self.components[part] === 'object' &&
                        self.components[part].parentNode) {
                        self.components[part].parentNode
                        .removeChild(self.components[part]);
                    }
                }
            },

            // /utility functions for adding htmlstrings (e.g. output from create()
            // ) into the dom.
            write : function (towrite, doc) {
                doc = (doc) ? doc : document;
                if (typeof towrite === 'string') {
                    doc.write(towrite);
                } else if (typeof towrite === 'object' && towrite.text) {
                    doc.write(towrite.text);
                    if (towrite.htmlID) {
                        self.html.put(doc.getElementById(towrite.htmlID));
                    }
                }
            },
            replaceContents : function (htmlstring, dom) {
                if (typeof htmlstring === 'string') {
                    dom.innerHTML = htmlstring;
                }
            }
        };//this.html

    }, // DomObject
    'AssetView' : function () {
        var self = this;
        Sherd.Base.DomObject.apply(this);

        this.options = {};

        // get/set functions to communicate current state to other players
        this.getState = function () {};
        this.setState = function (obj) {};

        if (this.html && !this.html.pull) {
            // NOTE: html.pull is not currently used.
            this.html.pull = function (dom_or_id, optional_microformat) {
                // /argument resolution
                if (typeof dom_or_id === 'string') {
                    dom_or_id = document.getElementById(dom_or_id);
                }
                var mf = (optional_microformat) ? optional_microformat : self.microformat;
                // /
                var asset = mf.read({
                    html : dom_or_id
                });
                // FAKE!!! (for now)
                self.events.signal(self, 'asset.update');

                return asset;
            };
            this.html.push = function (dom_or_id, options) {
                options = options || {};
                options.microformat = options.microformat || self.microformat;
                options.asset = options.asset || self._asset;
                // /argument resolution
                if (typeof dom_or_id === 'string') {
                    dom_or_id = document.getElementById(dom_or_id);
                }
                if (options.asset) {
                    if (options.asset !== self._asset) {
                        if (self.deinitialize) {
                            self.deinitialize();
                        }

                        var updated = (options.microformat.update && options.microformat.update(options.asset, dom_or_id.firstChild));
                        if (!updated) {
                            var create_obj = options.microformat.create(options.asset, null, options);

                            if (create_obj.text && dom_or_id) {
                                dom_or_id.innerHTML = create_obj.text;
                            }

                            // options.extra_text = { 'instructions' : 'clipform-instructions' }
                            for (var div in options.extra) {
                                if (div in create_obj) {
                                    dom_or_id = document.getElementById(options.extra[div]);
                                    if (dom_or_id) {
                                        dom_or_id.innerHTML = create_obj[div];
                                    }
                                }
                            }

                            // Create microformat.components (self.components)
                            var top = document.getElementById(create_obj.htmlID);

                            // If the created element was a vimeo video, we need to
                            // initialize its 'ready' handler.
                            if (/^vimeo-wrapper-\d+$/.test(create_obj.htmlID)) {
                                var iframe = jQuery(top).find('iframe')[0];
                                var froogaloop = $f(iframe);
                                froogaloop.addEvent('ready', function() {
                                    djangosherd.assetview.settings.vimeo.view.vimeoPlayerReady(
                                        froogaloop);
                                });
                            }
                            self.html.put(top, create_obj);
                        }
                    }
                }
            };
        }
    },// AssetView
    'AssetManager' : function (config) {
        this.config = (config) ? config : {
            // defaults
            'storage' : Sherd.Base.Storage,
            'layers' : {

            }
        };

    },// AssetManager
    'Storage' : function () {
        Sherd.Base.Observer.call(this);// inherit

        var _local_objects = {};
        var localid_counter = 0;
        this._localid = function (obj_or_id) {
            var localid;
            if (typeof obj_or_id === 'string') {
                localid = obj_or_id;
            } else if (hasAttr(obj_or_id, 'local_id')) {
                localid = obj_or_id.local_id;
            } else {
                localid = String(++localid_counter);
            }
            return localid;
        };
        this._local = function (id, obj) {
            if (arguments.length > 1) {
                _local_objects[id] = obj;
            }
            return (hasAttr(_local_objects, id)) ? _local_objects[id] : false;
        };
        this.load = function (obj_or_id) {

        };
        this.get = function (obj_or_id) {
            var localid = this._localid(obj_or_id);
            return this._local(localid);
        };
        this.save = function (obj) {
            var localid = this._localid(obj);
            this._local(localid, obj);
        };
        this.remove = function (obj_or_id) {

        };

        this._update = function () {
            this.callListeners('update', [ this ]);
        };
    }//Storage
};
//Base

/* connected functions
 con_func(event,src
 */
if (typeof jQuery !== 'undefined') {
    ///TODO: before making jQuery take precedent over MochiKit, we need to
    /// make sure  viewers using self.events.connect()/signal() work with jQuery
    Sherd.winHeight = function () {
        return jQuery(window).height() - 245;
    };
    Sherd.Base.Events = {
        'connect' : function (subject, event, func) {
            var disc = jQuery(subject).bind(event, function (evt, param) {
                if (param) {
                    func(param);
                } else {
                    func(evt);
                }
            });
            return {
                disconnect : function () {
                    jQuery(disc).unbind(event);
                }
            };
        },
        'signal' : function (subject, event, param) {
            jQuery(subject).trigger(event, [param]);
        }
    };
} //end jquery
else if (typeof MochiKit !== 'undefined') {
    Sherd.winHeight = function () {
        return MochiKit.Style.getViewportDimensions().h - 250;
    };
    Sherd.Base.Events = {
        'connect' : function (subject, event, func) {
            if (typeof subject.nodeType !== 'undefined' ||
                subject === window ||
                subject === document) {
                event = 'on' + event;
            }
            var disc = MochiKit.Signal.connect(subject, event, func);
            return {
                disconnect : function () {
                    MochiKit.Signal.disconnect(disc);
                }
            };
        },
        'signal' : function (subject, event, param) {
            MochiKit.Signal.signal(subject, event, param);
        }
    };
} //end mochikit
else {
    throw new Error("Use a framework, Dude! MochiKit, jQuery, YUI, whatever!");
}
