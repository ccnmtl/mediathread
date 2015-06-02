/*
  mustache.js — Logic-less templates in JavaScript

  See http://mustache.github.com/ for more info.

  interface:
    Mustache.to_html(template, context, partials, send_fun)
    Mustache.template(name, template, options)
    Mustache.tmpl(name, context)
    Mustache.set_pragma_default(name, pragma_default, pragma) 
    
 */

(function() {
  function Renderer(options,name) {
    this.name = name; //helps with partial recursion
    var p_source = this.default_pragmas;
    if (options) {
      if (options.pragmas) p_source = options.pragmas;
      if (options.sub) this.sub = true;
    }
    this.pragmas = {};
    for (p in p_source) {
      this.pragmas[p] = p_source[p];
      this.pragma_initialize(p);
    }
  }
  function PublicMustache(){}
  /* 
    Public Interface
  */
  PublicMustache.prototype = {
    name: "mustache.js",
    version: "0.4-dev",
    Renderer:Renderer,
    to_html:function(template, context, partials, send_fun) {
      var compiled = new this.Renderer().compile(template, partials);
      if (typeof send_fun==='function') ///hack for now until we implement buffer?
        send_fun(compiled.render(context));
      else
        return compiled.render(context);
    },
    compile:function(template,partials) {
      var compiled = new this.Renderer().compile(template, partials);
      return function(context) {
        return compiled.render.call(compiled,context);
      }
    },
    template:function(name,template,options) {
      var tmpl = this.Renderer.prototype.partials[name] = new this.Renderer(options,name);
      return tmpl.compile(template,false); //separate step for recursive partials
    },
    tmpl:function(name,context) {
      if (name in this.Renderer.prototype.partials) {
        return this.Renderer.prototype.partials[name].render(context);
      } else {
        throw Error('No template or partial with name:'+name);
      }
    },
    ///Run this before creating templates depending on them
    set_pragma_default:function(name, pragma_default, pragma) {
      if (pragma_default) {
        this.Renderer.prototype.default_pragmas[name] = (typeof pragma_default=='object'?pragma_default:{});
      } else {
        delete this.Renderer.prototype.default_pragmas[name];
      }
      if (pragma)
        this.Renderer.prototype.pragmas_implemented[name] = pragma;
    }
  }

  if (this.Mustache) 
    this.SkyMustache = new PublicMustache();
  else
    this.Mustache = new PublicMustache();
  
  /* 
     Checks whether a value is thruthy or false or 0
     Optimization: taking this out of find() speeds it up
  */
  function is_kinda_truthy(bool) {
    return (bool || bool === false || bool === 0);
  }

  Renderer.prototype = {
    otag: "{{",
    ctag: "}}",

    //stateful objects--can we separate these out somehow?
    state: {},
    context: {},
    recurse: 0,
    partials: {}, //set only on the prototype--so this is a Singleton
    default_pragmas: {
      'IMPLICIT-ITERATOR':{iterator:'.'},
      'i18n':{}
    },
    pragmas_implemented: {
      ///return overrides run during template parsing in this.piece()
      'IMPLICIT-ITERATOR':function() {
        if (!this.pragmas['IMPLICIT-ITERATOR'].iterator) {
          this.pragmas['IMPLICIT-ITERATOR'].iterator = '.';
        }
        return function(method,name,pragma_opts) {
          if (name !== pragma_opts.iterator) return false;
          switch(method) {
            case "^":case "#":
              return false
            case "{": //unescaped content
              return this.pieces.dot_unescaped;
            default:
              return this.pieces.dot_escaped;
          }
        }
      },
      '?-CONDITIONAL':function() {
        return function(method,name,pragma_opts,obj) {
          if (method === '#' && /\?$/.test(name)) {
            obj.name = name.substr(0,name.length-1);
            obj.orig_name = name;
            return this.pieces.conditional;
          }
        }
      },
      'DOT-SEPARATORS':function() {
        this.get_object = function(name,context) {
          var parts = name.split("."), obj = context;
          for(var i = 0, p; obj && (p = parts[i]); i++){
            obj = (p in obj ? obj[p] : undefined);
          }
          return obj;
        }
      },
      'i18n':function() {
        this.section_prefixes.push('_');
        return function(method,name,pragma_opts,obj) {
          if (method === '_') {
            if (name === 'i' && typeof _==='function') {
              obj.i18n = _(obj.uncompiled, this.pragmas['TRANSLATION-HINT'] || undefined);
              obj.compiled = new Renderer({pragmas:this.pragmas,sub:true},
                                          this.name).compile(obj.i18n,null,{'otag':obj.otag,'ctag':obj.ctag})
              return this.pieces.just_render;
            } else {
              throw Error("When i18n is turned on, no variables starting with '_' are allowed.");
            }
          }
        }
      },
      'TRANSLATION-HINT':function() {
        /*don't need to do anything, as this just holds info for i18n pragma  */
      },
      'EMBEDDED-PARTIALS':function() {
        Renderer.prototype.update_partial = function(context, opts) {
          if (this.inner_index) {
            opts = opts || {};
            var parent = opts.parent || document;
            var doms_to_update = [];
            if (this.partial_id) {
              doms_to_update.push((parent.ownerDocument || document).getElementById(this.partial_id.render(context)));
            } else if (this.partial_class) {
              var classname = this.partial_class.render(context);
              if (parent.getElementsByClassName) {
                doms_to_update = Array.prototype.slice.call(parent.getElementsByClassName(classname));
              } else if (jQuery) {
                doms_to_update = jQuery('.'+classname, parent).toArray();
              }
            }
            if (doms_to_update) {
              var pre = opts.pre || function(){};
              var post = opts.post || function(){};
              for (var i=0; i<doms_to_update.length; i++) {
                pre(doms_to_update[i],context);
                doms_to_update[i].innerHTML = this.compiled[this.inner_index].compiled.render(context);
                post(doms_to_update[i],context);
              }
            }
          }
        };
        Renderer.prototype.render_partial = function(context, opts) {
            if (this.inner_index) {
                return this.compiled[this.inner_index].compiled.render(context);
            }
        };        
        Renderer.prototype.css_selector = function() {
          if (this.partial_unique_id)
            return '#'+this.partial_unique_id;
          if (this.partial_unique_class)
            return '.'+this.partial_unique_id;
        }
        PublicMustache.prototype.update = function(template_name, context, opts) {
          var template = Renderer.prototype.partials[template_name];
          if (template && template.update_partial)
            return template.update_partial(context, opts);
        };
        PublicMustache.prototype.render_partial = function(template_name, context, opts) {
            var template = Renderer.prototype.partials[template_name];
            if (template && template.update_partial) {
                return template.render_partial(context, opts);
            }
        };                
        PublicMustache.prototype.css_selector = function(template_name) {
          var template = Renderer.prototype.partials[template_name];
          if (template)
            return template.css_selector();
        }
        return function(method,name,pragma_opts,obj) {
          if (method === '#' && /^>>/.test(name) ) {
            var template_name = name.substring(2);
            var oneelement_regex = new RegExp('^(\\s*<[^>]+?(id=[\\\'\\"]([^\\\'\\"]+)[\\\'\\"]|class=[\\\'\\"]([^\\\'\\"]+)[\\\'\\"])[^>]*>)([\\s\\S]+)(<\\/\\w+>\\s*)$','mg');
            var html_match = oneelement_regex.exec(obj.uncompiled);
            if (html_match) {
              ///split up the innerHTML content so it can be rendered separately
              obj.compiled = this.section_compile(html_match[1], obj.otag, obj.ctag);
              obj.compiled.inner_index = obj.compiled.compiled.length;
              if (html_match[3]) {
                obj.compiled.partial_id = this.section_compile(
                  html_match[3], obj.otag, obj.ctag
                );
                //if @id isn't variable, then we'll use that to find all this object, otherwise the first @class
                if (obj.compiled.partial_id.compiled.length == 1 && typeof obj.compiled.partial_id.compiled[0] == 'string') {
                  obj.compiled.partial_unique_id = html_match[3];
                } else {
                  var class_match = /class=[\'\"]([^\'\"]+)[\'\"]/mg.exec(html_match[1]);
                  if (class_match) {
                    var classes = class_match[1].split(' ');
                    if (!(new RegExp(obj.otag).test(classes[0]))) {
                      obj.compiled.partial_unique_class = classes[0];
                    }
                  }
                }
              } else {//first class used
                var classes = html_match[4].split(' ');
                obj.compiled.partial_class = this.section_compile(
                  classes[0], obj.otag, obj.ctag
                );
                //use second class to find all objects of this type
                if (classes.length > 1 && !(new RegExp(obj.otag).test(classes[1]))) {
                  obj.compiled.partial_unique_class = classes[1];
                }
              }
              //add the rest of the template after the opening tag
              obj.compiled.compiled.push({
                'content':this.pieces.just_render,
                'uncompiled':html_match[5],
                'compiled':this.section_compile(html_match[5], obj.otag, obj.ctag)
              })
              obj.compiled.compiled.push(html_match[6]);
            } else {
              obj.compiled = this.section_compile(obj.uncompiled, obj.otag, obj.ctag);
            }
            Renderer.prototype.partials[template_name] = obj.compiled
            return this.pieces.just_render;
          }
        }
      },
      'FILTERS':function() {
        this.filter_regex = /\?([\w\=\!]+)\(([\w-.,]*)\)$/;
        this.original_find = this.find;
        this.find = function(ctx, context) {
          if (typeof ctx.filter_function === 'function') {
            return ctx.filter_function.call(this, ctx.name, context, ctx.filter_arguments)
          } else {
            return this.original_find(ctx,context)
          }
        };
        return function(method,name,pragma_opts,obj) {
          var filter_match = name.match(this.filter_regex);
          if (filter_match) {
            obj.name = name.slice(0, this.filter_regex.lastIndex - filter_match[0].length);
            obj.filter_function = Renderer.prototype.filters_supported[ filter_match[1] ];
            obj.filter_arguments = filter_match[2].split(',');
            if (typeof obj.filter_function !== 'function') {
              throw Error("Filter '"+filter_match[1]+"' not supported.");
            }
          }
        }
      }
    },
    filters_supported: {
      '==':function(name,context,args) {
        return (this.get_object(name,context,this.context)
                == this.get_object(args[0],context,this.context))
      },
      '!=':function(name,context,args) {
        return (this.get_object(name,context,this.context)
                == this.get_object(args[0],context,this.context))
      },
      'in':function(name,context,args) {
        return (this.get_object(name,context,this.context)
                in this.get_object(args[0],context,this.context))
      },
      'linebreaksbr':function(name,context,args) {
        return String(this.get_object(name,context,this.context)||'').replace(/\n/g,'<br />');
      }
    },
    pragma_initialize: function(name) {
      if (typeof this.pragmas_implemented[name] === 'function') {
        this.pragmas[name]['=override'] = this.pragmas_implemented[name].call(this);
      } else {
	throw Error("This implementation of mustache doesn't understand the '"+name+"' pragma");
      }
    },
    pragma_parse: function(pragma_declaration) {
      var pragma = {};
      var name_opts = pragma_declaration.split(/\s+/);
      if (name_opts.length > 1) {
        var opts = name_opts[1].split('=');
        if (opts.length > 1) {
          pragma[opts[0]] = opts[1];
        }
      }
      this.pragmas[name_opts[0]] = pragma;
      this.pragma_initialize(name_opts[0]);
    },

    render: function(state, top_context) {
      state = state || {};
      this.state = {ctx:[],contexts:[state]};
      this.context = top_context || state;
      return this.map(this.compiled, this.render_func, this).join('');
    },

    render_func: function(o) {
      return (typeof o === 'string' ? o : o.content.call(this,o,this.state));
    },

    compile: function(template, partials, opts) {
      template = template || '';
      var compiled = [];
      //1. TODO find pragmas and replace them
      var otag = (opts && opts.otag ? opts.otag : this.otag);
      var ctag = (opts && opts.ctag ? opts.ctag : this.ctag);
      if (partials) {
        for (a in partials) {
          var p = Renderer.prototype.partials[a] = new Renderer(false,a);
          p.compile(partials[a],false); //separate step for recursive partials
        }
      }
      
      //2. split on new delimiters
      var sections = this.map(
        this.split_delimiters(template, otag, ctag),
        function(s_delim) {
          return this.split_sections(s_delim.template, s_delim.otag, s_delim.ctag);
        },
        this);
      
      for (var i=0;i<sections.length;i++) {
        for (var j=0;j<sections[i].length;j++) {
          var s = sections[i][j];
          if (s.name === undefined) {
            //3. for each delimiter break up tags/blocks
            this.split_tags(s.template, s.otag, s.ctag, compiled);
          } else {
            compiled.push(s)
          }
        }
      }
      /*
      var last = compiled.length -1;
      if (typeof compiled[last] === 'string') {
        compiled[last] = compiled[last].replace(/\n+$/,'');
      }*/
      this.template = template;
      this.compiled = compiled;
      return this;
    },

    to_html: function(template, context, partials) {
      ///alters state!  should it!?
      var compiled = this.compile(template, partials);
      return compiled.render(context);
    },

    /* breaks up the template by delimiters
       this helps avoid some other random bugs, but
       an edge-case consequence is that you cannot change delimiters inside blocks
     */
    split_delimiters: function(template, otag, ctag) {
      var regex = new RegExp(otag+'=([^=\\s]+)\\s+([^=\\s]+)='+ctag,'g');
      var pragma_regex = new RegExp(otag + "%\\s*([^\\/#\\^]+?)\\s*%?" + ctag, "g");
      var found = regex.exec(template);
      var rv_list = [];

      var that = this;
      function remove_pragmas(tmpl) {
        return tmpl.replace(pragma_regex,function(full_match, pragma_declaration) {
          that.pragma_parse.call(that,pragma_declaration);
          return '';
        });
      }

      if (found) {
        rv_list.push({
          'template': remove_pragmas(template.slice(0,regex.lastIndex-found[0].length)),
          'otag':otag,'ctag':ctag
        });
        Array.prototype.push.apply(rv_list, this.split_delimiters(
          template.slice(regex.lastIndex),
          this.escape_regex(found[1]),this.escape_regex(found[2])
        ))
      } else {
        rv_list.push({'template':remove_pragmas(template),'otag':otag,'ctag':ctag});
      }
      return rv_list;
    },


    /*
      Divides inverted (^) and normal (#) sections
    */
    section_prefixes: ["^","#"],
    split_sections: function(template, otag, ctag) {
      // CSW - Added "+?" so it finds the tighest bound, not the widest
      var regex = new RegExp(otag + "("+this.map(this.section_prefixes,this.escape_regex).join("|")+")\\s*(.*[^\\s])\\s*" + ctag +
                             "([\\s\\S]*?)" + otag + "\\/\\s*\\2\\s*" + ctag, "mg");
      var found, prevInd=0, rv_list = [];

      while (found = regex.exec(template)) {
        rv_list.push({
          'template':template.slice(prevInd,regex.lastIndex-found[0].length),
          'otag':otag,'ctag':ctag
        })
        var temp = found[3];

        var sub_section = {
          'block':found[1],       //'#'=test/list '^'=inverted
          'name':found[2],        //block name value
          'uncompiled': temp, //inner block content
          'otag':otag,'ctag':ctag
        }
        sub_section['content'] = this.piece(found[1], found[2], sub_section);
        //maybe a pragma from this.piece() did it for us
        if (!sub_section.compiled) { 
          sub_section['compiled'] = this.section_compile(temp, otag, ctag);
        }

        rv_list.push(sub_section);

        prevInd = regex.lastIndex;
      }
      rv_list.push({
        'template':template.slice(prevInd),
        'otag':otag,'ctag':ctag
      });
      return rv_list;
    },
    section_compile: function(uncompiled, otag, ctag) {
      return new Renderer({pragmas:this.pragmas,sub:true},this.name).compile(uncompiled,null,{'otag':otag,'ctag':ctag});
    },
    /* 
       Split regular strings with {{foo}} and friends into array of joinable parts
     */
    split_tags: function(template, otag, ctag, rv_list) {
      var regex = new RegExp(otag + "(=|!|>|&|\\{|%)?\\s*([^\\/#\\^]+?)\\s*(\\1|\\})?" + ctag, "g");
      var found, prevInd=0;
      while (found = regex.exec(template)) {
        var front = regex.lastIndex-found[0].length;
        if (front != prevInd) //don't push empty strings
          rv_list.push(/*string content:*/
            template.slice(prevInd,regex.lastIndex-found[0].length)
          );
        var sub_section = {'name':found[2]};
        switch(found[1]) {//operator
        case "!": 
          break; // ignore comments
        case "%": 
          //shouldn't get here, because this is done in the split_delimiters phase
          //so pragmas will be enabled in time for different section blocks to be passed 
          //to compiled sub-sections
          this.pragma_parse(found[2]);
          break;
        case "{": // the triple mustache is unescaped
          sub_section['content'] = this.piece('{',found[2],sub_section);
          rv_list.push(sub_section);
          break;
        case "=": // broken delimiter setting
          throw Error("Incorrectly formed delimiter changing tag: "+found[0]);
          break;
        case ">": // partials
          if (found[2] in this.partials) {
	    sub_section['compiled'] = this.partials[found[2]];
            //rv_list.push.apply(rv_list, this.partials[found[2]].compiled);
          } else if (found[2] === this.name) {///recursion
            throw Error("Unset partial reference '"+found[2]+"' not found in template:"+ this.name);
            //sub_section['compiled'] = this; //issue: might be child of partial like in a block
          } else {
            throw Error("Unknown partial '"+found[2]+"'"
                        + ((this.name) ? ' not found in template: '+this.name : ''));
          }
          //sub_section['compiled'].compiled.push('\n');
          //break;
        default: // regular escaped value
          sub_section['content'] = this.piece(found[1],found[2],sub_section);
          rv_list.push(sub_section);
          break;
        }
        prevInd = regex.lastIndex;
      }
      if (prevInd != template.length) //TODO: should this be length-1?
        rv_list.push(/*string content:*/template.slice(prevInd));
      return rv_list;
    },
    pieces: {
      inverse_block:function(ctx, state) {
        var value = this.find(ctx, state.contexts[0]);
        if (!value || this.is_array(value) && value.length === 0) {
          return ctx.compiled.render(state.contexts[0], this.context);
        } else
          return ""
      },
      conditional:function(ctx, state) {
        var value = this.find(ctx, state.contexts[0]);
        if (value && value.length !== 0) {
          return ctx.compiled.render(state.contexts[0], this.context);
        }
      },
      partial:function(ctx, state) {
	var c = state.contexts[0];
        ++this.recurse;
        if (this.recurse > 100 && this === ctx.compiled) {
          var keys = '';
          for (a in c) { keys += " ,"+a; }
          throw Error("TOO MUCH RECURSION:" + keys);
        }
	return ctx.compiled.render((typeof c[ctx.name]==='object' ? c[ctx.name] : c), this.context);
      },
      block:function(ctx, state) {
        var value = this.find(ctx, state.contexts[0]);
        if (value) {
          if(Object.prototype.toString.call(value)==='[object Array]'){// Enumerable, Let's loop!
            state.ctx.unshift(ctx);
            state.contexts.unshift(0);
            var rv = this.map(value, function render_array_item(row) {
              this.state.contexts[0] = row;
              return this.map(this.state.ctx[0].compiled.compiled,
                              this.render_func,this).join('');
            },this).join("");
            state.contexts.shift();
            state.ctx.shift();
            return rv;
          } 
	  switch (typeof value) {
	  case 'function':
            return value.call(state.contexts[0], ctx.uncompiled, function render(text) {
              ///this function is forced to use (SLOW) closures even for default rendering text
              if (text === ctx.uncompiled) {
                return ctx.compiled.render(state.contexts[0], state.contexts[state.contexts.length-1]);
              } else {
                return new Renderer({sub:true},this.name).compile(text).render(state.contexts[0], 
                                                           state.contexts[state.contexts.length-1]);
              }
            });
	  case 'object':
            //state.ctx = ctx;
            var rv = ctx.compiled.render(value, this.context);
            return rv;
	  default:
            return ctx.compiled.render(state.contexts[0], this.context);	    
          }
        } 
        return "";
      },
      escaped:function(ctx, state) {
        return this.escape(this.find(ctx, state.contexts[0]));
      },
      unescaped:function(ctx, state) {
        return this.find(ctx, state.contexts[0]);
      },
      dot_escaped:function(ctx,state) {
        return this.escape(this.display(state.contexts[0],state.contexts[0]));
      },
      dot_unescaped:function(ctx,state) {
        return this.display(state.contexts[0],state.contexts[0]);
      },
      just_render:function(ctx,state) {
        return ctx.compiled.render(state.contexts[0], this.context);
      }
    },
    piece: function(method, name, obj) {
      for (a in this.pragmas) {
        var p = this.pragmas[a];
        if (p['=override']) {
          var handler = p['=override'].call(this,method,name,p,obj);
          if (handler) return handler;
        }
      }
      switch(method) {
      case "^"://invert
        return this.pieces.inverse_block;
      case "#"://block
        return this.pieces.block;
      case ">"://partial
        return this.pieces.partial;
      case "&"://function extension
        return this.pieces.unescaped; //could optimize better?
      case "{": //unescaped content
        return this.pieces.unescaped;
      case "_": //TODO: if i18n is ON, but the block is not _i but _foo, what do we do?
        return this.pieces.just_render;        
      default:
        return this.pieces.escaped;
      }
    },
    escape_regex: function(text) {
      var specials = [
        '/', '.', '*', '+', '?', '|',
        '(', ')', '[', ']', '{', '}', '\\','^'
      ];
      var regex = new RegExp(
        '(\\' + specials.join('|\\') + ')', 'g'
      );
      return text.replace(regex,'\\$1');
    },
    
    get_object: function(name,ctx,ctx2) {
      if (ctx && is_kinda_truthy(ctx[name]))
        return ctx[name];
      else if (is_kinda_truthy(ctx2[name]))
        return ctx2[name];
    },
    display: function(value,context) {
      if(typeof value === "function") {
        return value.apply(context);
      }
      if(value !== undefined) {
        return value;
      }
      // silently ignore unkown variables
      return "";
    },
    find: function(ctx, context) {
      var value = this.get_object(ctx.name,context,this.context);
      return this.display(value,context);
    },

    /*
      Does away with nasty characters
    */
    ///Which regex do we want?  double-escape or not?
    escape_reg: new RegExp("&|[\\\"\\'<>\\\\]","g"),
    //escape_reg: new RegExp("&(?!\\w+;)|[\\\"\\'<>\\\\]","g"),
    escape: function(s) {
      s = String(s === null ? "" : s);
      ///This would be faster: Why do we need to escape '\' and '>' ?
      //return s.replace('&',"&amp;").replace("<","&lt;").replace("'",'&#39;').replace('"','&quot;');
      return s.replace(this.escape_reg, function(s) {
        switch(s) {
        case "&": return "&amp;";
        case "\\": return "\\\\";
        case '"': return '&quot;';
        case "'": return '&#39;';
        case "<": return "&lt;";
        case ">": return "&gt;";
        default: return s;
        }
      });
    },

    is_array: function(a) {
      return Object.prototype.toString.call(a) === '[object Array]';
    },

    /*
      Why, why, why? Because IE. Cry, cry cry.
      Strangely, Chrome goes faster with the custom function
    */
    map: Array.map || function(ary, fn, thisObj) {
      var len = ary.length >>> 0,
        rv = new Array(len);
      ///must go forward for recursive partials to process correctly
      for (var i=0;i<len;i++) {
        rv[i] = fn.call(thisObj, ary[i]);
      }
      return rv;
    }

  }/*Renderer.prototype*/

  
})()