/**
 * baseline video helper functions:
 *
 *
 * TODO: make sure overlapping seeks don't trip over each other
 *
 */
if (typeof Sherd === 'undefined') {
    Sherd = {};
}
if (!Sherd.Video) {
    Sherd.Video = {};
}
if (!Sherd.Video.Helpers) {
    Sherd.Video.secondsToCode = function (seconds) {
        // second argument is the timecode object to be modified, otherwise
        // it'll create one
        var tc = {};
        var intTime = Math.floor(seconds);
        tc.hr = parseInt(intTime / 3600, 10);
        tc.min = parseInt((intTime % 3600) / 60, 10);
        tc.sec = intTime % 60;
        tc.fraction = seconds - intTime;

        if (tc.hr < 10) {
            tc.hr = "0" + tc.hr;
        }
        if (tc.min < 10) {
            tc.min = "0" + tc.min;
        }
        if (tc.sec < 10) {
            tc.sec = "0" + tc.sec;
        }

        return tc.hr + ":" + tc.min + ":" + tc.sec;
    };

    Sherd.Video.codeToSeconds = function (code) {
        if (!code) {
            return 0;
        }
        var mvscale = 1;
        // takes a timecode like '0:01:36:00.0' and turns it into # seconds
        var t = code.split(':');
        var x = t.pop();
        var seconds = 0;
        if (x.indexOf('.') >= 0) { // 00.0 format is for frames
            // ignore frames
            x = parseInt(t.pop(), 10);
        }
        var timeUnits = 1; // seconds -> minutes -> hours
        while (x || t.length > 0) {
            seconds += x * timeUnits * mvscale;
            timeUnits *= 60;
            x = parseInt(t.pop(), 10);
        }
        return seconds;
    };
    Sherd.Video.Helpers = function () {
        // helper functions
        this.secondsToCode = Sherd.Video.secondsToCode;
        this.codeToSeconds = Sherd.Video.codeToSeconds;
    };
}

