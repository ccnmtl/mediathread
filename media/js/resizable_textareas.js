var DEFAULT_WIDTH = "400";
var DEFAULT_HEIGHT = "150";

var handle_map = {};

Drag = {
      _move: null,
      _down: null,
    
   start: function(e) {
      log("dragging " + e.target());
      e.stop();
        
        // We need to remember what we're dragging.
      Drag._target = e.target();
        
        /*
            There's no cross-browser way to get offsetX and offsetY, so we
            have to do it ourselves. For performance, we do this once and
            cache it.
        */

      try {
	 Drag._offset = Drag._diff(
				   e.mouse().page,
				   getElementPosition(Drag._target));
	 Drag._tadim = getElementDimensions(handle_map[Drag._target.id]);
	 }
      catch (err) {
	 alert(err);
	 }
      Drag._lastmouse = e.mouse().page,
      Drag._move = connect(document, 'onmousemove', Drag._drag);
      Drag._down = connect(document, 'onmouseup', Drag._stop);
   },

      _offset: null,
      _target: null,
      _tadim: null,
      _lastmouse: null,
    
      _diff: function(lhs, rhs) {
         return new MochiKit.Style.Coordinates(lhs.x - rhs.x, lhs.y - rhs.y);
      },
      _ddiff: function(lhs, rhs) {
	 return new MochiKit.Style.Dimensions(lhs.w - rhs.w, lhs.h - rhs.h);
      },
        
      _drag: function(e) {
         e.stop();
	 var ta = handle_map[Drag._target.id];
         setElementPosition(Drag._target,Drag._diff(e.mouse().page, Drag._offset));
	 var mousediff = Drag._diff(e.mouse().page, Drag._lastmouse);
	 setElementDimensions(ta, {w : Drag._tadim.w + mousediff.x, 
	    h : Drag._tadim.h + mousediff.y});
      },
    
      _stop: function(e) {
         disconnect(Drag._move);
         disconnect(Drag._down);
      }
};

function makeResizable(ta) {    
   var parent = ta.parentNode;
   var handle = IMG({'width' : "20", "height" :
         "20", "alt" : "", "src" :
         "http://www2.ccnmtl.columbia.edu/images/winresize.gif", "class" : "resize-handle",
      "id" : ta.name + "-handle"});
   parent.appendChild(handle);
   handle_map[handle.id] = ta;

   var tadim = getElementDimensions(ta);
   var tapos = getElementPosition(ta);

   setElementPosition(handle,{x : tapos.x + tadim.w, y : tapos.y + tadim.h});
   connect(handle, 'onmousedown', Drag.start);
}                               
                                
                                
function initTextAreas () {     
   forEach(getElementsByTagAndClassName('textarea','resizable'),
	   function (ta) {makeResizable(ta);});
};
                                
addLoadEvent(initTextAreas);
