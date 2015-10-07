/*
  Support for the Kaltura js-enabled player.  documentation at:
  http://Kaltura.com/api/docs/oembed
 */

if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.Kaltura && Sherd.Video.Base) {
    Sherd.Video.Kaltura = function () {
        var self = this;
        
        Sherd.Video.Base.apply(this, arguments); //inherit -- video.js -- base.js
        
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
        
        this.state = {
            starttime: 0,
            endtime: 0,
            seeking: false,
            autoplay: false
        };
        
        ////////////////////////////////////////////////////////////////////////
        // Microformat
        
        // create === asset->{html+information to make it}
        this.microformat.create = function (obj) {
            var wrapperID = Sherd.Base.newID('kaltura-wrapper-');
            ///playerID MUST only have [\w] chars or IE7 will fail
            var playerID = Sherd.Base.newID('kaltura_player_');
            var autoplay = obj.autoplay ? "true" : "false";
            self.media._ready = false;
            self.media.current_state = "stopped";
            
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
            
            // massage the url options if needed, take off everything after the ? mark
            var url = obj.kaltura;
            
            // For IE, the id needs to be placed in the object.
            // For FF, the id needs to be placed in the embed.
            var objectID = 'id="' + playerID + '"';
            var classID = '';
            if (window.navigator.userAgent.indexOf("MSIE") > -1) {
                classID = 'classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000"';
            }
            
            return {
                object: obj,
                width: obj.options.width,
                height: obj.options.height,
                htmlID: wrapperID,
                playerID: playerID, // Used by microformat.components initialization
                autoplay: autoplay, // Used later by _seek seeking behavior
                mediaUrl: url, // Used by _seek seeking behavior
                text: '<div id="' + wrapperID + '" class="sherd-kaltura-wrapper">' +
                      '  <object width="' + obj.options.width + '" height="' + obj.options.height + '" ' + objectID +
                          ' type="application/x-shockwave-flash" data="' + url + '" ' + classID + '>' +
                        '  <param name="movie" value="' + url + '"></param>' +
                        '  <param name="allowscriptaccess" value="always"/></param>' +
                        '  <param name="width" value="' + obj.options.width + '"></param>' +
                        '  <param name="height" value="' + obj.options.height + '"></param>' +
                        '  <param name="allowfullscreen" value="true"></param>' +
                        '  <param name="flashVars" value="autoPlay=' + autoplay + '&streamerType=hdnetwork&akamaiHD.loadingPolicy=preInitialize&akamaiHD.asyncInit=true&kml=local&kmlPath=http://mediathread.ccnmtl.columbia.edu/media/js/sherdjs/lib/kaltura/config.xml"/>' +
                        '</object>' +
                      '</div>'
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
                    //the first works for everyone except safari
                    //the latter probably works everywhere except IE
                    rv.player = document[create_obj.playerID] || document.getElementById(create_obj.playerID);
                    rv.autoplay = create_obj.autoplay;
                    rv.mediaUrl = create_obj.mediaUrl;
                    rv.playerID = create_obj.playerID;
                    rv.width = create_obj.width;
                    rv.height = create_obj.height;
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
        
        // Note: not currently in use
        this.microformat.type = function () { return 'Kaltura'; };
        
        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            return obj.kaltura === self.components.mediaUrl &&
                   document.getElementById(self.components.playerID) &&
                   self.media.ready();
        };
        
        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides
        
        this.initialize = function (create_obj) {
            // register for notifications from clipstrip to seek to various times in the video
            self.events.connect(self, 'seek', self.media.playAt);
            
            self.events.connect(self, 'playclip', function (obj) {
                self.setState(obj, { 'autoplay': true });
            });
        };
        
        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific
        
        window.jsCallbackReady = function () {
            self.components.player.addJsListener("playerStateChange", "playerStateChangeHandler");
            self.components.player.addJsListener("durationChange", "durationChangeHandler");
            self.components.player.addJsListener("entryReady", "entryReadyHandler");
            self.components.player.addJsListener("playerUpdatePlayhead", "timeChangeHandler");
            self.components.player.addJsListener("playerPlayEnd", "playerFinished");
        };
        
        window.entryReadyHandler = function (data, id) {
            self.media._ready = true;
            self.media.video_duration = data.duration;
            self.media.binary_state = "paused";
            self.events.signal(self, 'duration', { duration: data.duration });
            jQuery(window).trigger('video.create', [self.components.itemId, self.components.primaryType]);
        };
        
        window.durationChangeHandler = function (data, id) {
            self.media.video_duration = data.duration;
            self.events.signal(self, 'duration', { duration: data.duration });
        };
        
        window.timeChangeHandler = function (data, id) {
            self.media.current_time = data;
            
            if (self.state.starttime !== undefined && self.media.isPlaying() && self.media.current_time !== undefined) {
                self.media.seek(self.state.starttime, self.state.endtime, self.state.autoplay);
            }
        };
        
        window.playerStateChangeHandler = function (data, id) {            
            if (self.media.binary_state === "paused" && data === "playing") {
                jQuery(window).trigger('video.play', [self.components.itemId, self.components.primaryType]);
                self.media.binary_state = "playing";
            } else if (self.media.binary_state === "playing" && data === "paused") {
                jQuery(window).trigger('video.pause', [self.components.itemId, self.components.primaryType]);
                self.media.binary_state = "paused";
            }
            self.media.current_state = data;
        };
        
        window.playerFinished = function () {
            jQuery(window).trigger('video.finish', [self.components.itemId, self.components.primaryType]);
        };

        this.media.duration = function () {
            if (self.media.video_duration !== undefined) {
                return self.media.video_duration;
            } else if (self.components.player && self.media.ready()) {
                self.media.video_duration = self.components.player.evaluate('{mediaProxy.entry.duration}');
                return self.media.video_duration;
            } else {
                return 0;
            }
        };
        
        this.media.pause = function () {
            if (self.components.player) {
                try {
                    self.components.player.sendNotification('doPause');
                } catch (e) {}
            }
        };
        
        this.media.play = function () {
            if (self.components.player) {
                try {
                    self.components.player.sendNotification('doPlay');
                } catch (e) {}
            }
        };
        
        this.media.ready = function () {
            return self.media._ready;
        };
        
        this.media.isPlaying = function () {
            return self.components.player && self.media.current_state && self.media.current_state === "playing";
        };

        this.media.seek = function (starttime, endtime, autoplay) {
            // Kaltura player needs to be fully buffered before seeking
            // the buffering can only be accomplished by actually playing the video.
            if (!self.media.ready()) {
                self.state.starttime = starttime;
                self.state.endtime = endtime;
                self.state.autoplay = autoplay;
            } else if (autoplay && !self.media.isPlaying()) {
                self.state.starttime = starttime;
                self.state.endtime = endtime;
                self.state.autoplay = autoplay;
                
                self.media.play();
            } else {
                if (starttime !== undefined) {
                    self.components.player.sendNotification('doSeek', starttime);
                }
                
                if (endtime !== undefined) {
                    self.media.current_time = self.state.starttime;
                    
                    // wait until the video seek/play catches up before queuing the end timer
                    self.media.pauseAt(endtime);
                }
                
                // clear any saved values if they exist
                delete self.state.starttime;
                delete self.state.endtime;
                delete self.state.autoplay;
            }
        };
        
        this.media.time = function () {
            var time = 0;
            if (self.components.player && self.media.current_time) {
                return self.media.current_time;
            }
            return time;
        };
        
        this.media.timestrip = function () {
            var w = self.components.width;
            return {
                w: w,
                trackX: 53,
                trackWidth: w - 150,
                visible: true
            };
        };
    };
}