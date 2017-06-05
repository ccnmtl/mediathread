/* global Sherd: true */
//Use Cases:
//Default
//-- starttime:0, endtime:0

//Signals:
//seek: when a user clicks on the start/end time of the ClipPlay, sends a seek event out

if (!Sherd) {Sherd = {}; }
if (!Sherd.Video) {Sherd.Video = {}; }
if (!Sherd.Video.Annotators) {Sherd.Video.Annotators = {}; }
if (!Sherd.Video.Annotators.ClipPlay) {
    Sherd.Video.Annotators.ClipPlay = function () {
        var self = this;

        Sherd.Video.Base.apply(this, arguments); //inherit off video.js - base.js

        this.attachView = function (view) {
            this.targetview = view;
        };

        this.getState = function () {
            var obj = {};

            obj.starttime = self.components.starttime;
            obj.endtime = self.components.endtime;
            return obj;
        };

        this.setState = function (obj) {
            if (typeof obj === 'object') {
                var c = self.components;
                if (obj === null) {
                    c.starttime = c.endtime = 0;
                } else {
                    c.starttime = obj.start || 0;
                    c.endtime = obj.end || c.starttime;
                }
                return true;
            }
        };

        this.initialize = function (create_obj) {
            self.events.connect(self.components.clipPlay, 'click', function (evt) {
                var obj = self.getState();
                self.events.signal(
                    self.targetview, 'playclip',
                    {start: obj.starttime, end: obj.endtime, autoplay: true});
            });
        };

        this.microformat.create = function (obj) {
            return {
                htmlID: 'play-selection',
                text: '<button class="btn btn-sm btn-default"' +
                    'id="play-selection">' +
                    'Play Selection ' +
                    '<span class="glyphicon glyphicon-play" ' +
                    'aria-hidden="true"></span></button>'
            };
        };

        // self.components -- Access to the internal player and any options needed at runtime
        this.microformat.components = function (html_dom, create_obj) {
            try {
                return {
                    clipPlay: document.getElementById(create_obj.htmlID),
                    starttime: 0,
                    endtime: 0,
                };
            } catch (e) {}
            return false;
        };
    };/* function Sherd.Video.Annotators.ClipPlay() */
        
}/*if !ClipPlay...*/
