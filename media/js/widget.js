
function insensitiveSort(a,b) {
  string = a + b
  a = a.toLowerCase()
  b = b.toLowerCase()
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

function move (from, to) {
    var fbox = new Array();
    var tbox = new Array();
    var lookup = new Array();

    // Copy data from 'to' and 'from' boxes into 'tbox' and 'fbox'
    // arrays; if an item in 'from' is selected, it gets moved into
    // 'tbox'.'lookup' holds the values of each option.
    for (i=0; i<to.length; i++) {
        if (to.options[i].value == -1) continue;
        lookup[to.options[i].text] = to.options[i].value;
        tbox[i] = to.options[i].text;
    }
    for (i=0; i<from.length; i++) {
        if (from.options[i].value == -1) continue;
        lookup[from.options[i].text] = from.options[i].value;
        if (from.options[i].selected)
            tbox[tbox.length] = from.options[i].text;
        else
            fbox[fbox.length] = from.options[i].text;
    }

    // Sort both of the arrays, then fill up the selection boxes with
    // the sorted values.
    fbox.sort(insensitiveSort);
    tbox.sort(insensitiveSort);
    from.length = 0;
    to.length = 0;

    // This is stupid. Mac IE has a nasty bug where, if a multiple selection
    // box is left empty, it seems to move the other selection box all over
    // the screen. So if the 'from' box is going to be empty, we fill it with
    // an empty option. We then check for this dummy option up above
    // (value == -1) to get rid of it when we don't need it.
    if (fbox.length == 0)
        from[0] = new Option('', -1);
    for (i=0; i<fbox.length; i++)
        from[i] = new Option(fbox[i], lookup[fbox[i]]);
    for (i=0; i<tbox.length; i++)
        to[i] = new Option(tbox[i], lookup[tbox[i]]);
}

function select_all (s) {
    for (i=0; i<s.length; i++)
        s.options[i].selected = 1;
}
