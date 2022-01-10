/* global Sherd: true */
if (typeof Sherd === 'undefined') {
    Sherd = {};
}

// TODO used?
if (!Sherd.AssetLayer) {
    Sherd.AssetLayer = function() {

    };// AssetLayer
}

// GenericAssetView -- contains the pointer functions for displaying all types of media
// Each media type identifies a "view" to display the media
// And a clipForm that controls how the media is annotated
const GenericAssetView = function(options) {
    var self = this;
    //consts
    var Clipstripper = Sherd.Video.Annotators.ClipStrip;
    var Clipformer = Sherd.Video.Annotators.ClipForm;
    var Clipplayer = Sherd.Video.Annotators.ClipPlay;
    this.options = options;
    // //INIT
    this.settings = {};
    if (Sherd.Video) {
        var decorateVideo = function(options, viewgroup) {
            if (options.clipform) {
                viewgroup.clipform = new Clipformer();// see clipform.js
                viewgroup.clipform.attachView(viewgroup.view);
                if (options.storage) {
                    viewgroup.clipform.addStorage(options.storage);
                }
            }
            if (options.clipstrip) {
                viewgroup.clipstrip = new Clipstripper();
                viewgroup.clipstrip.attachView(viewgroup.view);
            }
            if (options.hasOwnProperty('clipplay') && options.clipplay) {
                viewgroup.clipplay = new Clipplayer();
                viewgroup.clipplay.attachView(viewgroup.view);
            }
        };
        if (Sherd.Video.YouTube) {
            var youtube = this.settings.youtube = {
                'view': new Sherd.Video.YouTube()
            };
            decorateVideo(options, youtube);
        }
        if (Sherd.Video.Flowplayer) {
            var flowplayer = this.settings.flowplayer = {'view': new Sherd.Video.Flowplayer() };
            decorateVideo(options, flowplayer);
        }
        if (Sherd.Video.Videotag) {
            var videotag = this.settings.videotag = {'view': new Sherd.Video.Videotag() };
            decorateVideo(options, videotag);
        }
        if (Sherd.Video.Vimeo) {
            var vimeo = this.settings.vimeo = {'view': new Sherd.Video.Vimeo() };
            decorateVideo(options, vimeo);
        }
    } /*end Video*/
    if (Sherd.Image && Sherd.Image.OpenLayers) {
        var image = {
            'view' : new Sherd.Image.OpenLayers()
        };
        if (options.clipform) {
            image.clipform = new Sherd.Image.Annotators.OpenLayers();
            image.clipform.attachView(image.view);
            if (options.storage) {
                image.clipform.addStorage(options.storage);
            }
        }
        this.settings.image = image;
    }
    if (Sherd.Image && Sherd.Image.FSIViewer) {
        var fsi = {
            'view' : new Sherd.Image.FSIViewer()
        };
        if (options.clipform) {
            fsi.clipform = new Sherd.Image.Annotators.FSIViewer();
            fsi.clipform.attachView(fsi.view);
            if (options.storage) {
                fsi.clipform.addStorage(options.storage);
            }
        }
        this.settings.fsiviewer = fsi;
    }

    if (Sherd.Pdf && Sherd.Pdf.PdfJS) {
        const pdf = {
            'view': new Sherd.Pdf.PdfJS()
        };

        if (options.clipform) {
            pdf.clipform = new Sherd.Pdf.Annotators.Pdf();
            pdf.clipform.attachView(pdf.view);

            if (options.storage) {
                pdf.clipform.addStorage(options.storage);
            }
        }

        this.settings.pdf = pdf;
    } else {
        console.error('Error loading Sherd.Pdf view!');
    }

    this.settings.NONE = {
        view: {
            html: {
                remove: function() {},
                push: function() {}
            },
            setState: function() {},
            getState: function() {},
            queryformat: {
                find: function() {}
            }
        }
    };
    this.settings.NONE.clipform = this.settings.NONE.view;
    this.settings.NONE.clipstrip = this.settings.NONE.view;
    // //API
    var current_type = false;
    this.html = {
        remove: function() {
            if (current_type) {
                self.settings[current_type].view.html.remove();
                if (self.clipstrip) {
                    self.clipstrip.html.remove();
                    self.clipstrip = null;
                }
                current_type = false;
            }
        },
        push: function(htmlDom, options) {
            if (options.asset && options.asset.type &&
                (options.asset.type in self.settings)) {

                if (current_type) {
                    if (current_type !== options.asset.type) {
                        self.html.remove();
                    }
                }

                current_type = options.asset.type;

                // /the main pass
                var cur = self.settings[current_type];
                cur.view.html.push(htmlDom, options);

                if (cur.clipform) {
                    self.clipform = cur.clipform;
                }
                if (cur.clipplay) {
                    cur.clipplay.html.push(options.targets.clipplay, {
                        asset: {}
                    });
                    self.clipplay = cur.clipplay;
                }
                if (cur.clipstrip) {
                    var target = 'clipstrip-display'; //default
                    if (options.targets && options.targets.clipstrip) {
                        target = options.targets.clipstrip;
                    } else if (self.options.targets &&
                               self.options.targets.clipstrip) {
                        target = self.options.targets.clipstrip;
                    }
                    cur.clipstrip.html.push(target, {
                        asset: {}
                    });
                    self.clipstrip = cur.clipstrip;
                }
            } else {
                if (window.console) {
                    window.console.error(options);
                    window.console.error(self.settings);
                }
                throw new Error(
                    'Your asset does not have a (supported) type marked.');
            }
        }
    };
    this.setState = function() {
        if (current_type) {
            var cur = self.settings[current_type];
            //special JS magic -- set this == view
            cur.view.setState.apply(cur.view, arguments);
            if (self.clipstrip) {
                self.clipstrip.setState.apply(self.clipstrip, arguments);
            }
            if (self.clipplay) {
                self.clipplay.setState.apply(self.clipplay, arguments);
            }
        }
    };
    this.getState = function() {
        if (current_type) {
            return self.settings[current_type].view.getState.apply(
                //special JS magic -- this == view
                self.settings[current_type].view, arguments
            );
        }
    };
    this.queryformat = {
        find: function(str) {
            if (self.settings[current_type].view.queryformat &&
                self.settings[current_type].view.queryformat.find) {
                return self.settings[current_type].view.queryformat.find(str);
            } else {
                return [];
            }
        }
    };
    this.layer = function() {
        if (self.settings[current_type].view.Layer) {
            return new self.settings[current_type].view.Layer();
        } else if (self.clipstrip && self.clipstrip.Layer) {
            return new self.clipstrip.Layer();
        }
    };
};

if (!window.Sherd.GenericAssetView) {
    window.Sherd.GenericAssetView = GenericAssetView;
}
