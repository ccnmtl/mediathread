/*----------------------------------------------------------------------------\
|                                Table Sort                                   |
|-----------------------------------------------------------------------------|
|                         Created by Erik Arvidsson                           |
|                  (http://webfx.eae.net/contact.html#erik)                   |
|                      For WebFX (http://webfx.eae.net/)                      |
|-----------------------------------------------------------------------------|
| A DOM 1 based script that allows an ordinary HTML table to be sortable.     |
|-----------------------------------------------------------------------------|
|                  Copyright (c) 1998 - 2002 Erik Arvidsson                   |
|-----------------------------------------------------------------------------|
| This software is provided "as is", without warranty of any kind, express or |
| implied, including  but not limited  to the warranties of  merchantability, |
| fitness for a particular purpose and noninfringement. In no event shall the |
| authors or  copyright  holders be  liable for any claim,  damages or  other |
| liability, whether  in an  action of  contract, tort  or otherwise, arising |
| from,  out of  or in  connection with  the software or  the  use  or  other |
| dealings in the software.                                                   |
| - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - |
| This  software is  available under the  three different licenses  mentioned |
| below.  To use this software you must chose, and qualify, for one of those. |
| - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - |
| The WebFX Non-Commercial License          http://webfx.eae.net/license.html |
| Permits  anyone the right to use the  software in a  non-commercial context |
| free of charge.                                                             |
| - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - |
| The WebFX Commercial license           http://webfx.eae.net/commercial.html |
| Permits the  license holder the right to use  the software in a  commercial |
| context. Such license must be specifically obtained, however it's valid for |
| any number of  implementations of the licensed software.                    |
| - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - |
| GPL - The GNU General Public License    http://www.gnu.org/licenses/gpl.txt |
| Permits anyone the right to use and modify the software without limitations |
| as long as proper  credits are given  and the original  and modified source |
| code are included. Requires  that the final product, software derivate from |
| the original  source or any  software  utilizing a GPL  component, such  as |
| this, is also licensed under the GPL license.                               |
|-----------------------------------------------------------------------------|
| 1998-??-?? | First version                                                  |
|-----------------------------------------------------------------------------|
| Created 1998-??-?? | All changes are in the log above. | Updated 2001-??-?? |
|-----------------------------------------------------------------------------|
| Also, modified by Anders Pearson to make this work with Safari, and to make |
| the HTML more standard compliant.                                           |
| Zarina Mustapha made some changes to highlight the sorted columns, and      |
| added the zebra table                                                       |
|-----------------------------------------------------------------------------|
| 2004 Summer | Modified                                                      |
\----------------------------------------------------------------------------*/


var dom = (document.getElementsByTagName) ? true : false;
var ie5 = (document.getElementsByTagName && document.all) ? true : false;
var arrowUp, arrowDown;

if (ie5 || dom)
	initSortTable();

function initSortTable() {
			imgup = this.document.createElement("img");
			imgup.src = "/site_media/img/ascending.png";
	arrowUp = document.createElement("span");
	arrowUp.appendChild(imgup);
	arrowUp.className = "arrow";

			imgdwn = this.document.createElement("img");
			imgdwn.src = "/site_media/img/descending.png";
	arrowDown = document.createElement("span");
	arrowDown.appendChild(imgdwn);
	arrowDown.className = "arrow";
}



function initStripes()
{
    var tables = document.getElementsByTagName('TABLE');
    for (var h = 0; h < tables.length; h++)
    {
		classesT = tables[h].className;
		if (classesT=='striped') {assignTROddEven(document.getElementsByTagName('TABLE')[h].getElementsByTagName('TBODY')[0]);}
	}
}

