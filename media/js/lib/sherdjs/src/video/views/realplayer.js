/*
Documentation:
  http://service.real.com/help/library/guides/ScriptingGuide/HTML/samples/javaembed/JAVAFrames.htm
  clip position:
      http://service.real.com/help/library/guides/ScriptingGuide/HTML/samples/javaembed/position.txt
  play/pause:
      http://service.real.com/help/library/guides/ScriptingGuide/HTML/samples/javaembed/playback1.txt
  embed/object attrs:
      http://service.real.com/help/library/guides/realone/ProductionGuide/HTML/htmfiles/embed.htm

  SERIALIZATION of asset
       {url:''
	,width:320
	,height:260
	,autoplay:'false'
	,controller:'true'
	,errortext:'Error text.'
	,type:'video/quicktime'
	};
 */
if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.RealPlayer && Sherd.Video.Base) {
    Sherd.Video.RealPlayer = function () {
        var self = this;
        Sherd.Video.Base.apply(this, arguments); //inherit off video.js - base.js

        ////////////////////////////////////////////////////////////////////////
        // Microformat
        this.microformat.create = function (obj, doc) {
            var wrapperID = Sherd.Base.newID('realplayer-wrapper-');
            var playerID = Sherd.Base.newID('realplayer-player-');
            var controllerID = Sherd.Base.newID('realplayer-controller-');
            var console = 'Console' + playerID;

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
                currentTimeID: 'currtime' + playerID,
                durationID: 'totalcliplength' + playerID,
                text: '<div id="' + wrapperID + '" class="sherd-flowplayer-wrapper" ' +
                '     style="width:' + obj.options.width + 'px">' +
                '<object id="' + playerID + '" classid="clsid:CFCDAA03-8BE4-11cf-B84B-0020AFBBCCFA"' +
                '        height="' + obj.options.height + '" width="' + obj.options.width + '">' +
                '<param name="CONTROLS" value="ImageWindow">' +
                '<param name="AUTOSTART" value="' + obj.autoplay + '">' +
                '<param name="CONSOLE" value="' + console + '">' +
                '<param name="SRC" value="' + obj.realplayer + '">' +
                '<embed height="' + obj.options.height + '" width="' + obj.options.width + '"' +
                '       NOJAVA="true" console="' + console + '" ' +
                '  controls="ImageWindow" ' +
                '  src="' + obj.realplayer + '" ' +
                '  type="audio/x-pn-realaudio-plugin" ' +
                '  autostart="' + obj.autoplay + '" > ' +
                '</embed>' +
                '</object>' +
                '<object id="' + controllerID + '" classid="clsid:CFCDAA03-8BE4-11cf-B84B-0020AFBBCCFA"' +
                '        height="36" width="' + obj.options.width + '">' +
                '<param name="CONTROLS" value="ControlPanel">' +
                '<param name="CONSOLE" value="' + console + '">' +
                '<embed src="' + obj.realplayer + '" type="audio/x-pn-realaudio-plugin" controls="ControlPanel" ' +
                '    console="' + console + '" ' +
                '    width="' + obj.options.width + '" ' +
                '    height="36">' +
                '</embed>' +
                '</object>' +
                '<div class="time-display"><span id="currtime' + playerID + '">00:00:00</span>/<span id="totalcliplength' + playerID + '">00:00:00</span></div>' +
                '</div>'
            };
            return create_obj;
        };

        this.microformat.components = function (html_dom, create_obj) {
            try {
                var rv = {};
                if (html_dom) {
                    rv.wrapper = html_dom;
                }
                if (create_obj) {
                    var objs = html_dom.getElementsByTagName('object');
                    var embs = html_dom.getElementsByTagName('embed');
                    if (embs.length) {//netscape
                        rv.player = rv.playerNetscape = embs[0];
                        rv.controllerNetscape = embs[1];
                    } else {
                        rv.player = rv.playerIE = objs[0];
                        rv.controllerIE = objs[1];
                    }

                    rv.width = (create_obj.options && create_obj.options.width) || rv.player.offsetWidth;
                    rv.mediaUrl = create_obj.realplayer;

                    rv.duration = document.getElementById(create_obj.durationID);
                    rv.elapsed = document.getElementById(create_obj.currentTimeID);
                }
                return rv;
            } catch (e) {}
            return false;
        };

        // Find the objects based on the individual player properties in the DOM
        // Works in conjunction with read
        this.microformat.find = function (html_dom) {
            throw new Error("unimplemented");
        };

        // Return asset object description (parameters) in a serialized JSON format.
        // Will be used for things like printing, or spitting out a description.
        // works in conjunction with find
        this.microformat.read = function (found_obj) {
            throw new Error("unimplemented");
        };

        this.microformat.type = function () { return 'realplayer'; };

        // Replace the video identifier within the rendered .html
        this.microformat.update = function (obj, html_dom) {
            /*
            if (obj.realplayer && self.components.player && self.media.ready()) {
                try {
                    if (obj.realplayer != self.components.mediaUrl) {
                        return false;
                    }
                    return true;
                } catch (e) { }
            }*/
            return false;
        };


        ////////////////////////////////////////////////////////////////////////
        // AssetView Overrides

        this.initialize = function (create_obj) {
            self.events.connect(self, 'seek', self.media.playAt);
            self.events.connect(self, 'playclip', function (obj) {
                self.setState(obj, { autoplay: true });
                self.media.play();
            });
            self.events.queue('realplayer tick-tock', [{
                poll: 1000,
                test: function () {
                    self.components.duration.innerHTML = self.secondsToCode(self.media.duration());
                    self.components.elapsed.innerHTML = self.secondsToCode(self.media.time());
                }
            }]);
            ///TODO: figure out some hacky way to auto-buffer content
            ///      so load-time on each seek isn't so bad.  Realplayer sux.
        };

        // Overriding video.js
        this.deinitialize = function () {
        };

        ////////////////////////////////////////////////////////////////////////
        // Media & Player Specific

        this.media.duration = function () {
            var duration = 0;
            try {
                if (self.components.player &&
                    typeof self.components.player.GetLength !== 'undefined') {
                    ///Real API returns milliseconds
                    duration = self.components.player.GetLength() / 1000;
                    self.events.signal(self, 'duration', { duration: duration });
                }
            } catch (e) {}
            return duration;
        };

        this.media.pause = function () {
            if (self.components.player) {
                self.components.player.DoPause();
            }
        };

        this.media.play = function () {
            if (self.media.ready()) {
                self.components.player.DoPlay();
            } else {
                self.events.queue('real play', [{ test: self.media.ready, poll: 100},
                                                { call: self.media.play }]);
            }
        };

        // Used by tests
        this.media.isPlaying = function () {
            var playing = false;
            try {
                ///API:0=stopped,1=contacting,2=buffering,3=playing,4=paused,5=seeking
                ///Seek can occur when >= 2
                playing = (self.components.player &&
                           self.components.player.GetPlayState &&
                           self.components.player.GetPlayState() === 3);
            } catch (e) {}
            return playing;
        };

        this.media.ready = function () {
            var status;
            try {
                var p = self.components.player;
                return (p && typeof p.GetPlayState !== 'undefined');
            } catch (e) {
                return false;
            }
        };
        this.media.seekable = function () {
            try {
                var s = self.components.player.GetPlayState();
                return (self.media.ready() && s > 1 && s < 5);
            } catch (e) {
                return false;
            }
        };

        var seek_last = 0;
        this.media.seek = function (starttime, endtime, play) {
            var my_seek = ++seek_last;
            var p = self.components.player;
            if (self.media.seekable()) {
                if (starttime !== undefined) {
                    ///API in milliseconds
                    p.SetPosition(starttime * 1000);
                    if (play) {
                        self.media.play();
                    }
                }
                if (endtime) {
                    // Watch the video's running time & stop it when the endtime rolls around
                    self.media.pauseAt(endtime);
                }
            } else {
                self.events.queue('realplayer ready to seek', [ {
                    poll : 500,
                    test : self.media.seekable
                }, {
                    test : function () {
                        return (seek_last === my_seek);
                    }
                }, {
                    call : function () {
                        self.media.seek(starttime, endtime, play);
                    }
                } ]);
            }

            // store the values away for when the player is ready
            self.components.starttime = starttime;
            self.components.endtime = endtime;
        };

        this.media.time = function () {
            var time = 0;
            try {
                time = self.components.player.GetPosition() / 1000;
            } catch (e) {}
            return time;
        };

        this.media.timescale = function () {
            return 1;
        };

        this.media.timestrip = function () {
            var w = self.components.player.width;
            return {
                w: w,
                trackX: 110,
                trackWidth: w - 220,
                visible: true
            };
        };

        //returns true, if we're sure it is. Not currently used
        this.media.isStreaming = function () {
            return true;
        };

        // Used by tests.
        this.media.url = function () {
            throw new Error("unimplemented function media.url");
        };

    }; //Sherd.Video.RealPlayer

}