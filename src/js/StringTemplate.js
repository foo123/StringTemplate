/**
*   StringTemplate, 
*   a simple and flexible string template class for Node/XPCOM/JS, PHP, Python, ActionScript
* 
*   @version: 1.0.0
*   https://github.com/foo123/StringTemplate
**/
!function( root, name, factory ){
"use strict";
if ( ('undefined'!==typeof Components)&&('object'===typeof Components.classes)&&('object'===typeof Components.classesByID)&&Components.utils&&('function'===typeof Components.utils['import']) ) /* XPCOM */
    (root.$deps = root.$deps||{}) && (root.EXPORTED_SYMBOLS = [name]) && (root[name] = root.$deps[name] = factory.call(root));
else if ( ('object'===typeof module)&&module.exports ) /* CommonJS */
    (module.$deps = module.$deps||{}) && (module.exports = module.$deps[name] = factory.call(root));
else if ( ('undefined'!==typeof System)&&('function'===typeof System.register)&&('function'===typeof System['import']) ) /* ES6 module */
    System.register(name,[],function($__export){$__export(name, factory.call(root));});
else if ( ('function'===typeof define)&&define.amd&&('function'===typeof require)&&('function'===typeof require.specified)&&require.specified(name) /*&& !require.defined(name)*/ ) /* AMD */
    define(name,['module'],function(module){factory.moduleUri = module.uri; return factory.call(root);});
else if ( !(name in root) ) /* Browser/WebWorker/.. */
    (root[name] = factory.call(root)||1)&&('function'===typeof(define))&&define.amd&&define(function(){return root[name];} );
}(  /* current root */          this, 
    /* module name */           "StringTemplate",
    /* module factory */        function ModuleFactory__StringTemplate( undef ){
"use strict";

var PROTO = 'prototype';

function StringTemplate( tpl, replacements, compiled )
{
    var self = this;
    if ( !(self instanceof StringTemplate) ) return new StringTemplate(tpl, replacements, compiled);
    self.id = null;
    self.tpl = null;
    self._renderer = null;
    self._args = [tpl||'',replacements || StringTemplate.defaultArgs,compiled];
    self._parsed = false;
}
StringTemplate.defaultArgs = /\$(-?[0-9]+)/g;
StringTemplate.multisplit = function multisplit( tpl, reps, as_array ) {
    var r, sr, s, i, j, a, b, c, al, bl;
    as_array = !!as_array;
    a = [ [1, tpl] ];
    for ( r in reps )
    {
        if ( reps.hasOwnProperty( r ) )
        {
            c = [ ]; sr = as_array ? reps[ r ] : r; s = [0, reps[ r ]];
            for (i=0,al=a.length; i<al; i++)
            {
                if ( 1 === a[ i ][ 0 ] )
                {
                    b = a[ i ][ 1 ].split( sr ); bl = b.length;
                    c.push( [1, b[0]] );
                    if ( bl > 1 )
                    {
                        for (j=0; j<bl-1; j++)
                        {
                            c.push( s );
                            c.push( [1, b[j+1]] );
                        }
                    }
                }
                else
                {
                    c.push( a[ i ] );
                }
            }
            a = c;
        }
    }
    return a;
};
StringTemplate.multisplit_re = function multisplit_re( tpl, re ) {
    re = re.global ? re : new RegExp(re.source, re.ignoreCase?"gi":"g"); /* make sure global flag is added */
    var a = [ ], i = 0, m;
    while ( m = re.exec( tpl ) )
    {
        a.push([1, tpl.slice(i, re.lastIndex - m[0].length)]);
        a.push([0, m[1] ? m[1] : m[0]]);
        i = re.lastIndex;
    }
    a.push([1, tpl.slice(i)]);
    return a;
};
StringTemplate.arg = function( key, argslen ) { 
    var i, k, kn, kl, givenArgsLen, out = 'args';
    
    if ( arguments.length && null != key )
    {
        if ( key.substr ) 
            key = key.length ? key.split('.') : [];
        else 
            key = [key];
        kl = key.length;
        givenArgsLen = !!(argslen && argslen.substr);
        
        for (i=0; i<kl; i++)
        {
            k = key[ i ]; kn = +k;
            if ( !isNaN(kn) ) 
            {
                if ( kn < 0 ) k = givenArgsLen ? (argslen+(-kn)) : (out+'.length-'+(-kn));
                out += '[' + k + ']';
            }
            else
            {
                out += '["' + k + '"]';
            }
        }
    }
    return out; 
};
StringTemplate.compile = function( tpl, raw ) {
    var l = tpl.length, 
        i, notIsSub, s, out;
    
    if ( true === raw )
    {
        out = '"use strict"; return (';
        for (i=0; i<l; i++)
        {
            notIsSub = tpl[ i ][ 0 ]; s = tpl[ i ][ 1 ];
            out += notIsSub ? s : StringTemplate.arg(s);
        }
        out += ');';
    }
    else
    {
        out = '"use strict"; var argslen=args.length; return (';
        for (i=0; i<l; i++)
        {
            notIsSub = tpl[ i ][ 0 ]; s = tpl[ i ][ 1 ];
            if ( notIsSub ) out += "'" + s.replace(SQUOTE, "\\'").replace(NEWLINE, "' + \"\\n\" + '") + "'";
            else out += " + String(" + StringTemplate.arg(s,"argslen") + ") + ";
        }
        out += ');';
    }
    return new Function('args', out);
};
StringTemplate[PROTO] = {
    constructor: StringTemplate
    
    ,id: null
    ,tpl: null
    ,_parsed: false
    ,_args: null
    ,_renderer: null
    
    ,dispose: function( ) {
        var self = this;
        self.id = null;
        self.tpl = null;
        self._parsed = null;
        self._args = null;
        self._renderer = null;
        return self;
    }
    ,fixRenderer: function( ) {
        var self = this;
        self.render = 'function' === typeof self._renderer ? self._renderer : self.constructor[PROTO].render;
        return self;
    }
    ,parse: function( ) {
        var self = this;
        if ( false === self._parsed )
        {
            // lazy init
            self._parsed = true;
            var tpl = self._args[0], replacements = self._args[1], compiled = self._args[2];
            self._args = null;
            self.tpl = replacements instanceof RegExp 
                ? StringTemplate.multisplit_re(tpl, replacements) 
                : StringTemplate.multisplit( tpl, replacements );
            if ( true === compiled )
            {
                self._renderer = StringTemplate.compile( self.tpl );
                self.fixRenderer( );
            }
        }
        return self;
    }
    ,render: function( args ) {
        var self = this;
        args = args || [ ];
        if ( false === self._parsed )
        {
            // lazy init
            self.parse( );
            if ( self._renderer ) return self._renderer( args );
        }
        //if ( self._renderer ) return self._renderer( args );
        var tpl = self.tpl, l = tpl.length,
            argslen = args.length, i, t, s, out = ''
        ;
        for(i=0; i<l; i++)
        {
            t = tpl[ i ];
            if ( 1 === t[ 0 ] )
            {
                out += t[ 1 ];
            }
            else
            {
                s = t[ 1 ];
                if ( (+s === s) && (s < 0) ) s = argslen+s;
                out += args[ s ];
            }
        }
        return out;
    }
};

// export it
return StringTemplate;
});
