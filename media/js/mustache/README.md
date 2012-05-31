# mustache.js — Logic-less templates with JavaScript

> What could be more logical awesome than no logic at all?

For a list of implementations (other than JavaScript) and editor
plugins, see <http://mustache.github.com/>.


## Where to Use?

You can use mustache.js rendering stuff in various scenarios. E.g. you can
render templates in your browser, or rendering server-side stuff with
[node.js][node.js], use it for rendering stuff in [CouchDB][couchdb]’s views.


## Who Uses Mustache?

An updated list is kept on the Github wiki. Add yourself, if you use
mustache.js: <http://wiki.github.com/janl/mustache.js/beard-competition>


## Usage

A quick example how to use mustache.js:

    var view = {
      title: "Joe",
      calc: function() {
        return 2 + 4;
      }
    }

    var template = "{{title}} spends {{calc}}";

    var html = Mustache.to_html(template, view);

`template` is a simple string with mustache tags and `view` is a JavaScript
object containing the data and any code to render the template.

To precompile the template for repeated use:
 
    Mustache.template("Spent Template", template);
    
    var html = Mustache.tmpl("Spent Template", view);

This saves the template in the key "Spent Template" where you can render the same
template with different `view`s many times without re-compiling the template.

## Template Tag Types

There are several types of tags currently implemented in mustache.js.

For a language-agnostic overview of Mustache’s template syntax, see the
`mustache(5)` manpage or <http://mustache.github.com/mustache.5.html>.

### Simple Tags

Tags are always surrounded by mustaches like this `{{foobar}}`.

    var view = {name: "Joe", say_hello: function(){ return "hello" }}

    template = "{{say_hello}}, {{name}}"


### Conditional Sections

