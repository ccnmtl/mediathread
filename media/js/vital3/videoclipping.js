var iotime = 0;
var tctime;
var currtime = '';
var startime = '';
var endtime = '';
var clipType = 'Clip';
var grabTimer_id = null;
var grabber_id = null;
var endIntTime = null;
var startIntTime = null;
var stopAtEndTime = true;
var startTimeoutID = null;
var clipStripSelected = null;
var clipStripStart = null;
var clipStripRange = null;
var clipStripEnd = null;
var clipStripTarget;
var clipStripLength;
var theMovie;
var movDuration = 1;
var movscale = 600;

var CLIP_MARKER_WIDTH = 7;
// createLoggingPane();

function grabTime() {
    iotime = theMovie.GetTime();
    currtime = intToCode(iotime, tctime);
    $('currtime').innerHTML = currtime;
    if (endIntTime && iotime >= endIntTime && stopAtEndTime) {
        wd('grabTime: endIntTime,iotime', endIntTime, iotime);
        theMovie.Stop();
        stopAtEndTime = false;
    }
}

function startAtStartTime(autoplay) {
    function tryStart(autoplay) {
        try {
            if (testQT()) {
                jumpToStartTime(autoplay);
            }
        } catch (err) {
            startTimeoutID = window.setTimeout(function() {
                tryStart(autoplay);
            }, 300);
            wd('startAtStartTime() error:', err);
        }
    }
    ;
    tryStart(autoplay);
}

function jumpToEndTime() {
    playRate = parseInt(theMovie.GetRate(), 10);
    theMovie.Stop(); // HACK: QT doesn't rebuffer if we don't stop-start
    theMovie.SetTime(endIntTime);
    theMovie.SetRate(playRate);
    if (playRate != 0) {
        stopAtEndTime = false;
        theMovie.Play();
    }
}

function jumpToStartTime(autoplay) {
    playRate = parseInt(theMovie.GetRate(), 10);
    theMovie.Stop(); // HACK: QT doesn't rebuffer if we don't stop-start
    theMovie.SetTime(startIntTime);
    stopAtEndTime = true;
    if (!autoplay) {
        theMovie.SetRate(playRate);
    }
    if (autoplay || playRate != 0) {
        theMovie.Play();
    }
}

/**
 * Refactored into vitalwrapper.js. Soon to be deleted! function InMovieTime() { //
 * Set the Start Time if (currtime != '') { startime = currtime;
 * document.forms['videonoteform'].clipBegin.value = startime; startIntTime =
 * iotime; if (endIntTime < startIntTime) { wd('InMovieTime--bring end to
 * start', endIntTime, startIntTime); endtime = startime; stopAtEndTime = false;
 * endIntTime = startIntTime; document.forms['videonoteform'].clipEnd.value =
 * startime; } moveClipStrip(startIntTime, endIntTime); if
 * (document.forms['videonoteform'].clipType[1].checked) { //Marker cliptype
 * theMovie.Stop(); } initQtDuration(); } }
 * 
 * function OutMovieTime() { // Set the End Time if (currtime != '') { //
 * document.forms['videonoteform'].endsec.value = tctime.sec; //
 * document.forms['videonoteform'].endmin.value = tctime.min; //
 * document.forms['videonoteform'].endhrs.value = tctime.hr; endtime = currtime;
 * document.forms['videonoteform'].clipEnd.value = endtime; endIntTime = iotime;
 * if (endIntTime < startIntTime) { startime = endtime; startIntTime =
 * endIntTime; ; document.forms['videonoteform'].clipBegin.value = endtime; }
 * moveClipStrip(startIntTime, endIntTime); theMovie.Stop(); initQtDuration(); } }
 */

function formToClip() {
    startime = document.forms['videonoteform'].clipBegin.value;
    endtime = document.forms['videonoteform'].clipEnd.value;
    if (startime.match(/[^0-9:.]/))
        throw "Not a valid Start Time";
    if (endtime.match(/[^0-9:.]/))
        throw "Not a valid End Time";
    startIntTime = codeToInt(startime);
    endIntTime = codeToInt(endtime);
    moveClipStrip(startIntTime, endIntTime);
}

