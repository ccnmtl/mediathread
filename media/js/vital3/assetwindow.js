leftPos = 0
if (screen) {
	leftPos = screen.width-550
}

function assetWindow(pop, title) {

var popWindow = window.open(pop, title,'left='+leftPos+',top=0,toolbar=0,location=0,directories=0,status=0,menubar=0,scrollbars=1,resizable=1,width=820,height=550');

popWindow.focus();

}

function openPopWin(theURL,w,h,resizing,scrolling,winname) {
	var winl = (screen.width - w) / 2;
	var wint = (screen.height - h) / 2;
	winprops = 'height='+h+',width='+w+',top='+wint+',left='+winl+',resizable='+resizing+',scrollbars='+scrolling+',location=no,status=no,menubar=no,directories=no,toolbar=no'
	popwin = window.open(theURL, winname, winprops)
	if (parseInt(navigator.appVersion) >= 4) { popwin.window.focus(); }
	if (popwin.opener == null) popwin.opener = self;
}

function openCitation(url) {
    // baseUrl is defined in the essayWorkspace template:
    openPopWin(baseUrl+url ,480,400,0,9,'videoviewer');
}

function addMaterialCitation(evt) {
    //createLoggingPane();
    evt = (evt) ? evt : window.event;
    var eTarget= (evt.target) ? evt.target : evt.srcElement;
    var citation =eTarget; //.firstChild;
    linkTitle=citation.getAttribute('title');
    linkName=citation.getAttribute('name');

    //removing extraneous 0's in the timecode
    linkTitle=linkTitle.replace(/([ -])0:/g,"$1");
    linkTitle=linkTitle.replace(/([ -])0/g,"$1");

    cite_text='&#160;<input type="button" class="materialCitation" onclick="openCitation(\''+linkName+'\')" name="'+linkName+'" value="'+linkTitle+'" />&#160;';
    insertTinyMCEcontent(cite_text,'note');
}

function insertTinyMCEcontent(html_string, textarea_node_or_id) {
    if (!tinyMCE.isSafari) {
	tinyMCE.execCommand('mceInsertContent',false,html_string);
    }
    else { //SAFARI SUCKS!
	/* This is a work around for Safari not setting content on
	   TEXTAREAs which have style display:none
	*/
	var n=$(textarea_node_or_id);
	var nid = n.id;
	//tinyMCE.triggerSave(); //SHOULD WORK BUT DOESN'T so we use getContent
	html_string = tinyMCE.getContent()+html_string;

	var x=n.cloneNode(true);
	x.setAttribute('style',null);
	var p=n.parentNode;
	p.replaceChild(x,n);
	
	x.value=html_string;
	x.setAttribute('id',nid);
	x.style.display='none';

	//tinyMCE.updateContent(nid);  //SHOULD WORK BUT DOESN'T so we use setContent
	tinyMCE.setContent(x.value);
    }
}

function confirmDelete() {
	
	if (confirm("Are you sure you want to delete these?")) {
		return true;
	} else {
		return false;
	}
}
