/* global Sherd: true*/

import {renderPage} from '../../../../../pdf/utils.js';

const PdfJS = function() {
    var self = this;
    Sherd.Base.AssetView.apply(this, arguments); //inherit

    this.presentation = null;

    this.events.connect(window, 'resize', function() {
        if (self.presentation) {
            self.presentation.resize();
        }
    });

    this.pdf = {
        'features': [],
        'feature2json': function(feature) {
            console.log('feature2json');
        },
        'features2svg': function() {
            throw new Error('not implemented correctly');
        },
        'frag2feature': function(obj, map) {
            console.log('frag2feature');
        },
        'object_proportioned': function(object) {
            console.log('object_proportioned');
            var dim = {w: 180, h: 90};
            var w = object.width || 180;//76.23;//
            var h = object.height || 90;
            if (w / 2 > h) {
                dim.h = Math.ceil(180 * h / w);
            } else {
                dim.w = Math.ceil(90 * w / h);
            }
            return dim;
        },
        'object2bounds': function(object) {
            console.log('object2bounds');
        }
    };

    /*
     * Presentations pan and zoom to the annotation.
     */
    this.presentations = {
        'thumb': {
            height: function() {
                return 100;
            },
            width: function() {
                return 100;
            },
            initialize: function(obj, presenter) {
                console.log('pdf thumb init');
            },
            resize: function() {},
            controls: false
        },
        'gallery': {
            height: function(obj, presenter) {
                // scale the height
                return parseInt(this.width(obj, presenter), 10) /
                    obj.width * obj.height;
            },
            width: function(obj, presenter) {
                return 200;
            },
            initialize: function(obj, presenter) {
                console.log('pdf gallery init');
            },
            resize: function() {},
            controls: false
        },
        'default': {
            height: function(obj, presenter) {
                return Sherd.winHeight();
            },
            width: function(obj, presenter) { return '100%'; },
            initialize: function(obj, presenter) {
                console.log('pdf default init');
            },
            resize: function() {
            },
            controls: false
        },
        'medium': {
            height: function(obj, presenter) {
                var height = self.components.winHeight ? self.components.winHeight() : Sherd.winHeight();
                return height;
            },
            width: function(obj, presenter) {
                return '100%';
            },
            initialize: function(obj, presenter) {
                console.log('pdf medium init');
            },
            resize: function() {

            },
            controls: true
        },
        'small': {
            height: function() {
                return 390;
            },
            width: function() {
                return 320;
            },
            initialize: function(obj, presenter) {
                console.log('pdf small init');
            },
            resize: function() {},
            controls: false
        }
    };

    this.getPresentation = function(create_obj) {
        let presentation;
        switch (typeof create_obj.object.presentation) {
            case 'string':
                presentation = self.presentations[create_obj.object.presentation];
                break;
            case 'object':
                presentation = create_obj.object.presentation;
                break;
            case 'undefined':
                presentation = self.presentations['default'];
                break;
        }
        return presentation;
    };

    this.currentfeature = false;
    this.current_obj = false;

    this.getState = function() {
        return self.currentFeature;
    };

    // Called on initialization
    this.setState = function(obj) {
        const top = document.getElementById(self.current_obj.htmlID);
        const canvasEl = top.querySelector('canvas');
        const presentation = self.getPresentation(self.current_obj);

        // If page number isn't present, fall back to page 1.
        const pageNumber = (obj.geometry && obj.geometry.page) ?
              obj.geometry.page : 1;

        self.pdfLoadingTask.promise.then(function(pdf) {
            pdf.getPage(pageNumber).then(function(page) {
                renderPage(page, canvasEl, presentation.height());
            });
        });
    };

    this.microformat = {};
    this.microformat.create = function(obj, doc, options) {
        var wrapperID = Sherd.Base.newID('pdfjs-wrapper');
        ///TODO:zoom-levels might be something more direct on the object?
        if (!obj.options) {
            obj.options = {};
        }

        return {
            object: obj,
            htmlID: wrapperID,
            text: '<div id="' + wrapperID
                + '" class="sherd-pdfjs-view"><canvas></canvas></div>',
            winHeight: options &&
                options.functions &&
                options.functions.winHeight ?
                options.functions.winHeight : Sherd.winHeight
        };
    };
    this.microformat.update = function(obj, html_dom) {
        ///1. test if something exists in components now (else return false)
        ///2. assert( obj ~= from_obj) (else return false)
        //map is destroyed during .deinitialize(), so we don't need to
    };
    this.deinitialize = function() {
        if (this.pdf.map) {
            this.Layer.prototype.destroyAll();
            this.pdf.map.destroy();
        }
    };
    this.initialize = function(create_obj) {
        if (!create_obj) {
            return;
        }

        const presentation = self.getPresentation(create_obj);
        // Init pdf.js view
        const top = document.getElementById(create_obj.htmlID);
        const canvasEl = top.querySelector('canvas');
        const loadingTask = pdfjsLib.getDocument(create_obj.object.pdf);
        self.pdfLoadingTask = loadingTask;

        top.style.width = presentation.width(create_obj.object, self) + 'px';
        top.style.height = presentation.height(create_obj.object, self) + 'px';

        self.current_obj = create_obj;
    };
    this.microformat.components = function(html_dom, create_obj) {
        return {
            'top': html_dom,
            'winHeight': create_obj.winHeight
        };
    };

    this.queryformat = {
        find: function(str) {
            console.log('queryformat find', str);
            var xywh = String(str).match(/xywh=((\w+):)?([.\d]+),([.\d]+),([.\d]+),([.\d]+)/);
            if (xywh !== null) {
                var ann = {
                    xywh: {
                        x: Number(xywh[3]),
                        y: Number(xywh[4]),
                        w: Number(xywh[5]),
                        h: Number(xywh[6]),
                        units: xywh[2] || 'pixel'
                    }
                };
                return [ann];
            }
            return [];
        }
    };
};

// Old-Fashioned export
if (!window.Sherd) { window.Sherd = {}; }
if (!window.Sherd.Pdf) { window.Sherd.Pdf = {}; }
if (!window.Sherd.Pdf.PdfJS) {
    window.Sherd.Pdf.PdfJS = PdfJS;
}

// New export
export {PdfJS};
