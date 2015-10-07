/*
 http://developer.apple.com/mac/library/documentation/QuickTime/Conceptual/QTScripting_JavaScript/aQTScripting_Javascro_AIntro/Introduction%20to%20JavaScript%20QT.html
http://developer.apple.com/safari/library/documentation/QuickTime/Conceptual/QTScripting_JavaScript/bQTScripting_JavaScri_Document/QuickTimeandJavaScri.html

  SERIALIZATION of asset
       {url:''
	,width:320
	,height:260
	,autoplay:'false'
	,controller:'true'
	,errortext:'Error text.'
	,type:'video/quicktime'
	};

	@todo - Stop using the quicktime poster movie type and just create a clickable jpg that shows the real quicktime movie.
	This should allow a transparent arrow to be overlayed onto the poster so cheesy control text "Click to Play" can be removed.
	Some tips here: http://digitalmedia.oreilly.com/2006/09/29/two-slick-quicktime-tricks.html?page=2
 */
if (!Sherd) {Sherd = {}; }
if (!Sherd.Video) {Sherd.Video = {}; }
if (!Sherd.Video.QuickTime) {
    Sherd.Video.QuickTime = function () {
        var self = this;
        self._played = false; // See this.media.seek
        Sherd.Video.Base.apply(this, arguments); //inherit off video.js - base.js

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
                width: function () { return 540; },
                height: function () { return 383; }
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Microformat

        this.microformat.create = function (obj, doc) {

            var wrapperID = Sherd.Base.newID('quicktime-wrapper-');
            var playerID = Sherd.Base.newID('quicktime-player-');
            self._played = false;

            var opt = {
                url: '',
                width: 320,
                height: 240,
                controller_height: 20,
                autoplay: 'false',
                controller: 'true',
                errortext: 'Error text.',
                mimetype: 'video/quicktime',
                poster: false,
                loadingposter: false,
                extra: ''
            };
            for (var a in opt) {
                if (opt.hasOwnProperty(a)) {
                    if (obj[a]) {
                        opt[a] = obj[a];
                    }
                }
            }

            if (!obj.presentation_width) {
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

                obj.presentation_width = presentation.width();
                obj.presentation_height = presentation.height();
            }

            var full_height = obj.presentation_height + Number(opt.controller_height);
            opt.href = '';//for poster support
            opt.autohref = '';//for poster support
            if (!(/Macintosh.*Version\/[3-9][.0-9]+ Safari/.test(navigator.userAgent) ||
                /Linux/.test(navigator.userAgent)
            )) {
                opt.mimetype = 'image/x-quicktime';
                opt.extra += '<param name="href" value="' + opt.url + '" />' +
                    '<param name="autohref" value="' + opt.autoplay + '" />' +
                    '<param name="target" value="myself" />';

                opt.controller = 'false';
                if (opt.loadingposter && opt.autoplay === 'true') {
                    opt.url = opt.loadingposter;
                } else if (opt.poster) {
                    opt.url = opt.poster;
                }
            }

            var clicktoplay = "";
            if (opt.autoplay !== 'true') {
                clicktoplay += '<div id="clicktoplay">Click video to play</div>';
            }

            //we need to retest where the href usecase is needed
            //since safari breaks
            return {
                htmlID: wrapperID,
                playerID: playerID,
                timedisplayID: 'timedisplay' + playerID,
                currentTimeID: 'currtime' + playerID,
                durationID: 'totalcliplength' + playerID,
                object: obj,
                text: clicktoplay + '<div id="' + wrapperID + '" class="sherd-quicktime-wrapper">' +
                 '<div id="timedisplay' + playerID + '" style="visibility:hidden">' +
                   '<span id="currtime' + playerID + '">00:00:00</span>' +
                   '/<span id="totalcliplength' + playerID + '">00:00:00</span></div>' +
                '<!--[if IE]>' +
                '<object id="' + playerID + '" ' +
                'width="' + obj.presentation_width + '" height="' + full_height + '" ' +
                'style="behavior:url(#qt_event_source)"  ' +
                'codebase="http://www.apple.com/qtactivex/qtplugin.cab"  ' +
                'classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B">' +
                '<![endif]-->' +
                '<!--[if !IE]><-->' +
                '    <object id="' + playerID + '" type="' + opt.mimetype + '" ' +
                '    data="' + opt.url + '" ' +
                '    width="' + obj.presentation_width + '" height="' + full_height + '">' +
                '<!-- ><![endif]--> ' +
                '<param name="src" value="' + opt.url + '" />' +
                '<param name="controller" value="' + opt.controller + '" />' +
                '<param name="type" value="' + opt.mimetype + '" />' +
                '<param name="enablejavascript" value="true" />' +
                '<param name="autoplay" value="' + opt.autoplay + '" />' +
                '<param name="width" value="' + obj.presentation_width + '">' +
                '<param name="height" value="' + full_height + '">' +
                '<param name="postdomevents" value="true" />' +
                '<param name="scale" value="aspect" />' +
                opt.extra + '' +
                opt.errortext + '</object></div>'

            };
        };

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
                    rv.duration = document.getElementById(create_obj.durationID);
                    rv.elapsed = document.getElementById(create_obj.currentTimeID);
                    rv.timedisplay = document.getElementById(create_obj.timedisplayID);
                    rv.autoplay = create_obj.object.autoplay === 'true';
                    rv.playerID = create_obj.playerID;
                    rv.htmlID = create_obj.htmlID;
                    rv.mediaUrl = create_obj.object.quicktime;
                    rv.itemId = create_obj.object.id;
                    rv.primaryType = create_obj.object.primary_type;                                        
                }
                return rv;
            } catch (e) {}
            return false;
        };

        // Find the objects based on the individual player properties in the DOM
        // NOTE: Not currently in use.
        // Works in conjunction with read
        this.microformat.find = function (html_dom) {
            // Find the objects based on the QT properties in the DOM
            var found = [];
            //SNOBBY:not embeds, since they're in objects--and not xhtml 'n' stuff
            var objects = ((html_dom.tagName.toLowerCase() === 'object') ?
                [html_dom]
                : html_dom.getElementsByTagName('object')
            //function is case-insensitive in IE and FFox,at least
            );
            for (var i = 0; i < objects.length; i++) {
                if (objects[i].getAttribute('classid') === 'clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B' ||
                    objects[i].getAttribute('type') === 'video/quicktime') {
                    found.push({'html': objects[i]});
                }
            }
            return found;
        };

        // Return asset object description (parameters) in a serialized JSON format.
        // NOTE: Not currently in use.
        // Will be used for things like printing, or spitting out a description.
        // works in conjunction with find
        this.microformat.read = function (found_obj) {
            var obj = {
                url: '',//defaults
                quicktime: '',
                width: 320,
                height: 240,
                controller_height: 20,
                autoplay: 'false',
                controller: 'true',
                errortext: 'Error text.',
                type: 'video/quicktime'
            };
            var params = found_obj.html.getElementsByTagName('param');
            for (var i = 0; i < params.length; i++) {
                obj[params[i].getAttribute('name')] = params[i].getAttribute('value');
            }
            if (obj.src) {
                obj.url = obj.src;
                delete obj.src;
            } else {
                obj.url = found_obj.html.getAttribute('data');
            }
            obj.quicktime = obj.url;
            if (Number(found_obj.html.width)) {
                obj.width = Number(found_obj.html.width);
            }
            if (Number(found_obj.html.height)) {
                obj.height = Number(found_obj.html.height);
            }
            return obj;
        };

        this.microformat.type = function () { return 'quicktime'; };

        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            if (obj.quicktime && self.components.player && self.media.ready()) {
                try {
                    if (obj.quicktime !== self.components.mediaUrl) {
                        self.components.player.SetURL(obj.quicktime);
                        self.components.mediaUrl = obj.quicktime;
                        if (/MSIE/.test(navigator.userAgent) && self.components.autoplay) {
                            window.setTimeout(function () {
                                self.components.player.SetURL(self.components.mediaUrl); //reset the url

                                self.media.seek(self.components.starttime, self.components.endtime); // redo the seek also.
                            }, 400);
                        }
                    }
                    self.microformat._startUpdateDisplayTimer();
                    return true;
                } catch (e) { }
            }
            return false;
        };

        this.microformat._startUpdateDisplayTimer = function (create_obj) {
            self.media._duration = 0;
            self.events.queue('quicktime duration watcher & tick count',
                    [{test: function () {
                        // Update the duration
                        var newDuration = self.media.duration();
                        if (newDuration !== self.media._duration) {
                            self.media._duration = newDuration;
                            self.components.duration.innerHTML = self.secondsToCode(newDuration);
                            self.events.signal(self, 'duration', { duration: newDuration });
                        }
                        if (self.media.ready()) {
                            self.components.timedisplay.style.visibility = 'visible';
                            // set dimensions correctly
                            self.media.resize(create_obj.object.presentation_width,
                                create_obj.object.presentation_height, create_obj);
                        }

                        // Update the tick count
                        self.media._updateTickCount();

                        return false;
                    },
                    poll: 500}
                    ]);
        };

        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides
        
        this.addListener = function (evt, handler) { 
            if (document.addEventListener) {
                self.components.player.addEventListener(evt, handler);
            } else {
                // IE
                self.components.player.attachEvent('on' + evt, handler);
            }
        };
        
        window.onQuicktimePlay = function () {
            if (self.media.binary_state === 'paused') {
                jQuery(window).trigger('video.play', [self.components.itemId, self.components.primaryType]);
                self.media.binary_state = 'playing';
            }
        };
        
        window.onQuicktimePause = function () {
            if (self.media.binary_state === 'playing') {
                jQuery(window).trigger('video.pause', [self.components.itemId, self.components.primaryType]);
                self.media.binary_state = 'paused';
            }
        };
        
        window.onQuicktimeFinish = function () {
            jQuery(window).trigger('video.finish', [self.components.itemId, self.components.primaryType]);
            self.media.binary_state = 'paused';
        };

        this.initialize = function (create_obj) {
            self.media._duration = self.media.duration();
            self.media.binary_state = 'paused';

            // kickoff some timers
            self.events.queue('quicktime ready to seek',
                    [{ test: function () {
                            return (self.media.ready() &&
                                    self.media.duration() > 0 && // Is the duration valid yet?
                                    (self.components.player.GetMaxTimeLoaded() / self.media.timescale()) > self.components.starttime);
                        },
                        poll: 500
                     },
                     { call: function () {
                            // We wait here for the situation of suckage:
                            // Mac Chrome: auto-seeking from poster-frame needs some time to 'really' load the video
                            setTimeout(function () {
                                self.setState({
                                    "start": self.components.starttime,
                                    "end": self.components.endtime
                                });
                            }, 400);
                        }
                     }]);

            self.microformat._startUpdateDisplayTimer(create_obj);

            // register for notifications from clipstrip to seek to various times in the video
            self.events.connect(self, 'seek', self.media.playAt);

            self.events.connect(self, 'playclip', function (obj) {
                self.setState(obj);

                // give it a second
                ///TODO: should just use self.setState(obj, {autoplay:true});
                window.setTimeout(function () { self.media.play(); }, 200);
            });
            
            jQuery(window).trigger('video.create', [self.components.itemId, self.components.primaryType]);
            
            self.addListener('qt_play', onQuicktimePlay);
            self.addListener('qt_pause', onQuicktimePause);
            self.addListener('qt_ended', onQuicktimeFinish);
        };

        // Overriding video.js
        this.deinitialize = function () {
            self.events.clearTimers();

            if (self.media.isPlaying()) {
                self.media.pause();
            }
            if (self.components.timedisplay) {
                self.components.timedisplay.style.display = 'none';
            }
        };

        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            var duration = 0;
            try {
                if (self.components.player &&
                    typeof self.components.player.GetDuration !== 'undefined') {
                    var frame_duration = self.components.player.GetDuration();
                    if (frame_duration < 2147483647) {
                        duration = frame_duration / self.media.timescale();
                    }
                }
            } catch (e) {}
            return duration;
        };

        this.media.pause = function () {
            if (self.components.player) {
                self.components.player.Stop();
            }
        };

        this.media.play = function () {
            if (self.media.ready()) {
                if (!self.media.swapPoster()) {
                    self.components.player.Play();
                }
            } else {
                self.events.queue('qt play', [{ test: self.media.ready, poll: 100},
                                              { call: self.media.play}]);
            }
        };

        this.media.swapPoster = function () {
            var p = self.components.player;
            ///WARNING: mimetype doesn't change after HREF advancement
            ///         so we need to test if we're already advanced
            var mimetype = '';
            try { //Safari SUX: dies on GetMIMEType for no reason.
                mimetype = p.GetMIMEType();
            } catch (e) {/*pass*/}
            var href = p.GetHREF();
            if (href && !self._played && /image/.test(mimetype)) {
                // Setting the URL in this manner is only needed the first time through
                // In order to facilitate fast seeking and update, keep track of the first time
                // via the _played class variable, then default to a regular play event
                p.SetURL(href);
                p.SetHREF('');
                self._played = true;
                return true;
            } else {
                return false;
            }
        };

        // Used by tests
        this.media.isPlaying = function () {
            var playing = false;
            try {
                playing = (self.components.player &&
                           self.components.player.GetRate &&
                           self.components.player.GetRate() > 0);
            } catch (e) {}
            return playing;
        };

        this.media.ready = function () {
            var status;
            try {
                var p = self.components.player;
                ///IE SUX: will return 'unknown' for (typeof p.GetPluginStatus)
                ///        and dies silently on (p.GetPluginStatus)
                if (p && typeof p.GetPluginStatus !== 'undefined') {
                    status = p.GetPluginStatus();
                }
            } catch (e) {} // player is not yet ready

            return (status === 'Playable' || status === 'Complete');
        };

        this.media.seek = function (starttime, endtime, autoplay) {
            if (self.media.ready()) {
                var p = self.components.player;
                if (starttime !== undefined) {
                    var playRate = p.GetRate();
                    if (playRate > 0) {
                        p.Stop(); // HACK: QT doesn't rebuffer if we don't stop-start
                    }
                    try {
                        p.SetTime(starttime * self.media.timescale());
                    } catch (e) {}
                    if (autoplay || self.components.autoplay || playRate !== 0) {
                        p.Play();
                    }
                }
                if (endtime) {
                    // Watch the video's running time & stop it when the endtime rolls around
                    self.media.pauseAt(endtime);
                }
            }

            // store the values away for when the player is ready
            self.components.starttime = starttime;
            self.components.endtime = endtime;
        };

        this.media.time = function () {
            var time = 0;
            try {
                time = self.components.player.GetTime() / self.media.timescale();
            } catch (e) {}
            return time;
        };

        this.media.timescale = function () {
            var timescale = 1;
            try {
                timescale = self.components.player.GetTimeScale();
            } catch (e) {}
            return timescale;
        };

        this.media.timestrip = function () {
            var w = self.components.player.width;
            return {
                w: w,
                trackX: 152,
                trackWidth: w - 310,
                visible: true
            };
        };

        //returns true, if we're sure it is. Not currently used
        this.media.isStreaming = function () {
            //2147483647 (=0x7FFFFFFF) 0x7FFFFFFF is quicktime's magic number for streaming.
            var url = self.components.player.GetURL();
            return (url && /^rtsp/.test(url));
        };

        // Used by tests.
        this.media.url = function () {
            return self.components.player.GetURL();
        };

        this.media._updateTickCount = function () {
            if (typeof self.components.player.GetRate !== 'undefined' &&
                self.components.player.GetRate() > 0) {
                self.components.elapsed.innerHTML = self.secondsToCode(self.media.time());
            }
        };
        
        this.media.resize = function (w, h, obj) {
            if (!self.debug) {
                return;
            }

            /* Below is code that helps QT versions below 7.6.6
             * (uncertain of the exact version below)
             * However, it BREAKS QT 7.6.6 (and presumably above)
             * TODO: We could do version testing or just say
             *       we only support QT 7.6.6+
             */
            var p =  self.components.player;
            if (typeof p.SetRectangle !== 'undefined') {
                p.SetRectangle("0,0," + w + "," + h);
            }
        };
    }; //Sherd.AssetViews.QuickTime
}

