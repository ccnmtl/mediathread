/* global _gaq: true */

/**
 * Listens For:
 * video.create > video of type x is instantiated.
 * video.play > play a video with a given id and type
 * video.pause > pause a video with a given id and type
 *
 * Signals:
 * Nothing
 */
/* exported MediathreadAnalytics */

var MediathreadAnalytics = function(tracker) {
    var self = this;
    self.tracker = tracker;

    // Fired by sherdjs video viewers
    jQuery(window).on(
        'video.create',
        {'self': self},
        function(event, id, type) {
            _gaq.push(['_trackEvent', 'video', 'create', type, id]);
        });

    jQuery(window).on(
        'video.play',
        {'self': self},
        function(event, id, type) {
            _gaq.push(['_trackEvent', 'video', 'play', type, id]);
        });

    jQuery(window).on(
        'video.pause',
        {'self': self},
        function(event, id, type) {
            _gaq.push(['_trackEvent', 'video', 'pause', type, id]);
        });

    jQuery(window).on(
        'video.finish',
        {'self': self},
        function(event, id, type) {
            _gaq.push(['_trackEvent', 'video', 'finish', type, id]);
        });
};
