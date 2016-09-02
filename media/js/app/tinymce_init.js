/* global tinymce: true, STATIC_URL: true */

var tinymceSettings = {
    'browser_spellcheck': true,
    'convert_urls': false,
    'menubar': false,
    'plugins': 'compat3x, citation, code, editorwindow, image, link, ' +
        'paste, searchreplace, table, wordcount',
    'selector': '.mceEditor',
    'toolbar': 'bold, italic, underline, spacer, bullist, numlist, ' +
        'spacer, outdent, indent, spacer, undo, redo, spacer, link, ' +
        'unlink, image, spacer, code, pasteword',
    'content_css': STATIC_URL + 'css/project.css'
};