function codeToInt(code) {
    // takes a timecode like '0:01:36:00.0' and turns it into a QT int in frames
    var t = code.split(':');
    var x = t.pop();
    var intTime = 0;
    if (x.indexOf('.') >= 0) { // 00.0 format is in frames
        // ignore frames
        x = parseInt(t.pop(), 10);
    }
    var timeUnits = 1; // seconds -> minutes -> hours
    while (x || t.length > 0) {
        intTime += x * timeUnits * movscale;
        timeUnits *= 60;
        x = parseInt(t.pop(), 10);
    }
    return intTime;
}

function intToCode(intTime, myTC) {
    var tc = (myTC) ? myTC : {};
    intTime = Math.round(intTime / movscale);
    tc.hr = parseInt(intTime / 3600);
    tc.min = parseInt((intTime % 3600) / 60);
    tc.sec = intTime % 60;

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
}

function testQT() {
    // qtObj = document.movie1;
    if (typeof (theMovie) == 'undefined') {
        throw "movie object does not exist";
    }
    var status = theMovie.GetPluginStatus();
    if (status != 'Playable' && status != 'Complete') {
        throw "not ready to play yet";
    }
    movDuration = theMovie.GetDuration();
    movscale = theMovie.GetTimeScale();
    if (movDuration >= 2147483647) {
        throw "invalid duration returned";
    }
    movlen = intToCode(movDuration);

    testClip();
    return true;
}

function testClip() {
    if (clipType == 'Marker') {
        endtime = startime;
        if (typeof (theMovie) != 'undefined'
                && theMovie.GetPluginStatus() == 'Complete') {
            startIntTime = codeToInt(startime) - 100;
        } else {
            // If marker, then make starttime one second early and then movie
            // forward a second and stop
            startIntTime = codeToInt(startime) - 1000; // 1000 milliseconds = 1
                                                        // second
        }
    } else {
        startIntTime = codeToInt(startime);
    }
    endIntTime = codeToInt(endtime);
    if (theMovie.GetMaxTimeLoaded() < startIntTime) {
        throw "not enough of the movie downloaded";
    }
    initClipStrip();
}

function afterQTreallyLoads() {
    /*
     * If we can somehow know when QT has really really loaded (not just says
     * it's loaded) and all functions return valid values then this is what we
     * would run Since we can't do this, most of these are done 'just in time'
     * or quite redundantly
     */
    conformProportions(theMovie, 320, 240);
    movscale = theMovie.GetTimeScale();
    initQtDuration();
    initClipStrip();
}

function initQtDuration() {
    movDuration = theMovie.GetDuration();
    movlen = intToCode(movDuration);
    document.getElementById("totalcliplength").innerHTML = movlen;
}

function conformProportions(mymovie, w, h) {
    /*
     * This function still doesn't work when QT loads the movie in the
     * mini-window that comes up before it auto-sizes. When this function is run
     * then, it doubles the proportions and then QT re-doubles them and so we
     * only see a quarter of the screen. Somehow we need to 'know' when this is
     * happening. Maybe doing something special if GetMatrix returns 2,2,0 on
     * the diagonal? Ideally we would stop it from loading in that stupid little
     * window to begin with.
     */
    return;
    // ASSUME width is always greater than height
    // alert(theMovie.GetPluginStatus()+mymovie.GetRectangle()+mymovie.GetMatrix());

    var cur_wh = mymovie.GetRectangle().split(',');

    oldW = parseInt(cur_wh[2], 10) - parseInt(cur_wh[0], 10);
    oldH = parseInt(cur_wh[3], 10) - parseInt(cur_wh[1], 10);
    var newH = w * oldH / oldW;
    mymovie.SetRectangle("0,0," + w + "," + newH);

    matrix = mymovie.GetMatrix().split(',');
    // alert(mymovie.GetMatrix());
    matrix[5] = Math.round(h - newH);
    mymovie.SetMatrix(matrix.join(','));
    // alert('w'+w+' newH:'+newH+' '+theMovie.GetPluginStatus()+"--
    // "+matrix.join(','));
}

function speedset(string) {
    if (string = "normal") {
        document.movie1.SetRate(1.0);
    }
    if (string = "slow") {
        document.movie1.SetRate(0.4);
    }
}

