/* global Sherd: true, jwplayer: true */
/*
 * Using Flowplayer 5 to support the flash video and mp4 formats
 * Support for the Flowplayer js-enabled player.  documentation at:
 * https://flowplayer.org/docs/api.html
 *
 *
 */
if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.JWPlayer && Sherd.Video.Base) {
    Sherd.Video.JWPlayer = function () {
        var self = this;
        
        this.state = {ready: false};

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
            var wrapperID = Sherd.Base.newID('jwplayer-wrapper-');
            var playerID = Sherd.Base.newID('jwplayer-player-');
            

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
                playerParams: {'url': obj.mp4_audio},
                text: '<div class="jwplayer-timedisplay" id="timedisplay' + playerID + '" style="visibility:hidden;"><span id="currtime' + playerID + '">00:00:00</span>/<span id="totalcliplength' + playerID + '">00:00:00</span></div><div id="' + wrapperID + '" class="sherd-flowplayer-wrapper sherd-video-wrapper">' +
                      '<div class="sherd-jwplayer"' +
                           'style="display:block; width:' + obj.options.width + 'px;' +
                           'height:' + obj.options.height + 'px;" id="' + playerID + '">' +
                      '</div>' +
                     '</div>'
            };
            
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
                    rv.itemId = create_obj.object.id;
                    rv.primaryType = create_obj.object.primary_type;                    
                }
                return rv;
            } catch (e) {}
            return false;
        };
        
        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            var rc = false;
            var newUrl = obj.mp4_audio;
            if (newUrl && document.getElementById(self.components.playerID) && self.state.ready) {
                var playlist = self.components.player.getPlaylistItem(0);
                if (playlist.file === newUrl) {
                    // If the url is the same as the previous, just seek to the right spot.
                    // This works just fine.
                    rc = true;
                } else {
                    self.components.player.load([{file: newUrl.url}]);
                }
            }
            return rc;
        };
        
        this.microformat.type = function() {
            return 'jwplayer';
        };
        
        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides
        
        this.disconnect_pause = function() {
            self.events.killTimer('jwplayer pause');  
        };
        
        // Post-create step. Overriding here to do a component create using the JWPlayer API
        this.initialize = function (create_obj) {
            if (create_obj) {
                var options = {
                    file: create_obj.playerParams.url,
                    startparam: "start",
                    autostart: create_obj.object.autoplay ? true: false,
                    width: create_obj.object.options.width,
                    height: create_obj.object.options.height
                };

                self.components.player = jwplayer(self.components.playerID).setup(options);
                            
                jQuery(window).trigger('video.create', [self.components.itemId, self.components.primaryType]);
    
                // Save reference to the player
                // register for notifications from clipstrip to seek to various times in the video
                self.events.connect(self, 'seek', self.media.playAt);
                self.events.connect(self, 'playclip', function (obj) {
                    self.media.seek(obj.start, obj.end, true);
                });

                self.components.player.onReady(function(event) {
                    self.state.ready = true;
                    self.components.timedisplay.style.visibility = 'visible';
                });
                self.components.player.onPlay(function(event){
                    if (self.state.autoplay === false) {
                        self.media.pause();
                    }
                    delete self.state.autoplay;
                });  
                self.components.player.onPause(function(event) {
                    self.disconnect_pause();
                });
                self.components.player.onTime(function(event) {
                    self.components.elapsed.innerHTML =
                        self.secondsToCode(event.position);
                    self.components.duration.innerHTML =
                        self.secondsToCode(event.duration);
                });
            }
        };
        
        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            return self.components.player ? 
               self.components.player.getDuration() : 0;
        };
        
        this.media.pause = function () {
            if (self.components.player) {
                self.components.player.pause();
            }
        };

        this.media.play = function () {
            if (self.components.player) {
                self.components.player.play(0);
            }
        };

        this.media.isPlaying = function () {
            return self.components.player && self.components.player.getState() === 'PLAYING';
        };
        
        this.media.ready = function () {
            return self.state.ready;
        };
        
        this.media.seek = function (starttime, endtime, autoplay) {
            self.disconnect_pause();

            if (starttime !== undefined) {
                self.state.autoplay = autoplay;
                self.components.player.seek(starttime);
            } else if (autoplay) {
                self.media.play();
            }
            
            if (endtime) {
                setTimeout(function() {
                    self.media.pauseAt(endtime);
                }, 1000);
            }
        };
        
        this.media.time = function () {
            return self.components.player ? 
                self.components.player.getPosition() : 0;
        };
        
        this.media.timestrip = function () {
            // The clipstrip is calibrated to the jwplayer scrubber
            // Visually, it looks a little "short", but trust, it tags along
            // with the circle shaped thumb properly.
            var w = self.components.width;
            return {w: w,
                    trackX: 83,
                    trackWidth: w - 195,
                    visible: true};
        };
    };
}
