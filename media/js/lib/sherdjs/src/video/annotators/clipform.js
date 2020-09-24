/* global Sherd: true */
///clipform-display
///1. update noteform field: DjangoSherd_UpdateHack()
///2. initialize clipform field vals
///3. onchange of text fields in clipform to run: DjangoSherd_UpdateHack
///4. on tab-change, set startTime (and from that run DjangoSherd_UpdateHack)

//Listens for:
//Nothing

//Signals:
//clipstart - the clip start time has changed. signals self.targetview.media
//clipend -- the clip end time has changed. signals self.targetview.media

if (!Sherd) { Sherd = {}; }
if (!Sherd.Video) { Sherd.Video = {}; }
if (!Sherd.Video.Annotators) { Sherd.Video.Annotators = {}; }
if (!Sherd.Video.Annotators.ClipForm) {
    Sherd.Video.Annotators.ClipForm = function () {
        var secondsToCode = Sherd.Video.secondsToCode; // @todo -- consider moving these functions out of Video
        var codeToSeconds = Sherd.Video.codeToSeconds; // and into a separate Utilities or Helpers file?

        var self = this;
        Sherd.Base.AssetView.apply(this, arguments);// inherit

        this.attachView = function (view) {
            this.targetview = view;
        };

        this.targetstorage = [];
        this.addStorage = function (stor) {
            this.targetstorage.push(stor);
        };

        this.unbind = {};

        // @todo -- this getState is what is used for storing
        // all the data about the video. would be better if
        // it were a compilation of information from both clipform & player itself
        // eg. duration & timescale aren't clipform properties
        this.getState = function () {
            var duration = self.targetview.media.duration();
            var timeScale = self.targetview.media.timescale();
            var startFieldValue = self.components.startField ?
                self.components.startField.value : null;
            var endFieldValue = self.components.endField ?
                self.components.endField.value : null;

            var obj = {
                'startCode' : startFieldValue,
                'endCode' : endFieldValue,
                'duration' : duration,
                'timeScale' : timeScale,
                'start' : codeToSeconds(startFieldValue),
                'end' : codeToSeconds(endFieldValue)
            };

            return obj;
        };

        this.setState = function (obj, options) {
            if (typeof obj === 'object') {

                if (obj === null) {
                    obj = {};
                    obj.start = 0;
                    obj.end = 0;
                }

                // hook up an extra playbutton
                if (self.unbind.hasOwnProperty('tool_play')) {
                    self.unbind.tool_play.disconnect();
                }
                if (options && options.tool_play) {
                    self.unbind.tool_play = self.events.connect(options.tool_play, 'click', function (evt) {
                        var obj = self.getState();
                        self.events.signal(self.targetview, 'playclip', { start: obj.start, end: obj.end, autoplay: true });
                    });
                }

                self.showForm();

                var start;
                if (obj.startCode) {
                    start = obj.startCode;
                } else if (typeof obj.start !== 'undefined') {
                    start = secondsToCode(obj.start);
                }

                var end;
                if (obj.endCode) {
                    end = obj.endCode;
                } else if (typeof obj.end !== 'undefined') {
                    end = secondsToCode(obj.end);
                } else if (start) {
                    end = start;
                }
                ///Used to communicate with the clipstrip
                if (typeof start !== 'undefined') {
                    if (self.components.startField) {
                        self.components.startField.value = start;
                    }
                    if (self.components.startFieldDisplay) {
                        self.components.startFieldDisplay.innerHTML = start;
                    }
                    self.components.start = start;
                    self.events.signal(self.targetview, 'clipstart', { start: codeToSeconds(start) });
                }
                if (typeof end !== 'undefined') {
                    if (self.components.endField) {
                        self.components.endField.value = end;
                    }
                    if (self.components.endFieldDisplay) {
                        self.components.endFieldDisplay.innerHTML = end;
                    }
                    self.components.end = end;
                    self.events.signal(self.targetview, 'clipend', { end: codeToSeconds(end) });
                }

                if (options && options.mode === "browse") {
                    if (self.components.startField) {
                        self.components.startField.disabled = true;
                    }
                    if (self.components.endField) {
                        self.components.endField.disabled = true;
                    }
                    if (self.components.startButton) {
                        self.components.startButton.disabled = true;
                    }
                    if (self.components.endButton) {
                        self.components.endButton.disabled = true;
                    }

                    if (self.components.clipcontrols) {
                        self.components.clipcontrols.style.display = "none";
                    }
                } else {
                    // create, copy, edit
                    if (self.components.startField) {
                        self.components.startField.disabled = false;
                    }
                    if (self.components.endField) {
                        self.components.endField.disabled = false;
                    }
                    if (self.components.startButton) {
                        self.components.startButton.disabled = false;
                    }
                    if (self.components.endButton) {
                        self.components.endButton.disabled = false;
                    }

                    if (self.components.clipcontrols) {
                        self.components.clipcontrols.style.display = "inline";
                    }
                }
            }
        };

        this.storage = {
            update : function (obj, just_downstream) {
                if (!just_downstream) {
                    self.setState(obj);
                }
                if (self.targetstorage) {
                    for (var i = 0; i < self.targetstorage.length; i++) {
                        self.targetstorage[i].storage.update(obj);
                    }
                }
            }
        };

        this.initialize = function (create_obj) {
            var postStartButton = function(movieTime) {
                var movieTimeCode = secondsToCode(movieTime);
                if (self.components.startField) {
                    // update start time with movie time
                    self.components.startField.value = movieTimeCode;
                }

                if (self.components.endField &&
                    (movieTime > codeToSeconds(self.components.endField.value))
                   ) {
                    // update end time if start time is greater
                    self.components.endField.value = movieTimeCode;
                }
                self.storage.update(self.getState(), false);
            };
            self.events.connect(self.components.startButton, 'click', function (evt) {
                if (typeof self.targetview.media.getAsyncTime === 'function') {
                    self.targetview.media.getAsyncTime().then(function(time) {
                        postStartButton(time);
                    });
                } else {
                    var movieTime = self.targetview.media.time();
                    postStartButton(movieTime);
                }
            });

            var postEndButton = function(movieTime) {
                var movieTimeCode = secondsToCode(movieTime);

                if (self.targetview.media.pause) {
                    ///due to overwhelming user feedback for it to pause on clicking end-button
                    self.targetview.media.pause();
                }

                if (self.components.endField) {
                    // update the end time with movie time
                    self.components.endField.value = movieTimeCode;
                }

                // if the start time is greater then the endtime, make start time match end time
                if (self.components.startField &&
                    (movieTime < codeToSeconds(
                        self.components.startField.value))
                   ) {
                    self.components.startField.value = movieTimeCode;
                }

                self.storage.update(self.getState(), false);
            };
            self.events.connect(self.components.endButton, 'click', function (evt) {
                if (typeof self.targetview.media.getAsyncTime === 'function') {
                    self.targetview.media.getAsyncTime().then(function(time) {
                        postEndButton(time);
                    });
                } else {
                    var movieTime = self.targetview.media.time();
                    postEndButton(movieTime);
                }

            });
            self.events.connect(self.components.startField, 'change', function (evt) {
                var obj = self.getState();

                // if the start time is greater then the endtime, make end time match start time
                if (obj.end < obj.start) {
                    obj.end = obj.start;
                    obj.endCode = obj.startCode;
                    if (self.components.endField) {
                        // HTML
                        self.components.endField.value = obj.startCode;
                    }
                }
                self.storage.update(obj, false);
            });
            self.events.connect(self.components.endField, 'change', function (evt) {
                var obj = self.getState();

                // if the start time is greater then the endtime, make start time match end time
                if (obj.end < obj.start) {
                    obj.start = obj.end;
                    obj.startCode = obj.endCode;
                    if (self.components.startField) {
                        // HTML
                        self.components.startField.value = obj.endCode;
                    }
                }
                self.storage.update(obj, false);
            });
            self.events.connect(self.components.playClip, 'click', function (evt) {
                var obj = self.getState();
                self.events.signal(self.targetview, 'playclip', { start: obj.start, end: obj.end });
            });
        };

        this.showForm = function () {
            if (self.components.form) {
                self.components.form.style.display = "inline";
            }
        };

        this.hideForm = function () {
            if (self.components.form) {
                self.components.form.style.display = "none";
            }
        };

        this.microformat.create = function (obj) {
            var htmlID = 'clipform';
            return {
                htmlID : htmlID,
                text : '<div id="' + htmlID + '" style="display: none">' +
                '<div id="clipcontrols" class="sherd-clipform">' +
                   '<p id="instructions" style="display: none" class="sherd-instructions">' +
                       'Create a selection by clicking Start Time and End Time buttons as the video plays, ' +
                       'or by manually typing in times in the associated edit boxes.<br /><br />' +
                       'Add title, tags and notes. If a Course Vocabulary has been enabled by the instructor, ' +
                       'apply vocabulary terms. Click Save when you are finished.' +
                   '</p>' +
                      '<table>' +
                       '<tr><td span="0"><div><label for="annotation-title">Selection Times</label></div></td></tr>' +
                       '<tr class="sherd-clipform-editing">' +
                         '<td>' +
                           '<input type="button" class="btn-primary" value="Start Time" id="btnClipStart"/> ' +
                         '</td>' +
                         '<td width="10px">&nbsp;</td>' +
                         '<td>' +
                           '<input type="button" class="btn-primary" value="End Time" id="btnClipEnd"/> ' +
                         '</td>' +
                         '<td>&nbsp;</td>' +
                       '</tr>' +
                       '<tr class="sherd-clipform-editing">' +
                         '<td>' +
                           '<input type="text" class="timecode" id="clipStart" aria-label="clip start" value="' + self.components.start + '" />' +
                           '<div class="helptext timecode">HH:MM:SS</div>' +
                         '</td>' +
                         '<td style="width: 10px; text-align: center">-</td>' +
                         '<td>' +
                           '<input type="text" class="timecode" id="clipEnd" aria-label="clip end" value="' + self.components.end + '" />' +
                           '<div class="helptext timecode">HH:MM:SS</div>' +
                         '</td>' +
                         '<td class="sherd-clipform-play">' +
                         '<input type="image" title="Play Clip" class="regButton videoplay" id="btnPlayClip" src="' + STATIC_URL + 'img/icons/meth_video_play.png"/>' +
                         '</td>' +
                       '</tr>' +
                      '</table>' +
                '</div>'
            };
        };

        this.microformat.components = function (html_dom, create_obj) {
            return {
                'form' : html_dom,
                'startButton' : document.getElementById('btnClipStart'),
                'endButton' : document.getElementById('btnClipEnd'),
                'startField' : document.getElementById('clipStart'),
                'endField' : document.getElementById('clipEnd'),
                'startFieldDisplay' : document.getElementById('clipStartDisplay'),
                'endFieldDisplay' : document.getElementById('clipEndDisplay'),
                'playClip' : document.getElementById('btnPlayClip'),
                'clipcontrols' : document.getElementById('clipcontrols'),
                'start': "00:00:00",
                'end': "00:00:00"
            };
        };
    };
}