Conditional sections begin with `{{#condition}}` and end with
`{{/condition}}`. When `condition` evaluates to true, the section is rendered,
otherwise the whole block will output nothing at all. `condition` may be a
function returning true/false or a simple boolean.

    var view = {condition: function() {
      // [...your code goes here...]
      return true;
    }}

    {{#condition}}
      I will be visible if condition is true
    {{/condition}}


### Enumerable Sections

Enumerable Sections use the same syntax as condition sections do.
`{{#shopping_items}}` and `{{/shopping_items}}`. Actually the view decides how
mustache.js renders the section. If the view returns an array, it will
iterator over the items. Use `{{.}}` to access the current item inside the
enumeration section.

    var view = {name: "Joe's shopping card",
                items: ["bananas", "apples"]}

    var template = "{{name}}: <ul> {{#items}}<li>{{.}}</li>{{/items}} </ul>"

    Outputs:
    Joe's shopping card: <ul><li>bananas</li><li>apples</li></ul>


### Higher Order Sections

If a section key returns a function, it will be called and passed both the
unrendered block of text and a renderer convenience function.

Given this JS:

    "name": "Tater",
    "bolder": function() {
      return function(text, render) {
        return "<b>" + render(text) + '</b>'
      }
    }

And this template:

    {{#bolder}}Hi {{name}}.{{/bolder}}

We'll get this output:

    <b>Hi Tater.</b>

As you can see, we’re pre-processing the text in the block. This can be used
to implement caching, filters (like syntax highlighting), etc.

You can use `this.name` to access the attribute `name` from your view.

### Dereferencing Section

If you have a nested object structure in your view, it can sometimes be easier
to use sections like this:

    var objects = {
      a_object: {
        title: 'this is an object',
        description: 'one of its attributes is a list',
        a_list: [{label: 'listitem1'}, {label: 'listitem2'}]
      }
    };

This is our template:

    {{#a_object}}
      <h1>{{title}}</h1>
      <p>{{description}}</p>
      <ul>
        {{#a_list}}
          <li>{{label}}</li>
        {{/a_list}}
      </ul>
    {{/a_object}}

Here is the result:

    <h1>this is an object</h1>
      <p>one of its attributes is a list</p>
      <ul>
        <li>listitem1</li>
        <li>listitem2</li>
      </ul>

### Inverted Sections

An inverted section opens with `{{^section}}` instead of `{{#section}}` and
uses a boolean negative to evaluate. Empty arrays are considered falsy.

View:

    var inverted_section =  {
      "repo": []
    }

Template:

    {{#repo}}<b>{{name}}</b>{{/repo}}
    {{^repo}}No repos :({{/repo}}

Result:

    No repos :(


### View Partials

mustache.js supports a quite powerful but yet simple view partial mechanism.
Use the following syntax for partials: `{{>partial_name}}`

    var view = {
      name: "Joe",
      winnings: {
        value: 1000,
        taxed_value: function() {
            return this.value - (this.value * 0.4);
        }
      }
    };

    var template = "Welcome, {{name}}! {{>winnings}}"
    var partials = {
      winnings: "You just won ${{value}} (which is ${{taxed_value}} after tax)"};

    var output = Mustache.to_html(template, view, partials)

    output will be:
    Welcome, Joe! You just won $1000 (which is $600 after tax)

You invoke a partial with `{{>winnings}}`. Invoking the partial `winnings`
will tell mustache.js to look for a object in the context's property
`winnings`. It will then use that object as the context for the template found
in `partials` for `winnings`.

## Internationalization

mustache.js supports i18n using the `{{_i}}{{/i}}` tags.  When mustache.js encounters
an internationalized section, it will call out to the standard global gettext function `_()` with the tag contents for a
translation _before_ any rendering is done.  For example:

    var template = "{{_i}}{{name}} is using mustache.js!{{/i}}"

    var view = {
      name: "Matt"
    };

    var translationTable = {
      // Welsh, according to Google Translate
      "{{name}} is using mustache.js!": "Mae {{name}} yn defnyddio mustache.js!"
    };

    function _(text) {
      return translationTable[text] || text;
    }

    alert(Mustache.to_html(template, view));
    // alerts "Mae Matt yn defnyddio mustache.js!"

### The TRANSLATION-HINT Pragma

Some single words in English have different translations based on usage context.  Mustache.js supports this with the TRANSLATION-HINT pragma.  For example, the word "Tweet" can be used as a noun, or a verb.  The following template is ambiguous:

    <div class="tweet-button">{{_i}}Tweet{{/i}}</div>

By adding a pragma, we can provide the right context for a given template:

    {{%TRANSLATION-HINT mode=tweet_button}}

    <div class="tweet-button">{{_i}}Tweet{{/i}}</div>

This will lookup every translation in that template with the mode, e.g. `_('Tweet', {mode: "tweet_button"})`, which your gettext implementation can handle as appropriate.

## Escaping

mustache.js does escape all values when using the standard double mustache
syntax. Characters which will be escaped: `& \ " ' < >`. To disable escaping,
simply use triple mustaches like `{{{unescaped_variable}}}`.

Example: Using `{{variable}}` inside a template for `5 > 2` will result in `5 &gt; 2`, where as the usage of `{{{variable}}}` will result in `5 > 2`.


## Streaming

To stream template results out of mustache.js, you can pass an optional
`send()` callback to the `to_html()` call:

    Mustache.to_html(template, view, partials, function(line) {
      print(line);
    });


## Pragmas

Pragma tags let you alter the behaviour of mustache.js. They have the format
of

    {{%PRAGMANAME}}

and they accept options:

    {{%PRAGMANAME option=value}}

You can also activate the pragma for all templates with:

    Mustache.set_pragma_default(<PRAGMANAME>, <options>, <pragma code>)

So, to activate implicit iterator, without it appearing in the templates, you would run
  
    Mustache.set_pragma_default('IMPLICIT-ITERATOR',{iterator:'bob'})


### IMPLICIT-ITERATOR

When using a block to iterate over an enumerable (Array), mustache.js expects
an objects as enumerable items. The implicit iterator pragma enables optional
behaviour of allowing literals as enumerable items. Consider this view:

    var view = {
      foo: [1, 2, 3, 4, 5, "french"]
    };

The following template can iterate over the member `foo`:

    {{%IMPLICIT-ITERATOR}}
    {{#foo}}
      {{.}}
    {{/foo}}

If you don't like the dot in there, the pragma accepts an option to set your
own iteration marker:

    {{%IMPLICIT-ITERATOR iterator=bob}}
    {{#foo}}
      {{bob}}
    {{/foo}}

### TRANSLATION-HINT

See the "Internationalization" section above for info on this pragma.

### ?-CONDITIONAL

This allows one to make an explicitly conditional block, which will not iterate if it is
an array, but simply display the block.  The syntax is to suffix the name with a '?' so:

    {{%?-CONDITIONAL}}
    {{#foo?}}
      {{bob}}
    {{/foo?}}

Will print the block only if 'foo' evaluates to true, and if foo is an array, only print once
if foo is not empty.  This conditional test will also run faster than a normal block if
testing the truth value is all that's needed.

### DOT-SEPARATORS

For quick reference to a deep value in your context, use dots:

    {{%DOT-SEPARATORS}}
    {{foo.bar.1.hello}}

will render "baz" for the view `{foo:{bar:[0,{hello:"baz"}]}}`

### EMBEDDED-PARTIALS

To create partial templates within another template, you can use EMBEDDED-PARTIALS.

    {{%EMBEDDED-PARTIALS}}
    {{#>>piece}}
      {{x}}
    {{/>>piece}}
    {{#y}}
      {{>piece}}
    {{/y}}

Will render for `{x:1, y:{x:2}}`

      1
      2

### FILTERS

Inspired by [Django template tags/filters](http://docs.djangoproject.com/en/1.2/topics/templates/#filters), filters can process values through a function with extra arguments from the context.  There are three built-in filters so far: '==', '!=' to test equality, 'in' to test containment, and 'linebreaksbr' to replace lines with `<br />` elements.

    {{%FILTERS}}
    {{#foo?!=(bar)}}
      <p>{{foo?linebreaksbr()}}</p>
    {{/foo?==(bar)}}
       
Will render for `{foo:"xxx\nyyy",bar:"not_the_same_as_foo"}`

    <p>xxx<br />yyy</p>

The formating is to suffix the first variable name with a '?' and then the function name along with
parentheses.  There can be no white-space, but multiple arguments can be separated by parentheses.
The function must be added to `Mustache.Renderer.prototype.supported_filters` and is passed the
name, context, and the arguments as strings.  The function is responsible for calling `this.get_object(name, context, this.context)`
to convert any names into their contextual values.

### Making your own Pragmas

You can set to default and activate your own pragma by passing a function as the third argument to
Mustache.set_default_pragma().  This function is run with the Renderer as this.  If it returns
a function it will be run when a block or tag is being compiled and allow.  See `pragmas_implemented` in `mustache.js` for examples on how to use this.


## F.A.Q.

### Why doesn’t Mustache allow dot notation like `{{variable.member}}`?

The reason is given in the [mustache.rb
bugtracker](http://github.com/defunkt/mustache/issues/issue/6).

Mustache implementations strive to be template-compatible.


## More Examples and Documentation

See `examples/` for more goodies and read the [original mustache docs][m]

## Command Line

See `mustache(1)` man page or
<http://defunkt.github.com/mustache/mustache.1.html>
for command line docs.

Or just install it as a RubyGem:

    $ gem install mustache
    $ mustache -h

[m]: http://github.com/defunkt/mustache/#readme
[node.js]: http://nodejs.org
[couchdb]: http://couchdb.apache.org


## Plugins for jQuery, Dojo, Yui, CommonJS

This repository lets you build modules for [jQuery][], [Dojo][], [Yui][] and
[CommonJS][] / [Node.js][] with the help of `rake`:

Run `rake jquery` to get a jQuery compatible plugin file in the
`mustache-jquery/` directory.

Run `rake dojo` to get a Dojo compatible plugin file in the `mustache-dojo/`
directory.

Run `rake yui` to get a Yui compatible plugin file in the `mustache-yui/`
directory.

Run `rake commonjs` to get a CommonJS compatible plugin file in the
`mustache-commonjs/` directory which you can also use with [Node.js][].

## Testing

To run the mustache.js test suite, run `rake spec`.  All specs will be run first with JavaScriptCore (using `jsc`)
and again with Rhino, using `java org.mozilla.javascript.tools.shell.Main`.  To install Rhino on OSX, follow [these instructions](Rhino Install).

### Adding Tests

Tests are located in the `examples/` directory.  Adding a new test requires three files.  Here's an example to add a test named "foo":

`examples/foo.html` (the template):

    foo {{bar}}

`examples/foo.js` (the view context):

    var foo = {
      bar: "baz"
    };

`examples/foo.txt` (the expected output):

    foo baz

[jQuery]: http://jquery.com/
[Dojo]: http://www.dojotoolkit.org/
[Yui]: http://developer.yahoo.com/yui/
[CommonJS]: http://www.commonjs.org/
[Node.js]: http://nodejs.org/
[Rhino Install]: http://michaux.ca/articles/installing-rhino-on-os-x
