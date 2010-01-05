var Dom = YAHOO.util.Dom;
var Event = YAHOO.util.Event;
var Element = YAHOO.util.Element;

var myConfig = {
    //defer to CSS instead
    //height: '400px'
    //,width: '350px'
    animate: true
    //,dompath: true
    ,focusAtStart: true
    ,markup:'xhmtl'
    ,ptags:true
    ,filterWord:true
};
var TEXTAREA_ID = 'project-body-field';
var myEditor;
Event.onAvailable(TEXTAREA_ID,function(evt) {
    myEditor = new YAHOO.widget.Editor(TEXTAREA_ID, myConfig);
    //CSS is all broked if this isn't true.
    (new Element(document.getElementById(TEXTAREA_ID).parentNode)).addClass('yui-skin-sam');

    moreBasicToolbar.apply(myEditor);
    //myEditor.on('toolbarLoaded', function () {myEditor.toolbar.collapse();}, myEditor, true);
    
    Sherd.Cite.YUIEditor.apply(myEditor);

    myEditor.render(); 

});//Event.onAvailable

function moreBasicToolbar() {
    this._defaultToolbar.grouplabels=false;
    this._defaultToolbar.titlebar=false;//'hello';  
    this._defaultToolbar.buttonType = 'basic';    

    var fontstyle = this._defaultToolbar.buttons[2];
    fontstyle.buttons.splice(3,3);
    var indenting = this._defaultToolbar.buttons[12];
    var linking = this._defaultToolbar.buttons[14];
    this._defaultToolbar.buttons = [fontstyle, indenting, linking];
}

/* Requires YUI:
  <link rel="stylesheet" type="text/css" href="../lib/yui2/assets/yui.css" >
  <link rel="stylesheet" type="text/css" href="../lib/yui2/build/menu/assets/skins/sam/menu.css" />
  <link rel="stylesheet" type="text/css" href="../lib/yui2/build/button/assets/skins/sam/button.css" />
  <link rel="stylesheet" type="text/css" href="../lib/yui2/build/container/assets/skins/sam/container.css" />
  <link rel="stylesheet" type="text/css" href="../lib/yui2/build/editor/assets/skins/sam/editor.css" />

  <script type="text/javascript" src="../lib/yui2/build/yuiloader/yuiloader-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/event/event-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/dom/dom-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/animation/animation-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/element/element-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/container/container-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/menu/menu-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/button/button-min.js"></script>
  <script type="text/javascript" src="../lib/yui2/build/editor/editor-min.js"></script>
*/
