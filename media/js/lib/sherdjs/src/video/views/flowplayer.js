/* global Sherd: true, flowplayer: true, $f: true */
/*
 * Using Flowplayer to support the flash video and mp4 formats
 * Support for the Flowplayer js-enabled player.  documentation at:
 * http://flowplayer.org/doc    umentation/api/index.html
 *
 * Example Files:
 *
 * Pseudostreaming Flv
 * file: http://vod01.netdna.com/vod/demo.flowplayer/Extremists.flv
 *
 * Pseudostreaming Mp4
 * file: http://content.bitsontherun.com/videos/LJSVMnCF-327.mp4
 * queryString: ?starttime=${start}
 *
 * RTMP Flv
 * rtmp://vod01.netdna.com/play//vod/demo.flowplayer/metacafe.flv
 *
 * RTMP Mp4
 * rtmp://uis-cndls-3.georgetown.edu:1935/simplevideostreaming//mp4:clayton.m4v
 */
if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.Flowplayer && Sherd.Video.Base) {
    Sherd.Video.Flowplayer = function () {
        var self = this;
        
        this.state = {
            starttime: 0,
            endtime: 0
        };

        Sherd.Video.Base.apply(this, arguments); // inherit -- video.js -- base.js
        
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
            
            var create_obj = {
                object: obj,
                htmlID: wrapperID,
                playerID: playerID, // Used by .initialize post initialization
                timedisplayID: 'timedisplay' + playerID,
                currentTimeID: 'currtime' + playerID,
                durationID: 'totalcliplength' + playerID,
                playerParams: params,
                text: '<div class="flowplayer-timedisplay" id="timedisplay' + playerID + '" style="visibility:hidden;"><span id="currtime' + playerID + '">00:00:00</span>/<span id="totalcliplength' + playerID + '">00:00:00</span></div><div id="' + wrapperID + '" class="sherd-flowplayer-wrapper sherd-video-wrapper">' +
                      '<div class="sherd-flowplayer"' +
                           'style="display:block; width:' + obj.options.width + 'px;' +
                           'height:' + obj.options.height + 'px;" id="' + playerID + '">' +
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
                    rv.timedisplay = document.getElementById(create_obj.timedisplayID);
                    rv.elapsed = document.getElementById(create_obj.currentTimeID);
                    rv.duration = document.getElementById(create_obj.durationID);
                    rv.lastDuration = 0;
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
        
        // Find the objects based on the individual player properties in the DOM
        // NOTE: Not currently in use.
        this.microformat.find = function (html_dom) {
            var found = [];
            //SNOBBY:not embeds, since they're in objects--and not xhtml 'n' stuff
            var objects = ((html_dom.tagName.toLowerCase() === 'object') ?
                [html_dom] : html_dom.getElementsByTagName('object')
                //function is case-insensitive in IE and FFox,at least
            );
            for (var i = 0; i < objects.length; i++) {
                if (objects[i].getAttribute('id').search('flowplayer-player')) {
                    found.push({'html': objects[i]});
                }
            }
            return found;
        };
        
        // Return asset object description (parameters) in a serialized JSON format.
        // NOTE: Not currently in use. Will be used for things like printing, or spitting out a description.
        // Should be tested when we get there.
        this.microformat.read = function (found_obj) {
            var obj = {};
            var params = found_obj.html.getElementsByTagName('param');
            for (var i = 0; i < params.length; i++) {
                obj[params[i].getAttribute('name')] = params[i].getAttribute('value');
            }
            return obj;
        };
        
        this.microformat.type = function () { return 'flowplayer'; };
        
        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            var rc = false;
            var newUrl = self.microformat._getPlayerParams(obj);
            if (newUrl.url && document.getElementById(self.components.playerID) && self.media.state() > 0) {
                var playlist = self.components.player.getPlaylist();
                if (playlist[0].url === newUrl.url) {
                    // If the url is the same as the previous, just seek to the right spot.
                    // This works just fine.
                    rc = true;
                    delete self.state.starttime;
                    delete self.state.endtime;
                    delete self.state.last_pause_time;
                }
            }
            return rc;
        };
        
        this.microformat._getPlayerParams = function (obj) {
            var rc = {};
            if (obj.mp4_rtmp) {
                var a = self.microformat._parseRtmpUrl(obj.mp4_rtmp);
                rc.url = a.url;
                rc.netConnectionUrl = a.netConnectionUrl;
                rc.provider = 'rtmp';
            } else if (obj.flv_rtmp) {
                var rtmp = self.microformat._parseRtmpUrl(obj.flv_rtmp);
                rc.url = rtmp.url;
                rc.netConnectionUrl = rtmp.netConnectionUrl;
                rc.provider = 'rtmp';
            } else if (obj.flv_pseudo) {
                rc.url = obj.flv_pseudo;
                rc.provider = 'pseudo';
            } else if (obj.mp4_pseudo) {
                rc.url = obj.mp4_pseudo;
                rc.provider = 'pseudo';
            } else if (obj.mp4) {
                rc.url = obj.mp4;
                rc.provider = '';
            } else if (obj.flv) {
                rc.url = obj.flv;
                rc.provider = '';
            } else if (obj.video_pseudo) {
                rc.url = obj.video_pseudo;
                rc.provider = 'pseudo';
            } else if (obj.video_rtmp) {
                var video_rtmp = self.microformat._parseRtmpUrl(obj.video_rtmp);
                rc.url = video_rtmp.url;
                rc.netConnectionUrl = video_rtmp.netConnectionUrl;
                rc.provider = 'rtmp';
            } else if (obj.video) {
                rc.url = obj.video;
                rc.provider = '';
            } else if (obj.mp3) {
                rc.url = obj.mp3;
                rc.provider = 'audio';
            } else if (obj.mp4_audio) {
                rc.url = obj.mp4_audio;
                rc.provider = 'pseudo';
            }
            if (rc.provider === 'pseudo' && /\{start\}/.test(rc.url)) {
                var pieces = rc.url.split('?');

                // Bookmarklet bug in the JWPlayer scraping code led to
                // a lot of assets being added without the required $ 
                // in front of the start variable. This is a little patch 
                // so we don't have to redo all the asset primary sources at once.
                var queryString = pieces.pop();
                if (queryString === 'start={start}') {
                    queryString = 'start=${start}';
                }
                rc.queryString = encodeURI('?' + queryString);
                rc.url = pieces.join('?');
            }
            return rc;
        };
        
        // expected format: rtmp://uis-cndls-3.georgetown.edu:1935/simplevideostreaming//mp4:clayton.m4v
        this.microformat._parseRtmpUrl = function (url) {
            var rc = {};
            
            var idx = url.lastIndexOf('//');
            rc.netConnectionUrl = url.substring(0, idx);
            rc.url = url.substring(idx + 2, url.length);
            
            return rc;
        };
        
        this.microformat._queueReadyToSeekEvent = function () {
            self.events.queue('flowplayer ready to seek', [
                {
                    test: function () {
                        // Is the player ready yet?
                        if (self.media.state() > 2) {
                            if (self.media.duration() > 0) {
                                return true;
                            }
                        }
                        return (self.media.state() > 2 && self.media.duration() > 0);
                    },
                    poll: 500
                },
                {
                    call: function () {
                        self.events.signal(self/*==view*/, 'duration', { duration: self.media.duration() });
                        self.setState({ start: self.state.starttime, end: self.state.endtime});
                    }
                }
            ]);
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
                    clip: {
                        scaling: "fit",
                        // these are the common clip properties & event handlers
                        // they (theoretically) apply to all the clips
                        onSeek: function (clip, target_time) {
                            self.state.last_pause_time = target_time;
                        },
                        onStart: function () {
                            jQuery(window).trigger('video.play', [self.components.itemId, self.components.primaryType]);
                            self.connect_tickcount();
                        },
                        onResume: function () {
                            jQuery(window).trigger('video.play', [self.components.itemId, self.components.primaryType]);
                            self.connect_tickcount();
                        },
                        onPause: function (clip) {
                            self.state.last_pause_time = self.components.player.getTime();
                            jQuery(window).trigger('video.pause', [self.components.itemId, self.components.primaryType]);
                            self.disconnect_tickcount();
                            self.disconnect_pause();
                        },
                        onFinish: function () {
                            jQuery(window).trigger('video.finish', [self.components.itemId, self.components.primaryType]);
                            self.disconnect_tickcount();
                            self.disconnect_pause();
                        }
                    },
                    plugins: {
                        controls: {
                            autoHide: false,
                            volume: true,
                            mute: true,
                            time: false,
                            fastForward: false,
                            fullscreen: true
                        }
                    },
                    playlist: [{
                        url: create_obj.playerParams.url,
                        autoPlay: create_obj.object.autoplay ? true : false
                        //provider: added below conditionally
                    }]
                };
                if (create_obj.playerParams.provider) {
                    options.playlist[0].provider = create_obj.playerParams.provider;
                }
                
                if (create_obj.staticDuration) {
                    options.clip.duration = create_obj.staticDuration;
                }
                
                if (create_obj.playerParams.provider === "audio") {
                    options.plugins.audio = { url: flowplayer.audio_plugin};
                } else {
                    options.plugins.pseudo = { url: flowplayer.pseudostreaming_plugin};
                    options.plugins.rtmp = { url: flowplayer.rtmp_plugin};
                }
                
                if (create_obj.object.poster) {
                    options.clip.coverImage = { url: create_obj.object.poster, scaling: 'orig' };
                } else if (create_obj.playerParams.provider === "audio") {
                    options.clip.coverImage = { url: "http://mediathread.ccnmtl.columbia.edu/media/img/poster_audio.png", scaling: 'orig' };
                }
                
                if (create_obj.playerParams.provider === 'pseudo') {
                    ///TODO: when we can do update() we'll need to make each clip
                    ///      with its own plugin and load them with player.loadPluginWithConfig()
                    if (create_obj.playerParams.queryString) {
                        options.plugins.pseudo.queryString = create_obj.playerParams.queryString;
                    }
                }
                
                if (create_obj.playerParams.provider === 'rtmp') {
                    if (create_obj.playerParams.netConnectionUrl) {
                        options.playlist[0].netConnectionUrl = create_obj.playerParams.netConnectionUrl;
                    }
                }
                
                jQuery(window).trigger('video.create', [self.components.itemId, self.components.primaryType]);
                
                flowplayer(create_obj.playerID,
                           flowplayer.swf_location,
                           options);
    
                // Save reference to the player
                if (typeof $f === 'function') {
                    self.components.player = $f(create_obj.playerID);
                }
                self.components.provider = create_obj.playerParams.provider;
                
                // Setup timers to watch for readiness to seek/setState
                self.microformat._queueReadyToSeekEvent();
                
                // register for notifications from clipstrip to seek to various times in the video
                self.events.connect(self, 'seek', self.media.playAt);
                self.events.connect(self, 'duration', function (obj) {
                    self.components.timedisplay.style.visibility = 'visible';
                    self.components.duration.innerHTML = self.secondsToCode(obj.duration);
                });
                self.events.connect(self, 'playclip', function (obj) {
                    // Call seek directly
                    self.components.player.seek(obj.start);
                    
                    // There's a slight race condition between seeking to the start and pausing.
                    // If the new endtime is less than the old endtime, the pauseAt timer returns true immediately
                    // Getting around this by delaying pause call for a few millis
                    // Play likewise gets a little messed up if the previous clip is still around. So, delaying that too.
                    setTimeout(function () {
                        if (!self.media.isPlaying()) {
                            self.media.play();
                        }
                        if (obj.end) {
                            self.media.pauseAt(obj.end);
                        }
                    }, 750);
                });
                self.connect_tickcount();
            }
        };
        
        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            var duration = 0;
            if (self.components.staticDuration) {
                // Audio has major issues resolving duration. Pick up statically
                // described duration metadata if available.
                duration = self.components.staticDuration;
            } else if (self.components.player && self.components.player.isLoaded()) {
                var fullDuration = self.components.player.getPlaylist()[0].fullDuration;
                if (fullDuration) {
                    duration = fullDuration;
                    
                    if (self.components.lastDuration !== fullDuration) {
                        // signal the change
                        self.events.signal(self/*==view*/, 'duration', { duration: fullDuration });
                        self.components.lastDuration = fullDuration;
                    }
                }
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

        this.media.isPlaying = function () {
            var playing = false;
            try {
                playing = (self.media.state() === 3);
            } catch (e) {}
            return playing;
        };
        
        this.media.ready = function () {
            var ready = false;
            try {
                ready = self.media.state() > 2;
            } catch (e) {
            }
            return ready;
        };
        
        this.media.seek = function (starttime, endtime, autoplay) {
            // Reset the saved duration
            self.components.lastDuration = 0;
            
            if (!self.media.ready()) {
                self.state.starttime = starttime;
                self.state.endtime = endtime;
            } else {
                if (starttime !== undefined) {
                    self.components.player.seek(starttime);
                }
                
                if (endtime) {
                    self.media.pauseAt(endtime);
                }
                
                // clear any saved values if they exist
                delete self.state.starttime;
                delete self.state.endtime;
                
                // Delay the play for a few milliseconds
                // We need a little time for Flowplayer to process the seek
                // before play occurs. Otherwise, the player just
                // starts from the beginning of the clip and ignores the seek
                if ((autoplay || self.components.autoplay) && self.media.state() !== 3) {
                    setTimeout(function () {
                        self.media.play();
                    }, 100);
                }
            }
        };
        
        this.media.time = function () {
            var time = ((self.media.isPlaying()) ?
                        self.components.player.getTime()
                        : self.state.last_pause_time || 0
                       );
            if (time < 1) {
                time = 0;
            }
            return time;
        };
        
        this.media.timestrip = function () {
            // The clipstrip is calibrated to the flowplayer scrubber
            // Visually, it looks a little "short", but trust, it tags along
            // with the circle shaped thumb properly.
            var w = self.components.width;
            return {w: w,
                    trackX: 47,
                    trackWidth: w - 185,
                    visible: true
                   };
        };
        
        /**
        Returns the state of the player. Possible values are:
            -1  unloaded
            0   loaded
            1   unstarted
            2   buffering
            3   playing
            4   paused
            5   ended
        **/
        this.media.state = function () {
            try {
                return ((self.components.player) ? self.components.player.getState() : -1);
            } catch (e) {
                return -1;
            }

        };

    };
}
