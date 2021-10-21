/* global BrowserDetect: true, addLoadEvent: true */
/* exported shieldbrowser */

var browserblock = '<div class="nosupport_close"><a href="#" ' +
    'onclick="javascript:this.parentNode.parentNode.style.display=\'none\';' +
    ' return false;" title="Close this notice"></a></div>' +
    '<div class="browsers"> <div class="alert"> <div class="icon"></div>' +
    '<!-- class="icon" --> <div class="content"> <div class="title" ' +
    'id="nobrowserwarning">browsermsg1</div><!-- class="title" --> ' +
    '<div class="comment"><span id="minreqversion"></span>' +
    '<span id="nobrowsercomment">browsermsg2</span></div>' +
    '<!-- class="comment" --> </div><!-- class="content" -->' +
    '</div><!-- class="alert" --> <div class="solution"><div class="browser"' +
    ' id="chrome"> <div class="icon"></div><!-- class="icon" --> ' +
    '<div class="content"> <div class="title"> <a id="chromeurl" ' +
    'href="http://www.google.com/chrome/" title="Dowload the latest Google ' +
    'Chrome browser.">Chrome</a> </div><!-- class="title" --> </div>' +
    '<!-- class="content" --> </div><!-- class="chrome" --> ' +
    '<div class="browser" id="firefox"> <div class="icon"></div>' +
    '<!-- class="icon" --> <div class="content"> <div class="title"> ' +
    '<a id="firefoxurl" href="http://getfirefox.com" title="Dowload the ' +
    'latest Firefox browser.">Firefox</a> </div><!-- class="title" --> ' +
    '</div><!-- class="content" --> </div><!-- class="firefox" --> ' +
    '<div class="browser" id="safari"> <div class="icon"></div>' +
    '<!-- class="icon" --> <div class="content"> <div class="title"> ' +
    '<a id="safariurl" href="http://www.apple.com/safari/" ' +
    'title="Dowload the latest Safari browser.">Safari</a> </div>' +
    '<!-- class="title" --> </div><!-- class="content" --> </div>' +
    '<!-- class="safari" --> <div class="browser" id="msie"> ' +
    '<div class="icon"></div><!-- class="icon" --> <div class="content"> ' +
    '<div class="title"> <a id="ieurl" ' +
    'href="http://windows.microsoft.com/ie" title="Dowload the latest ' +
    'Internet Explorer browser.">Internet Explorer</a> </div><!-- ' +
    'class="title" --> </div><!-- class="content" --> </div>' +
    '<!-- class="msie" --> </div><!-- class="solution" --> ' +
    '<div class="visualclear"></div> </div><!-- browsers -->';

var browserlist;

function buildshieldbox() {
    if (!document.getElementById('shieldbox')) {
        return false;
    }
    var shieldwarningbox = document.getElementById('shieldbox');
    shieldwarningbox.className = 'warningmessage';

    shieldwarningbox.innerHTML = browserblock;

    var nobrowserwarningdiv = document.getElementById('nobrowserwarning');
    var nobrowsercommentdiv = document.getElementById('nobrowsercomment');

    nobrowserwarningdiv.innerHTML = 'You are using ' + BrowserDetect.browser +
        ' v.' + BrowserDetect.version + ', an unsupported browser.';

    nobrowsercommentdiv.innerHTML = '<br /><br />For a better experience ' +
        'using this site, please upgrade to a recommended recent web browser.';

    var thisbrowsername = null;
    if (BrowserDetect.browser === 'Internet Explorer') {
        thisbrowsername = 'MSIE';
    }
    for (var key in browserlist) {
        if (Object.prototype.hasOwnProperty.call(browserlist, key)) {
            if (BrowserDetect.browser.toLowerCase() === key.toLowerCase() ||
                (thisbrowsername && thisbrowsername.toLowerCase() ===
                    key.toLowerCase())) {
                document.getElementById('minreqversion').innerHTML =
                    'The minimum required version for this browser is ' +
                    browserlist[key] + '.';
            }
            var currentclass =
                document.getElementById(key.toLowerCase()).className;
            document.getElementById(key.toLowerCase()).className =
                currentclass + ' isrequired';
        }
    }
}

// eslint-disable-next-line no-unused-vars
function shieldbrowser(reqbrowser) {
    var browsername = false;
    var versionmismatch = false;

    var thisbrowsername = null;
    if (BrowserDetect.browser === 'Internet Explorer') {
        thisbrowsername = 'MSIE';
    }
    for (var key in reqbrowser) {
        if (BrowserDetect.browser.toLowerCase() === key.toLowerCase() ||
            (thisbrowsername && thisbrowsername.toLowerCase() ===
                key.toLowerCase())) {
            browsername = true;
            if ((BrowserDetect.version) < reqbrowser[key]) {
                versionmismatch = true;
            }
        }
    }
    if (!browsername || versionmismatch) {
        browserlist = reqbrowser;
        addLoadEvent(buildshieldbox);
    }
}