function clipStripPos(timeCodeInteger) {
    if (!clipStripTarget) {
        clipStripTarget = $('clipStripTrack');
        clipStripStart = $('clipStripStart');
        clipStripRange = $('clipStripRange');
        clipStripEnd = $('clipStripEnd');
        clipStripLength = parseInt(clipStripTarget.offsetWidth, 10);
    }
    try {
        movDuration = theMovie.GetDuration();
    } catch (err) {/* who cares */
    }
    var ratio = clipStripLength / movDuration;
    return ratio * timeCodeInteger;
}

function moveClipStrip(intStartTime, intEndTime, noteID) {
    left = clipStripPos(intStartTime);
    right = clipStripPos(intEndTime);
    if (noteID) {
        // i forget why i had this conditional
    }
    // else {
    clipStripStart.style.left = parseInt(left - CLIP_MARKER_WIDTH + 2, 10) + 'px';
    clipStripRange.style.left = left + 'px';
    clipStripRange.style.width = parseInt(right - left, 10) + 'px';
    clipStripEnd.style.left = right + 'px';

    clipStripStart.style.display = 'block';
    clipStripRange.style.display = 'block';
    clipStripEnd.style.display = 'block';
    // }

}

function initClipStrip() {
    try {
        moveClipStrip(startIntTime, endIntTime);
        if (!currentUID()) {
            clipStripStart.style.display = 'none';
            clipStripRange.style.display = 'none';
            clipStripEnd.style.display = 'none';
        }

    } catch (err) {
        logError('clipstrip failed to init', err);
    }
}

function addNoteStrip(noteID, noteclass) {
    var n = myNoteDetails[noteID];
    var left = clipStripPos(codeToInt(n.clipBegin));

    var width = (n.clipType == 'Marker') ? 3
            : width = clipStripPos(codeToInt(n.clipEnd)) - left;
    var strip = DIV( {
        'id' : 'clipStrip_' + noteID,
        'class' : noteclass,
        'style' : 'width:' + width + 'px;left:' + left + 'px'
    });
    clipStripTarget.appendChild(strip);

    strip.onmouseover = partial(function(t) {
        $('clipStripTitle').innerHTML = t;
    }, n.title);
    strip.onclick = partial(editNote, noteID);
}

function addNoteStrips() {
    var specialID = (document.forms['videonoteform'].uid) ? document.forms['videonoteform'].uid.value
            : 'noSpecial';

    for (noteID in myNoteDetails) {
        var noteclass = (specialID == noteID) ? 'noteSelected' : 'noteStrip';
        addNoteStrip(noteID, noteclass);
    }
}

function giveUp() {
    clearTimeout(grabTimer_id);
    clearTimeout(grabber_id);
    clearTimeout(startTimeoutID);
}

// mochikit debug messages can mess up playback.
var debug = false;

function wd(str) {
    if (debug) {
        logDebug(str);
    }
}

function prepareGrabber() {
    theMovie = document.movie1;
    if (!theMovie)
        theMovie = document.getElementById('movie1');

    if (theMovie != null) { // don't test GetPluginStatus here because IE fails
        try {
            if (testQT()) {
                // if we get past it, it worked and it's ready.

                // this seems to be the problem:
                grabTimer_id = setInterval(grabTime, 500);

                // addNoteStrips();
                initQtDuration();
                conformProportions(theMovie, 320, 240);
                wd('finally starting, duration:', movDuration, theMovie
                        .GetPluginStatus(), theMovie.GetRate());
                return;
            }
        } catch (err) {
            // otherwise try again
            wd('try again', err);
            grabber_id = setTimeout(prepareGrabber, 500);
            return;
        }
    }
    // otherwise try again
    grabber_id = setTimeout(prepareGrabber, 500);
}

function refresh_mymovie(stime, etime, cType) {
    /* my_movie is defined where the movie is written.  
     * It's basically a shell for the arguments for the qt movie
     */
    //the first two lines here are overkill but
    //necessary, so Safari doesn't keep the audio track
    //of the original movie clip
    if (stime) {
        startime = stime;
        endtime = etime;
        clipType = cType;
        startAtStartTime(/*autoplay=*/true);
    }
}

addLoadEvent(prepareGrabber);