function hilite(tableNode,nCol)
{
	var thead = tableNode.getElementsByTagName('THEAD')[0];
	var trows = thead.getElementsByTagName('TR')[0];
	var ths = trows.getElementsByTagName('TH');
	for (var i = 0; i < ths.length; i++) {
            classes = ths[i].className.split(" ");
            new_classes = "";
            for (var j = 0; j < classes.length; j++) {
                if ((classes[j] == "TableSortSelected") || 
                    (classes[j] == "TableSortUnselected")) {
                } else {
                    new_classes += " " + classes[j];
                }
            }
            new_classes += " TableSortUnselected";
            ths[i].className = new_classes;
        }
        classes = ths[nCol].className.split(" ");
        new_classes = "";
        for (var j = 0; j < classes.length; j++) {
            if ((classes[j] == "TableSortSelected") || 
                (classes[j] == "TableSortUnselected")) {
            } else {
                new_classes += " " + classes[j];
            }
        }
        new_classes += " TableSortSelected";
        ths[nCol].className = new_classes;
        
}



function hilitecolumn(tableNode,nCol)
{
	var tbodies = tableNode.getElementsByTagName('TBODY')[0];
	var trows = tbodies.getElementsByTagName('TR');
	
	for (var i = 0; i < trows.length; i++)
	{
		var tds = trows[i].getElementsByTagName("TD");

		for (var j = 0; j < tds.length; j++)
		{
			if (j==nCol) {tds[j].className='TableSortSelected';}
			else {tds[j].className='plain'}
		}

	}
}


function sortTable(tableNode, nCol, bDesc, sType) {
	var tBody = tableNode.tBodies[0];
	var trs = tBody.rows;
	var trl= trs.length;
	var a = new Array();
	
	for (var i = 0; i < trl; i++) {
		a[i] = trs[i];
	}
	
	var start = new Date;
	window.status = "Sorting data...";
	a.sort(compareByColumn(nCol,bDesc,sType));
	window.status = "Sorting data done";
	
	for (var i = 0; i < trl; i++) {
		tBody.appendChild(a[i]);
//		window.status = "Updating row " + (i + 1) + " of " + trl +
//						" (Time spent: " + (new Date - start) + "ms)";
	}
	
	// check for onsort
	if (typeof tableNode.onsort == "string")
		tableNode.onsort = new Function("", tableNode.onsort);
	if (typeof tableNode.onsort == "function")
		tableNode.onsort();
}

function CaseInsensitiveString(s) {
	return String(s).toUpperCase();
}

function parseDate(s) {
	return Date.parse(s.replace(/\-/g, '/'));
}

/* alternative to number function
 * This one is slower but can handle non numerical characters in
 * the string allow strings like the follow (as well as a lot more)
 * to be used:
 *    "1,000,000"
 *    "1 000 000"
 *    "100cm"
 */

function Numeric(s) {
    return Number(s.replace(/[^0-9\.]/g, ""));
}

function compareByColumn(nCol, bDescending, sType) {
	var c = nCol;
	var d = bDescending;
	
	var castFunc =(sType in TableSortCasts) ?TableSortCasts[sType] :TableSortCasts["Default"];

	return function (n1, n2) {
	        if (castFunc(n1.cells[c]) < castFunc(n2.cells[c]))
			return d ? -1 : +1;
		if (castFunc(n1.cells[c]) > castFunc(n2.cells[c]))
			return d ? +1 : -1;
		return 0;
	};
}

function sortColumnWithHold(e) {
	// find table element
	var el = ie5 ? e.srcElement : e.target;
	var table = getParent(el, "table");
	
	// backup old cursor and onclick
	var oldCursor = table.style.cursor;
	var oldClick = table.onclick;
	
	// change cursor and onclick	
	table.style.cursor = "wait";
	table.onclick = null;
	
	// the event object is destroyed after this thread but we only need
	// the srcElement and/or the target
	var fakeEvent = {srcElement : e.srcElement, target : e.target};
	
	// call sortColumn in a new thread to allow the ui thread to be updated
	// with the cursor/onclick
	window.setTimeout(function () {
		sortColumn(fakeEvent);
		// once done resore cursor and onclick
		table.style.cursor = oldCursor;
		table.onclick = oldClick;
	}, 100);
}

