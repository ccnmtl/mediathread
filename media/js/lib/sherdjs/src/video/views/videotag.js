/*
Documentation:

  SERIALIZATION of asset
       {url:''
	,width:320
	,height:260
	,autoplay:'false'
	,controller:'true'
	,errortext:'Error text.'
	,type:'video/ogg'
	};
  ISSUES:
     2010/August/26:
     Firefox does not have .seekable implemented
     There is no 'canseek' event.
     WebKit (Chrome) does not trigger 'progress' event, but triggers 'canplaythrough' like progress
     Would be nice to know if a particular event is supported (maybe even per-object)
 */
if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.Videotag) {
    Sherd.Video.Videotag = function () {
        var self = this;
        Sherd.Video.Base.apply(this, arguments); //inherit off video.js - base.js

        ////////////////////////////////////////////////////////////////////////
        // Microformat
        this.microformat.create = function (obj, doc) {
            var wrapperID = Sherd.Base.newID('videotag-wrapper-');
            var playerID = Sherd.Base.newID('videotag-player-');
            var controllerID = Sherd.Base.newID('videotag-controller-');

            var supported = self.microformat._getPlayerParams(obj);
            if (supported) {
                if (!obj.options) {
                    obj.options = {
                        width: (obj.presentation === 'small' ? 320 : (obj.width || 475)),
                        height: (obj.presentation === 'small' ? 240 : (obj.height || 336))
                    };
                }
                var create_obj = {
                    object: obj,
                    htmlID: wrapperID,
                    playerID: playerID, // Used by .initialize post initialization
                    text: '<div id="' + wrapperID + '" class="sherd-videotag-wrapper sherd-video-wrapper" ' +
                    '     style="width:' + obj.options.width + 'px">' +
                    '<video id="' + playerID + '" controls="controls"' +
                    ((obj.poster) ? ' poster="' + obj.poster + '" ' : '') +
                    '       height="' + obj.options.height + '" width="' + obj.options.width + '"' +
                    '       type=\'' + supported.mimetype + '\'' +
                    '       src="' + supported.url + '">' +
                    '</video>' +
                    '</div>',
                    provider: supported.provider
                };
                return create_obj;
            }
        };
        this.microformat._getPlayerParams = function (obj) {
            var types = {
                ogg: 'video/ogg; codecs="theora, vorbis"',
                webm: 'video/webm; codecs="vp8, vorbis"',
                mp4: 'video/mp4; codecs="avc1.42E01E, mp4a.40.2"'
            };
            var vid = document.createElement('video');
            var browser_supported = [];
            for (var a in types) {
                if (types.hasOwnProperty(a)) {
                    switch (vid.canPlayType(types[a])) {
                    case 'probably':
                        browser_supported.unshift(a);
                        break;
                    case 'maybe':
                        browser_supported.push(a);
                        break;
                    }
                }
            }
            for (var i = 0; i < browser_supported.length; i++) {
                if (obj[browser_supported[i]]) {
                    return {
                        'provider': browser_supported[i],
                        'url': obj[browser_supported[i]],
                        'mimetype': types[browser_supported[i]]
                    };
                }
            }
        };
        this.microformat.components = function (html_dom, create_obj) {
            try {
                var rv = {};
                if (html_dom) {
                    rv.wrapper = html_dom;
                }
                if (create_obj) {
                    rv.player = html_dom.getElementsByTagName('video')[0];
                    rv.width = (create_obj.options && create_obj.options.width) || rv.player.offsetWidth;
                    rv.mediaUrl = create_obj.object[create_obj.provider];
                }
                return rv;
            } catch (e) {}
            return false;
        };

        // Find the objects based on the individual player properties in the DOM
        // Works in conjunction with read
        this.microformat.find = function (html_dom) {
            throw new Error("unimplemented");
            //var found = [];
            //return found;
        };

        // Return asset object description (parameters) in a serialized JSON format.
        // Will be used for things like printing, or spitting out a description.
        // works in conjunction with find
        this.microformat.read = function (found_obj) {
            throw new Error("unimplemented");
        };

        this.microformat.type = function () { return 'videotag'; };

        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            var supported = self.microformat._getPlayerParams(obj);
            if (supported && self.components.player) {
                try {
                    self.components.player.type = supported.mimetype;
                    self.components.player.src = supported.url;
                    self.components.mediaUrl = supported.url;
                    return true;
                } catch (e) {}
            }
            return false;
        };


        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides

        this.initialize = function (create_obj) {
            self.events.connect(self, 'seek', self.media.playAt);
            self.events.connect(self, 'playclip', function (obj) {
                self.setState(obj);
                self.media.play();
            });
            if (self.components.player) {
                var signal_duration = function () {
                    self.events.signal(self, 'duration', { duration: self.media.duration() });
                };
                if (self.media.duration() > 0) {
                    signal_duration();
                } else {
                    self.events.connect(self.components.player, 'loadedmetadata', signal_duration);
                }
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            var duration = 0;
            if (self.components.player) {
                duration = self.components.player.duration || 0;
            }
            return duration;
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

        // Used by tests
        this.media.isPlaying = function () {
            return (self.components.player && !self.components.player.paused);
        };

        this.media.ready = function () {
            ///http://www.whatwg.org/specs/web-apps/current-work/multipage/video.html#dom-media-have_metadata
            return (self.components.player && self.components.player.readyState > 2);
        };

        this.media.seek = function (starttime, endtime, autoplay) {
            if (self.components.player) {
                var c, d = {}; //event listeners
                var _seek = function (evt) {
                    if (starttime !== undefined) {
                        try {
                            self.components.player.currentTime = starttime;
                            if (d.disconnect) {
                                d.disconnect();
                            }
                        } catch (e) {
                            return { error: true };
                        }
                    }
                    if (endtime) {
                        self.media.pauseAt(endtime);
                    }
                    if (autoplay || self.components.autoplay) {
                        self.media.play();
                    }
                    return {};
                };
                if (_seek().error) {
                    var progress_triggers = 0;
                    d = self.events.connect(self.components.player, 'progress', function (evt) {
                        progress_triggers = 1;
                        _seek(evt);
                    });
                    ///WebKit(Chrome) doesn't trigger progress, but 'canplaythrough' seems to trigger enough
                    c = self.events.connect(self.components.player, 'canplaythrough', function (evt) {
                        if (progress_triggers === 1) {
                            c.disconnect();
                        } else {
                            if (!(progress_triggers--)) {
                                d.disconnect();
                            }
                            d = c;
                            _seek(evt);
                        }
                    });
                }
            }
        };

        this.media.time = function () {
            return (!self.components.player || self.components.player.currentTime);
        };

        this.media.timescale = function () {
            return 1;
        };

        this.media.timestrip = function () {
            var w = self.components.player.width;
            return {w: w,
                trackX: 40,
                trackWidth: w - 140,
                visible: true
            };
        };

        //returns true, if we're sure it is. Not currently used
        this.media.isStreaming = function () {
            return false;
        };

        // Used by tests.
        this.media.url = function () {
            return self.components.mediaUrl;
        };

    }; //Sherd.Video.Videotag

}