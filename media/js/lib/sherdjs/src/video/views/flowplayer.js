/* global Sherd: true, flowplayer: true */
/*
 * Using Flowplayer to support the flash video and mp4 formats
 * Support for the Flowplayer js-enabled player.  documentation at:
 * https://flowplayer.org/docs/api.html
 *
 *
 */
if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.Flowplayer && Sherd.Video.Base) {
    Sherd.Video.Flowplayer = function () {
        var self = this;

        this.state = {ready: false};

        Sherd.Video.Base.apply(this, arguments); // inherit -- video.js -- base.js

        this.presentations = {
            'small': {
                width: function () { return 310; },
                height: function () { return 233; }
            },
            'medium': {
                width: function () { return 475; },
                height: function () { return 375; }
            },
            'default': {
                width: function () { return 620; },
                height: function () { return 466; }
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Microformat

        // create == asset->{html+information to make it}
        // setup the flowplayer div. will be replaced on write using the flowplayer API
        this.microformat.create = function (obj, doc) {
            var wrapperID = Sherd.Base.newID('flowplayer-wrapper-');
            var playerID = Sherd.Base.newID('flowplayer-player-');
            var params = self.microformat._getPlayerParams(obj);

            if (!obj.options) {
                var presentation;
                switch (typeof obj.presentation) {
                case 'string':
                    presentation = self.presentations[obj.presentation];
                    break;
                case 'object':
                    presentation = obj.presentation;
                    break;
                case 'undefined':
                    presentation = self.presentations['default'];
                    break;
                }

                obj.options = {
                    width: presentation.width(),
                    height: presentation.height()
                };
            }

            var posterUrl = "";
            if (obj.poster) {
                posterUrl = obj.poster;
            } else if (params.provider === "audio") {
                posterUrl = STATIC_URL + "img/poster_audio.png";
            }

            var create_obj = {
                object: obj,
                htmlID: wrapperID,
                playerID: playerID, // Used by .initialize post initialization
                playerParams: params,
                text: '<div id="' + wrapperID + '" class="sherd-flowplayer-wrapper sherd-video-wrapper">' +
                    '<div class="fp-full fp-outlined no-brand sherd-flowplayer no-hover fixed-controls"' +
                          'poster="' + posterUrl + '"' +
                           'style="display:block;" id="' + playerID + '">' +
                    '</div>' +
                    '</div>'
            };

            if (obj.metadata) {
                for (var i = 0; i < obj.metadata.length; i++) {
                    if (obj.metadata[i].key === 'duration') {
                        create_obj.staticDuration = obj.metadata[i].value;
                    }
                }
            }

            return create_obj;
        };

        // self.components -- Access to the internal player and any options needed at runtime
        this.microformat.components = function (html_dom, create_obj) {
            try {
                var rv = {};
                if (html_dom) {
                    rv.wrapper = html_dom;
                }
                if (create_obj) {
                    rv.width = create_obj.object.options.width;
                    rv.playerID = create_obj.playerID;
                    rv.mediaUrl = create_obj.playerParams.url;
                    rv.presentation = create_obj.object.presentation;
                    rv.autoplay = create_obj.object.autoplay ? true : false;
                    rv.itemId = create_obj.object.id;
                    rv.primaryType = create_obj.object.primary_type;

                    if (create_obj.staticDuration) {
                        rv.staticDuration = create_obj.staticDuration;
                    }
                }
                return rv;
            } catch (e) {}
            return false;
        };

        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            var rc = false;
            var newUrl = self.microformat._getPlayerParams(obj);
            if (newUrl.url && document.getElementById(self.components.playerID) && self.media.ready()) {
                if (self.components.player.video.url === newUrl.url) {
                    // If the url is the same as the previous, just seek to the right spot.
                    // This works just fine.
                    rc = true;
                }
            } else {
                self.state.ready = false;
            }
            return rc;
        };
        
        this.microformat._getPlayerParams = function (obj) {
            var rc = {};
            if (obj.mp4_rtmp) {
                var a = self.microformat._parseRtmpUrl(obj.mp4_rtmp);
                rc.url = a.url;
                rc.netConnectionUrl = a.netConnectionUrl;
            } else if (obj.flv_pseudo) {
                rc.url = obj.flv_pseudo;
            } else if (obj.mp4_pseudo) {
                rc.url = obj.mp4_pseudo;
            } else if (obj.mp4) {
                rc.url = obj.mp4;
            } else if (obj.flv) {
                rc.url = obj.flv;
            } else if (obj.video_pseudo) {
                rc.url = obj.video_pseudo;
            } else if (obj.video_rtmp) {
                var video_rtmp = self.microformat._parseRtmpUrl(obj.video_rtmp);
                rc.url = video_rtmp.url;
                rc.netConnectionUrl = video_rtmp.netConnectionUrl;
            } else if (obj.video) {
                rc.url = obj.video;
            } else if (obj.mp3) {
                rc.url = obj.mp3;
            } else if (obj.mp4_audio) {
                rc.url = obj.mp4_audio;
            } else if (obj.mp4_panopto) {
                rc.url = obj.mp4_panopto;
            }
            return rc;
        };
        
        this.microformat.type = function() {
            return 'flowplayer';
        };
        
        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides
        // Post-create step. Overriding here to do a component create using the Flowplayer API
        
        this.disconnect_pause = function() {
            self.events.killTimer('flowplayer pause');  
        };
        
        this.disconnect_tickcount = function() {
          self.events.killTimer('tick count');  
        };

        this.connect_tickcount = function() {
            self.events.queue('tick count', [{
                test : function () {
                    self.components.elapsed.innerHTML =
                        self.secondsToCode(self.media.time());
                    
                    if (self.components.provider === "audio") {
                        self.media.duration();
                    }
                },
                poll: 1000
            }]);  
        };
        
        this.initialize = function (create_obj) {
            if (create_obj) {
                var options = {
                    embed: false,
                    // one video: a one-member playlist
                    playlist: [],
                    splash: false,
                    swf: flowplayer.html5_swf_location
                 };

                 if (create_obj.object.flv || create_obj.object.flv_pseudo) {
                     options.playlist.push([{flv: create_obj.playerParams.url}]);
                 } else {
                     options.playlist.push([{mp4: create_obj.playerParams.url}]);
                 }

                 var elt = jQuery("#" + create_obj.playerID);
                 jQuery(elt).flowplayer(options);

                 jQuery(window).trigger('video.create', [self.components.itemId, self.components.primaryType]);

                // Save reference to the player
                self.components.player = flowplayer(elt);
                self.components.provider = create_obj.playerParams.provider;

                // register for notifications from clipstrip to seek to various times in the video
                self.events.connect(self, 'seek', self.media.playAt);
                self.events.connect(self, 'playclip', function (obj) {
                    self.media.seek(obj.start, obj.end, true);
                });

                self.components.player.bind("ready", function(e, api) {
                    self.state.ready = true;

                    if (self.state.starttime || self.state.autoplay) {
                        self.media.seek(self.state.starttime, self.state.endtime, self.state.autoplay);
                    }

                    if (api.video.src) {
                        var $el = jQuery('<a />', {
                            'href': api.video.src,
                            'title': 'Download video',
                            'download': 'download'
                        });
                        $el.html('<span class="glyphicon glyphicon-floppy-save" ' +
                                 'aria-hidden="true"></span>');
                        var $wrapper = jQuery('.sherd-flowplayer-download-btn');
                        $wrapper.append($el);
                        $wrapper.show();
                    }
                });
                self.components.player.bind("resume", function(e, api) {
                    self.connect_tickcount();
                });
                self.components.player.bind("stop", function(e, api) {
                    self.disconnect_tickcount();
                    self.disconnect_pause();
                });
                self.components.player.bind("pause", function(e, api) {
                    self.disconnect_tickcount();
                    self.disconnect_pause();
                });
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            return self.components.player ?
                self.components.player.video.duration : 0;
        };

        this.media.pause = function () {
            if (self.components.player) {
                self.components.player.pause();
            }
        };

        this.media.play = function () {
            if (self.components.player) {
                self.components.player.play();
            }
        };

        this.media.isPlaying = function () {
            return self.components.player && self.components.player.playing;
        };
        
        this.media.ready = function () {
            return self.state.ready;
        };

        this.media.seek = function (starttime, endtime, autoplay) {
            if (!self.media.ready()) {
                self.state.starttime = starttime;
                self.state.endtime = endtime;
                self.state.autoplay = autoplay;
            } else {
                self.disconnect_pause();
                delete self.state.starttime;
                delete self.state.endtime;
                delete self.state.autoplay;

                if (starttime !== undefined) {
                    self.components.player.seek(starttime, function() {
                        if (autoplay) {
                            self.media.play();
                        }
                        if (endtime) {
                            self.media.pauseAt(endtime);
                        }
                    });
                } else if (autoplay) {
                    self.media.play();
                    if (endtime) {
                        self.media.pauseAt(endtime);
                    }
                }
            }
        };

        this.media.time = function () {
            return self.components.player ? 
                self.components.player.video.time : 0;
        };

        this.media.timestrip = function () {
            // The clipstrip is calibrated to the flowplayer scrubber
            // Visually, it looks a little "short", but trust, it tags along
            // with the circle shaped thumb properly.
            var w = jQuery('#' + self.components.playerID).width();
            return {
                w: w,
                trackX: 2,
                trackWidth: w,
                visible: true
            };
        };
    };
}