function sortColumn(e) {
	var tmp = e.target ? e.target : e.srcElement;
	var tHeadParent = getParent(tmp, "thead");
	if (tHeadParent == null)
		return;
		
	var tbodyParent = getParent(tmp, "tbody");
	var el = getParent(tmp, "th");

        if (el != null && !/NoSort/.test(el.className)) {
		var p = el.parentNode;
		var i;

		// typecast to Boolean
		el._descending = !Boolean(el._descending);

		if (tHeadParent.arrow != null) {
			if (tHeadParent.arrow.parentNode != el) {
				tHeadParent.arrow.parentNode._descending = null;	//reset sort order		
			}
			tHeadParent.arrow.parentNode.removeChild(tHeadParent.arrow);
		}

		if (el._descending)
			tHeadParent.arrow = arrowUp.cloneNode(true);
		else
			tHeadParent.arrow = arrowDown.cloneNode(true);

		el.appendChild(tHeadParent.arrow);

			

		// get the index of the td
		var cells = p.cells;
                var cs = p.childNodes;
		var l = cs.length;
                th_idx = 0
		for (i = 0; i < l; i++) {
			if (cs[i] == el) break;
                        if (cs[i].nodeType == 1) {
                            if (cs[i].nodeName == "TH") {
                               th_idx++;
                               }
                            if (cs[i].nodeName == "TD") {
                               th_idx++;
                            }
                        }
		}

		var table = getParent(el, "table");
		var tbody = table.getElementsByTagName('TBODY')[0];
		// can't fail

                var uA = navigator.userAgent;
                var aN = navigator.appName;
                var aV = navigator.vendor;
                var IEbrowser = (uA.indexOf('MSIE') != - 1);

                var classes = ""
                if (IEbrowser) {
                    classes = el.className
                } else {
	            classes = el.getAttribute("class")
                }
                classes = classes ? classes : ""
                classes = classes.split(" ")
                var type = "Default";
                for (var idx = 0; idx < classes.length; idx++) {
		    if (classes[idx] in TableSortCasts)	type = classes[idx];
                } 
		sortTable(table,th_idx,el._descending, type);
		hilite(table,th_idx);
		hilitecolumn(table,th_idx);

		classesT = table.className;
		if (classesT=='striped') {assignTROddEven(tbody);}
		
	}
}

function assignTROddEven(tbody) {
	var tr = firstRealChild(tbody);
	var odd = false;
	while (tr) {
		tr.className = odd ? '' : 'odd';
		odd = !odd;
		tr = nextRealSibling(tr);
	}
}


function firstRealChild(parent) {
	var child = parent.firstChild;
	while (child && child.nodeType != 1) child = child.nextSibling;
	return child;
}

function nextRealSibling(el) {
	do el = el.nextSibling
	while (el && el.nodeType != 1);
	return el;
}

function getInnerText(el) {
        if (el.textContent) return el.textContent;

	if (el.innerText) return el.innerText;	//Not needed but it is faster

	var str = "";
	
	var cs = el.childNodes;
	var l = cs.length;
	for (var i = 0; i < l; i++) {
		switch (cs[i].nodeType) {
			case 1: //ELEMENT_NODE
				str += getInnerText(cs[i]);
				break;
			case 3:	//TEXT_NODE
				str += cs[i].nodeValue;
				break;
		}
		
	}
	
	return str;
}

function getParent(el, pTagName) {
	if (el == null) return null;
	else if (el.nodeType == 1 && el.tagName.toLowerCase() == pTagName.toLowerCase())	
// Gecko bug, supposed to be uppercase
		return el;
	else
		return getParent(el.parentNode, pTagName);
}

var TableSortCasts = {
    "Number":function(cell){return Numeric(getInnerText(cell));},
    "Date":function(cell){return parseDate(getInnerText(cell));},
    "DateTime":function(cell){
        var timetag = cell.getElementsByTagName('time');
        if (timetag.length) {
            return (timetag[0].datetime || Date.parse(timetag[0].getAttribute('datetime').split('.')[0]));
        }
    },
    "CaseInsensitiveString":function(cell){return CaseInsensitiveString(getInnerText(cell));},
    "Default":function(cell){return String(getInnerText(cell));},
}