if (!Sherd.Video.Base) {
    var noop = function () {
    };
    var unimplemented = function () {
        throw new Error('unimplemented');
    };

    Sherd.Video.Base = function (options) {
        var self = this;
        Sherd.Video.Helpers.apply(this, arguments);
        Sherd.Base.AssetView.apply(this, arguments);

        this.queryformat = {
            find: function (str) {
                //legacy
                var start_point = String(str).match(/start=([.\d]+)/);
                if (start_point !== null) {
                    var start = Number(start_point[1]);
                    if (!isNaN(start)) {
                        return [ {
                            start : start
                        } ];
                    }
                }
                //MediaFragment
                var videofragment = String(str).match(/t=([.\d]+)?,?([.\d]+)?/);
                if (videofragment !== null) {
                    var ann = {
                        start: Number(videofragment[1]) || 0,
                        end: Number(videofragment[2]) || undefined
                    };
                    return [ann];
                }
                return [];
            }
        };

        this.microformat = {
            create : function (obj) { // Return the .html embed block for the embedded player
                return '';
            },
            components: unimplemented, // Save the player and other necessary state for the control to be updated
            find : function (html_dom) { // Find embedded players. Note: Not currently in use.
                return [ {
                    html : html_dom
                } ];
            },
            read : function (found_obj) { // Return serialized description of embedded player. Note: Not currently in use.
                var obj;
                return obj;
            },
            supports: function () { return []; },  // Idea: Return list of types supported. Note: Not currently in use or implemented by anyone
            type: function () { var type; return type; }, // Return current type of media playing. Note: Not currently in use;
            update: function (obj, html_dom) {} // Replace the video identifier within the .html embed block
        };

        // AssetView overrides to initialize and deinitialize timers/ui/etc.
        this.initialize = function () {};

        this.deinitialize = function () {
            if (self.media.isPlaying()) {
                self.media.pause();
            }
            self.events.clearTimers();
        };

        // Player specific controls
        this.media = {
            duration : unimplemented, // get duration in seconds
            pause : unimplemented,
            pauseAt : function (endtime) {
                if (endtime) {
                    // kill any outstanding timers for this event
                    var name = self.microformat.type() + ' pause';
                    self.events.killTimer(name);
                    self.events.queue(name, [{
                            test: function () {
                                return self.media.time() >= endtime;
                            },
                            poll: 500
                        },
                        { call: function () { self.media.pause(); }}
                     ]);
                }
            },
            play : unimplemented,
            playAt : function (starttime) {
                self.media.seek(starttime, false, /*autoplay*/true);
            },
            isPlaying : function () {
                return false; // Used by ClipForm to determine whether the media is playing.
                // Maybe should be one level up so that ClipForm doesn't know about media
            },
            seek: unimplemented, // (starttime, endtime)
            ready: unimplemented, // whether the player is ready to go. mostly used internally.
            time : unimplemented, // get current time in seconds
            timescale : function () { return 1; }, // get the movie's timescale. only QT is not 1 (so far)
            timeCode: function () { // get current time as a time code string
                return self.secondsToCode(self.media.time());
            },
            timeStrip : unimplemented
        };

        this.play = function () {
            this.media.play();
        };

        // tell me where you are
        this.getState = function () {
            var state = {};
            state.start = self.media.time();
            state['default'] = (!state.start);
            state.duration = self.media.duration();
            state.timeScale = self.media.timescale();
            return state;
        };

        // did you give me a start point - cue?
        // did you give me an end point -- pause at that end point or jump to
        // the end point if you're past that point
        // if not loaded -- then do this as soon as you load (if ready)
        this.setState = function (obj, options) {
            if (typeof obj === 'object') {
                if (obj === null) {
                    //endtime is different so it doesn't start playing
                    this.media.seek(0, 0.1);
                } else {
                    this.media.seek(obj.start, obj.end, (options && options.autoplay || false));
                }
            }
        };

        if (!this.events) {
            this.events = {};
        }

        this.events._timers = {};
        this.events.registerTimer = function (name, timeoutID) {
            this._timers[name] = timeoutID;
        };

        this.events.killTimer = function (name) {
            if (this._timers[name]) {
                window.clearTimeout(this._timers[name]);
                delete this._timers[name];
                return true;
            } else {
                return false;
            }
        };

        this.events.clearTimers = function () {
            for (var name in this._timers) {
                if (this._timers.hasOwnProperty(name)) {
                    window.clearTimeout(this._timers[name]);
                }
            }
            this._timers = {};
        };

        /*
         * queue() takes a plan of tasks and will perform one after another with
         * the opportunity to keep trying a step until it's ready to proceed
         * @plan array of objects of the form: {data:'Queue dispatch'//passed to
         * all calls, but useful as a name, too ,call:function (){}//called
         * initially in sequence-- ,check:media.GetDuration ,test:function (){}
         * ,poll:100//msecs will keep trying until test(check()) returns true
         * ,callback:function (){}//if test(check()) returns true, this function
         * will be called //UNIMPLEMENTED--need some thought on where events get
         * registered, etc. ,event:'load' //will listen for this event to call
         * test(check()), parallel to polling ,broadcast:'seek' //event sent
         * when test(check())==true }; with all
         */
        this.events.queue = function queue(name, plan) {

            var current = -1;
            if (plan.length) {
                var next;
                var cur;
                var pollID;
                var timeoutID;

                //TODO: event, broadcast attrs
                var advance = function () {
                    if (pollID) {
                        window.clearTimeout(pollID);
                    }
                    if (timeoutID) {
                        window.clearTimeout(timeoutID);
                    }
                    ++current;
                    if (plan.length > current) {
                        cur = plan[current];
                        next();
                    }
                };
                next = function () {
                    var fired = false;
                    var curself = (cur.self) ? cur.self : this;
                    try {
                        if (cur.call) {
                            cur.call.apply(curself);
                        }
                    } catch (e) {
                        if (cur.log) {
                            cur.log.apply(curself, [ e, 'call failed' ]);
                        }
                    }
                    function go() {
                        if (fired) {
                            advance();
                            return;
                        }
                        var v = null;
                        var rv = true;
                        var data = (typeof cur.data !== 'undefined') ? cur.data : '';
                        try {
                            if (cur.check) {
                                v = cur.check.apply(curself, [ data ]);
                            }
                            if (cur.test) {
                                rv = cur.test.apply(curself, [ v, data ]);
                            }
                            if (cur.log) {
                                cur.log.apply(curself, [ [ v, rv, data ] ]);
                            }
                            if (rv) {
                                if (cur.callback) {
                                    cur.callback.apply(curself, [ rv, data ]);
                                }
                                fired = true;
                                advance();
                            } else if (cur.poll) {
                                pollID = window.setTimeout(arguments.callee, cur.poll);
                            }
                        } catch (e) {
                            if (cur.poll) {
                                pollID = window.setTimeout(arguments.callee, cur.poll);
                            }
                            if (cur.log) {
                                cur.log.apply(curself, [ e, data ]);
                            }
                        }

                        self.events.registerTimer(name, pollID);
                    } // endgo

                    if (cur.check || cur.poll || cur.test) {
                        pollID = window.setTimeout(go, 0);
                        self.events.registerTimer(name, pollID);
                    } else {
                        advance();
                    }
                    if (cur.timeout) {
                        timeoutID = window.setTimeout(function () {
                            fired = true;
                            advance();
                        }, cur.timeout);
                        self.events.registerTimer(name + 'timeout', timeoutID);
                    }
                };//next()
                advance();
            }
        };//event.queue()
    };//Sherd.Video.Base
}
