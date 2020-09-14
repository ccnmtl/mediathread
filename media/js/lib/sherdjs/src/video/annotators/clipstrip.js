/* global Sherd: true */
//Use Cases:
//Default
//-- starttime:0, endtime:0, duration:0
//-- left/right markers appear together at the 0px position, left-side of player

//Start & Duration
//-- starttime:x, endtime:undefined, duration:y
//-- endtime defaults to starttime -- left/right markers appear together at the start position
//>>> This case is from a queryString start parameter

//Start & End & Duration
//-- startime: x, endtime: y, duration: z
//-- Markers appear at start/end times appropriately

//Listens for:
//duration: changes in duration from the movie player. Some players don't get duration until playback begins
//the clipstrip will resize itself appropriately when the correct data is received.

//clipstart: changes in the clipstart from the clipform
//clipend: changes in the clipend from the clipform

//Signals:
//seek: when a user clicks on the start/end time of the clipstrip, sends a seek event out



if (!Sherd) {Sherd = {}; }
if (!Sherd.Video) {Sherd.Video = {}; }
if (!Sherd.Video.Annotators) {Sherd.Video.Annotators = {}; }
if (!Sherd.Video.Annotators.ClipStrip) {
    Sherd.Video.Annotators.ClipStrip = function () {
        var self = this;
        var CLIP_MARKER_WIDTH = 7;

        Sherd.Video.Base.apply(this, arguments); //inherit off video.js - base.js

        jQuery(window).resize(function() {
            if (self.components.hasOwnProperty('timestrip')) {
                self.microformat._resize();
            }
        });

        this.attachView = function (view) {
            this.targetview = view;

            // listen for changes in duration from the movie and clipstart/end changes from clipform
            self.events.connect(view, 'duration', self.setClipDuration); //player
            self.events.connect(view, 'clipstart', self.setClipStart); //clipform
            self.events.connect(view, 'clipend', self.setClipEnd); //clipform
        };

        this.getState = function () {
            var obj = {};

            obj.starttime = self.components.starttime;
            obj.endtime = self.components.endtime;
            obj.duration = self.components.duration;
            obj.timestrip = self.components.timestrip;
            return obj;
        };

        this.setState = function (obj) {
            if (typeof obj === 'object') {
                var c = self.components;
                if (obj === null) {
                    c.starttime = c.endtime = c.duration = 0;
                } else {
                    c.starttime = obj.start || 0;
                    c.endtime = obj.end || c.starttime;

                    if (obj.duration > 1) {
                        c.duration = obj.duration;
                        self.microformat._resize();
                    } else {
                        self.events.queue('quicktime has duration',
                                [{test: function () {
                                    return self.targetview.media.duration();
                                },
                                poll: 500
                                },
                                {call: function () {
                                    c.duration = self.targetview.media.duration();
                                    self.microformat._resize();
                                }
                                }]);
                    }
                }
                return true;
            }
        };

        // Event Listener: duration - from player
        // Assumes start & end times have been initialized through setState or are defaulted
        this.setClipDuration = function (obj) {
            if (obj.duration > 1) {
                self.components.duration = obj.duration;
                self.microformat._resize();
            }
        };

        // Event Listener: clipstart - from clipform
        // Assumes self.components.duration has been initialized either through setState or setClipDuration
        this.setClipStart = function (obj) {
            if (typeof obj.start !== 'undefined' && self.components.duration) {
                self.components.starttime = obj.start;
                self.microformat._resize();
            }
        };

        // Event Listener: clipend - from clipform
        // Assumes self.components.duration has been initialized
        this.setClipEnd = function (obj) {
            if (obj.end !== undefined && self.components.duration) {
                self.components.endtime = obj.end;
                self.microformat._resize();
            }
        };

        this.initialize = function (create_obj) {
            self.events.connect(self.components.clipStartMarker, 'click', function (evt) {
                self.events.signal(self.targetview, 'seek', self.components.starttime);
            });
            self.events.connect(self.components.clipEndMarker, 'click', function (evt) {
                self.events.signal(self.targetview, 'seek', self.components.endtime);
            });
            self.events.connect(self.components.clipRange, 'click', function (evt) {
                var obj = self.getState();
                self.events.signal(self.targetview, 'playclip', { start: obj.starttime, end: obj.endtime });
            });


            // setup the clip markers in the default position
            self.microformat._resize();
        };

        this.deinitialize = function () {
            self.events.clearTimers();
        };

        this.microformat.create = function (obj) {
            var htmlID = 'clipStrip';
            var timestrip = self.targetview.media.timestrip();
            return {
                htmlID: htmlID,
                timestrip: timestrip,
                text: '<div id="clipStrip" style="width: ' + timestrip.w + 'px">' +
                    '<div id="clipStripTrack"  style="width: ' + timestrip.trackWidth + 'px; left: ' + timestrip.trackX + 'px">' +
                            '<div id="clipStripStart" class="clipSlider" onmouseover="return escape(\'Go to note start time\')" style="display:none"></div>' +
                            '<div id="clipStripRange" class="clipStripRange" style="display:none"></div>' +
                            '<div id="clipStripEnd" class="noteStripEnd" onmouseover="return escape(\'Go to note end time\')" style="display:none"></div>' +
                        '</div>' +
                    '</div>'
            };
        };

        // self.components -- Access to the internal player and any options needed at runtime
        this.microformat.components = function (html_dom, create_obj) {
            try {
                return {
                    clipStrip: document.getElementById('clipStrip'),
                    clipStartMarker: document.getElementById('clipStripStart'),
                    clipRange: document.getElementById('clipStripRange'),
                    clipEndMarker: document.getElementById('clipStripEnd'),
                    timestrip: create_obj.timestrip,
                    starttime: 0,
                    endtime: 0,
                    duration: 0,
                    layers: {}
                };
            } catch (e) {}
            return false;
        };

        this.microformat._resize = function () {
            self.components.timestrip = self.targetview.media.timestrip();

            jQuery('#clipStrip').css('width', self.components.timestrip.w + 'px');
            jQuery('#clipStripTrack').css('width', self.components.timestrip.trackWidth + 'px');
            jQuery('.clipStripLayer').css('width', self.components.timestrip.trackWidth + 'px');

            var left = self.microformat._timeToPixels(self.components.starttime, self.components.duration, self.components.timestrip.trackWidth);

            var endtime = self.components.endtime > self.components.duration ? self.components.duration : self.components.endtime;

            var right = self.microformat._timeToPixels(endtime, self.components.duration, self.components.timestrip.trackWidth);
            var width = right - left;
            if (width < 0) {
                width = 0;
            }

            self.components.clipStartMarker.style.left = (left - CLIP_MARKER_WIDTH) + 'px';
            self.components.clipEndMarker.style.left = right + 'px';
            self.components.clipRange.style.left = left + "px";
            self.components.clipRange.style.width = width + 'px';

            self.components.clipStartMarker.style.display = 'block';
            self.components.clipRange.style.display = 'block';
            self.components.clipEndMarker.style.display = 'block';

            for (var layerName in self.components.layers) {
                if (self.components.layers.hasOwnProperty(layerName)) {
                    var layer = self.components.layers[layerName];
                    for (var annotationName in layer._anns) {
                        if (layer._anns.hasOwnProperty(annotationName)) {
                            var annotation = layer._anns[annotationName];

                            endtime = annotation.endtime > self.components.duration ? self.components.duration : annotation.endtime;

                            left = self.microformat._timeToPixels(annotation.starttime, self.components.duration, self.components.timestrip.trackWidth);
                            right = self.microformat._timeToPixels(endtime, self.components.duration, self.components.timestrip.trackWidth);
                            width = (right - left);
                            if (width < 0) {
                                width = 0;
                            }

                            jQuery("#" + annotation.htmlID).css("left", left);
                            jQuery("#" + annotation.htmlID).css("width", width);
                        }
                    }
                }
            }
        };

        this.microformat._timeToPixels = function (seconds, duration, width) {
            if (duration > 0) {
                var ratio = width / duration;
                var pos = ratio * seconds;
                return Math.round(Number(pos));
            } else {
                return 0;
            }
        };

        this.Layer = function () {};
        this.Layer.prototype = {
            create: function (name, opts) {
                // create a layer
                this.name = name;
                this.htmlID = 'clipStripLayer_' + name;
                this.title = (opts && opts.title) || this.name;
                this._anns = {};

                var html = '<div class="clipStripLayerContainer" id="' + this.htmlID + '" style="z-index:' + opts.zIndex + '">' +
                    '<div class="clipStripLayerTitle" style="left: ' + (self.components.timestrip.trackX - 98) + 'px">' + this.title + '&nbsp;</div>' +
                    '<div class="clipStripLayer"'  +
                        ' style="left: ' + self.components.timestrip.trackX + 'px; ' +
                        ' width: ' + self.components.timestrip.trackWidth + 'px;">' +
                    '</div>' +
                '</div>';


                // z-index -- An element with greater stack order is always in front of an element with a lower stack order.
                // For ClipStrip, the property is overloaded to mean top to bottom order. greater z-index === higher in the list
                var inserted = false;
                if (opts.zIndex !== undefined) {
                    jQuery(".clipStripLayerContainer").each(function (index, value) {
                        var zindex = jQuery(this).css("z-index");
                        if ((zindex && opts.zIndex > zindex) || (zindex === undefined || zindex === "auto")) {
                            jQuery(this).before(html);
                            inserted = true;
                            return false;
                        }
                    });
                }

                if (!inserted) { // insert at end
                    jQuery("#" + self.components.clipStrip.id).append(html);
                }

                self.components.layers[name] = this;

                if (opts.onmouseenter) {
                    self.onmouseenter = opts.onmouseenter;
                }
                if (opts.onmouseleave) {
                    self.onmouseleave = opts.onmouseleave;
                }
                if (opts.onclick) {
                    self.onclick = opts.onclick;
                }

                return this;
            },
            destroy: function () {
                this.removeAll();
                jQuery("#" + this.htmlID).remove();
                delete self.components.layers[name];
            },
            add: function (ann, opts) {

                if (ann.duration !== undefined && ann.duration > 1 && self.components.duration < 1) {
                    self.components.duration = ann.duration;
                }

                this._anns[opts.id] = { starttime: ann.start, endtime: ann.end, htmlID: this.name + '_annotation_' + opts.id, duration: ann.duration };

                jQuery("#" + this.htmlID).children(".clipStripLayer").append('<div class="annotationLayer" id="' + this._anns[opts.id].htmlID + '"></div>');

                if (opts.color) {
                    jQuery("#" + this._anns[opts.id].htmlID).css("background-color", opts.color);
                }

                jQuery("#" + this._anns[opts.id].htmlID).hover(
                        function enter() {
                            if (self.onmouseenter) {
                                self.onmouseenter(opts.id, this.name);
                            }
                        },
                        function leave() {
                            if (self.onmouseleave) {
                                self.onmouseleave(opts.id, this.name);
                            }
                        }
                );

                jQuery("#" + this._anns[opts.id].htmlID).click(function () {
                    if (self.onclick) {
                        self.onclick(opts.id, this.name);
                    }
                });

                self.microformat._resize();
            },
            remove: function (ann_id) {
                if (ann_id in this._anns) {
                    jQuery("#" + this._anns[ann_id].htmlID).remove();
                    delete this._anns[ann_id];
                }
            },
            removeAll: function () {
                for (var ann_id in this._anns)  {
                    if (this._anns.hasOwnProperty(ann_id)) {
                        this.remove(ann_id);
                        delete this._anns[ann_id];
                    }
                }
            },
            show: function () {
                jQuery("#" + this.htmlID).show();
            },
            hide: function () {
                jQuery("#" + this.htmlID).hide();
            }
        };
    };/* function Sherd.Video.Annotators.ClipStrip() */

}/*if !ClipStrip...*/
