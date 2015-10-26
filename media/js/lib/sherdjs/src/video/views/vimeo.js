/*
  Support for the Vimeo js-enabled player.  documentation at:
  http://vimeo.com/api/docs/oembed
  http://http://vimeo.com/api/docs/player-js

  Signals:
  duration: signals duration change

  Listens For:
  seek: seek to a particular starttime
 */

if (!Sherd) {Sherd = {}; }
if (!Sherd.Video) {Sherd.Video = {}; }
if (!Sherd.Video.Vimeo) {
    Sherd.Video.Vimeo = function () {
        var self = this;

        Sherd.Video.Base.apply(this, arguments); //inherit -- video.js -- base.js

        this.state = {
            starttime: 0,
            endtime: 0,
            seeking: false
        };

        this.presentations = {
            'small': {
                width: function () { return 310; },
                height: function () { return 220; }
            },
            'medium': {
                width: function () { return 475; },
                height: function () { return 336; }
            },
            'default': {
                width: function () { return 620; },
                height: function () { return 440; }
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Microformat

        // create == asset->{html+information to make it}
        this.microformat.create = function (obj) {
            var wrapperID = Sherd.Base.newID('vimeo-wrapper-');
            var playerID = Sherd.Base.newID('vimeo_player_');
            var autoplay = obj.autoplay ? 1 : 0;
            self.media._ready = false;

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

            // For IE, the id needs to be placed in the object.
            // For FF, the id needs to be placed in the embed.
            var objectID = '';
            var embedID = '';
            if (window.navigator.userAgent.indexOf("MSIE") > -1) {
                objectID = 'id="' + playerID + '"';
            } else {
                embedID = 'id="' + playerID + '"';
            }

            var bits = obj.vimeo.split('/');
            var clipId = bits[bits.length - 1];

            var embedCode = '<div id="' + wrapperID + '" class="sherd-vimeo-wrapper">' +
                '  <object width="' + obj.options.width + '" height="' + obj.options.height + '" ' +
                '          classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" ' + objectID + '>' +
                '  <param name="movie" value="http://vimeo.com/moogaloop.swf"></param>' +
                '  <param name="allowscriptaccess" value="always"/></param>' +
                '  <param name="autoplay" value="' + autoplay + '"></param>' +
                '  <param name="width" value="' + obj.options.width + '"></param>' +
                '  <param name="height" value="' + obj.options.height + '"></param>' +
                '  <param name="allowfullscreen" value="true"></param>' +
                '  <param name="flashvars" value="autoplay=0&amp;loop=0&amp;clip_id=' + clipId + '&amp;color=0&amp;fullscreen=1&amp;server=vimeo.com&amp;show_byline=1&amp;show_portrait=1&amp;show_title=1&amp;js_api=1">' +
                '  <embed ' + embedID + ' width="' + obj.options.width + '" height="' + obj.options.height + '" type="application/x-shockwave-flash"' +
                '     src="http://vimeo.com/moogaloop.swf" allowscriptaccess="always" allowfullscreen="true" flashvars="autoplay=' + autoplay + '&amp;loop=0&amp;clip_id=' + clipId + '&amp;color=0&amp;fullscreen=1&amp;server=vimeo.com&amp;show_byline=1&amp;show_portrait=1&amp;show_title=1&amp;js_api=1">' +
                '  </embed>' +
                '</object></div>';

            return {
                options: obj.options,
                htmlID: wrapperID,
                playerID: playerID,
                autoplay: autoplay, // Used later by _seek seeking behavior
                mediaUrl: obj.vimeo, // Used by _seek seeking behavior
                text: embedCode,
                object: obj
            };
        };

        // self.components -- Access to the internal player and any options needed at runtime
        this.microformat.components = function (html_dom, create_obj) {
            try {
                var rv = {};
                if (html_dom) {
                    rv.wrapper = html_dom;
                }
                if (create_obj) {
                    rv.autoplay = create_obj.autoplay;
                    rv.mediaUrl = create_obj.mediaUrl;
                    rv.playerID = create_obj.playerID;
                    rv.width = create_obj.options.width;
                    rv.height = create_obj.options.height;
                    rv.itemId = create_obj.object.id;
                    rv.primaryType = create_obj.object.primary_type;                    
                }
                return rv;
            } catch (e) {}
            return false;
        };

        // Return asset object description (parameters) in a serialized JSON format.
        // NOTE: Not currently in use. Will be used for things like printing, or spitting out a description.
        this.microformat.read = function (found_obj) {
            var obj = {};
            var params = found_obj.html.getElementsByTagName('param');
            for (var i = 0; i < params.length; i++) {
                obj[params[i].getAttribute('name')] = params[i].getAttribute('value');
            }
            obj.mediaUrl = obj.movie;
            return obj;
        };

        this.microformat.type = function () { return 'vimeo'; };

        this.microformat.update = function (obj, html_dom) {
            return obj.vimeo === self.components.mediaUrl && document.getElementById(self.components.playerID) && self.media.ready();
        };

        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides

        window.vimeo_player_progress = function (timing) {
            if (self.state.seeking === true && timing.seconds > 0.5) {
                self.state.seeking = false;
                delete self.state.autoplay;

                if (self.state.starttime !== undefined && self.state.starttime > 0) {
                    self.components.player.api_seekTo(self.state.starttime);
                    delete self.state.starttime;
                }

                if (self.state.endtime !== undefined) {
                    setTimeout(function () {
                        self.media.pauseAt(self.state.endtime);
                        delete self.state.endtime;
                    }, 200);
                }
            }
        };
        
        window.on_vimeo_play = function () {
            jQuery(window).trigger('video.play', [self.components.itemId, self.components.primaryType]);
        };
        
        window.on_vimeo_pause = function () {
            jQuery(window).trigger('video.pause', [self.components.itemId, self.components.primaryType]);
        };
        
        window.on_vimeo_finish = function () {
            jQuery(window).trigger('video.finish', [self.components.itemId, self.components.primaryType]);
        };

        window.vimeo_player_loaded = function (playerID) {
            jQuery(window).trigger('video.create', [self.components.itemId, self.components.primaryType]);
            
            self.components.player = document.getElementById(self.components.playerID);
            self.components.player.api_addEventListener("playProgress", "vimeo_player_progress");
            self.components.player.api_addEventListener("play", "on_vimeo_play");
            self.components.player.api_addEventListener("pause", "on_vimeo_pause");
            self.components.player.api_addEventListener("finish", "on_vimeo_finish");

            // register for notifications from clipstrip to seek to various times in the video
            self.events.connect(self, 'seek', self.media.playAt);

            self.events.connect(self, 'playclip', function (obj) {
                self.setState(obj, { 'autoplay': true });
            });

            var duration = self.media.duration();
            if (duration > 1) {
                self.events.signal(self, 'duration', { duration: duration });
            }

            self.media._ready = true;

            // get out of the "loaded" function before seeking happens
            if (self.state.starttime !== undefined) {
                setTimeout(function () {
                    self.media.seek(self.state.starttime, self.state.endtime, self.state.autoplay);
                }, 100);
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            var duration = 0;
            if (self.components.player) {
                try {
                    duration = self.components.player.api_getDuration();
                    if (duration < 0) {
                        duration = 0;
                    }
                } catch (e) {
                    // media probably not yet initialized
                }
            }
            return duration;
        };

        this.media.pause = function () {
            if (self.components.player) {
                try {
                    self.components.player.api_pause();
                } catch (e) {}
            }
        };

        this.media.play = function () {
            if (self.media.ready) {
                try {
                    self.components.player.api_play();
                } catch (e) {}
            }
        };

        this.media.ready = function () {
            return self.media._ready;
        };

        this.media.isPlaying = function () {
            var playing = false;
            try {
                if (self.components.player) {
                    playing = !self.components.player.api_paused();
                }
            } catch (e) {}
            return playing;
        };

        this.media.seek = function (starttime, endtime, autoplay) {
            if (starttime === undefined || starttime === 0) {
                starttime = 0.1; // don't even ask. 
            }
            // this might need to be a timer to determine "when" the media player is ready
            // it's working differently from initial load to the update method
            if (!self.media.ready()) {
                // executes on player_ready
                self.state.starttime = starttime;
                self.state.endtime = endtime;
                self.state.autoplay = autoplay;
            } else if (autoplay) {
                // executes on player_progress
                self.state.starttime = starttime;
                self.state.endtime = endtime;
                self.state.seeking = true;

                if (!self.media.isPlaying()) {
                    if (self.components.player.api_play) {
                        self.components.player.api_play();
                    }
                }
            } else if (self.media.isPlaying() || self.state.seeking || self.state.autoplay) {
                // executes immediately
                if (starttime !== undefined && starttime > 0) {
                    if (self.components.player.api_seekTo) {
                        self.components.player.api_seekTo(starttime);
                    }
                }

                if (endtime !== undefined) {
                    setTimeout(function () {
                        self.media.pauseAt(endtime);
                    }, 200);
                }

                delete self.state.starttime;
                delete self.state.endtime;
                delete self.state.autoplay;
                self.state.seeking = false;
            }
        };

        this.media.time = function () {
            var time = 0;
            if (self.components.player) {
                try {
                    time = self.components.player.api_getCurrentTime();
                    if (time < 0) {
                        time = 0;
                    }
                } catch (e) {
                    // media probably not yet initialized
                }
            }
            return time;
        };

        this.media.timestrip = function () {
            var w = self.components.width;
            return {
                w: w,
                trackX: 96,
                trackWidth: w - 283,
                visible: true
            };
        };

        // Used by tests. Might be nice to refactor state out so that
        // there's a consistent interpretation across controls
        this.media.state = function () {
            return 0;
        };

        this.media.url = function () {
            return self.components.player.api_getVideoUrl();
        };
    };
}