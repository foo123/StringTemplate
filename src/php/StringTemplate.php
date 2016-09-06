<?php
/**
*   StringTemplate, 
*   a simple and flexible string template class for Node/XPCOM/JS, PHP, Python, ActionScript
* 
*   @version: 1.0.0
*   https://github.com/foo123/StringTemplate
**/

if ( !class_exists('StringTemplate') )
{
class StringTemplate
{    
    public static function multisplit($tpl, $reps, $as_array=false)
    {
        $a = array( array(1, $tpl) );
        foreach ((array)$reps as $r=>$s)
        {
            $c = array( ); 
            $sr = $as_array ? $s : $r;
            $s = array(0, $s);
            foreach ($a as $ai)
            {
                if (1 === $ai[ 0 ])
                {
                    $b = explode($sr, $ai[ 1 ]);
                    $bl = count($b);
                    $c[] = array(1, $b[0]);
                    if ($bl > 1)
                    {
                        for ($j=0; $j<$bl-1; $j++)
                        {
                            $c[] = $s;
                            $c[] = array(1, $b[$j+1]);
                        }
                    }
                }        
                else
                {
                    $c[] = $ai;
                }
            }
            $a = $c;
        }
        return $a;
    }

    public static function multisplit_re( $tpl, $re ) 
    {
        $a = array(); 
        $i = 0; 
        while ( preg_match($re, $tpl, $m, PREG_OFFSET_CAPTURE, $i) ) 
        {
            $a[] = array(1, substr($tpl, $i, $m[0][1]-$i));
            $a[] = array(0, isset($m[1]) ? $m[1][0] : $m[0][0]);
            $i = $m[0][1] + strlen($m[0][0]);
        }
        $a[] = array(1, substr($tpl, $i));
        return $a;
    }
    
    public static function arg($key=null, $argslen=null)
    {
        $out = '$args';
        
        if ($key)
        {
            if (is_string($key))
                $key = !empty($key) ? explode('.', $key) : array();
            else 
                $key = array($key);
            $givenArgsLen = (bool)(null !=$argslen && is_string($argslen));
            
            foreach ($key as $k)
            {
                $kn = is_string($k) ? intval($k,10) : $k;
                if (!is_nan($kn))
                {
                    if ($kn < 0) $k = ($givenArgsLen ? $argslen : 'count('.$out.')') . ('-'.(-$kn));
                    
                    $out .= '[' . $k . ']';
                }
                else
                {
                    $out .= '["' . $k . '"]';
                }
            }
        }        
        return $out;
    }

    public static function compile($tpl, $raw=false)
    {
        static $NEWLINE = '/\\n\\r|\\r\\n|\\n|\\r/'; 
        static $SQUOTE = "/'/";
        
        if (true === $raw)
        {
            $out = 'return (';
            foreach ($tpl as $tpli)
            {
                $notIsSub = $tpli[ 0 ];
                $s = $tpli[ 1 ];
                $out .= $notIsSub ? $s : self::arg($s);
            }
            $out .= ');';
        }    
        else
        {
            $out = '$argslen=count($args); return (';
            foreach ($tpl as $tpli)
            {
                $notIsSub = $tpli[ 0 ];
                $s = $tpli[ 1 ];
                if ($notIsSub) $out .= "'" . preg_replace($NEWLINE, "' + \"\\n\" + '", preg_replace($SQUOTE, "\\'", $s)) . "'";
                else $out .= " . strval(" . self::arg($s,'$argslen') . ") . ";
            }
            $out .= ');';
        }
        return create_function('$args', $out);
    }

    
    public static $defaultArgs = '/\\$(-?[0-9]+)/';
    
    public $id = null;
    public $tpl = null;
    protected $_args = null;
    protected $_parsed = false;
    private $_renderer = null;
    
    public function __construct($tpl='', $replacements=null, $compiled=false)
    {
        $this->id = null;
        $this->_renderer = null;
        $this->tpl = null;
        $this->_args = array($tpl,!$replacements||empty($replacements)?self::$defaultArgs:$replacements,$compiled);
        $this->_parsed = false;
    }

    public function __destruct()
    {
        $this->dispose();
    }
    
    public function dispose()
    {
        $this->id = null;
        $this->tpl = null;
        $this->_args = null;
        $this->_parsed = null;
        $this->_renderer = null;
        return $this;
    }
    
    public function parse( )
    {
        if ( false === $this->_parsed )
        {
            // lazy init
            $tpl = $this->_args[0]; $replacements = $this->_args[1]; $compiled = $this->_args[2];
            $this->_args = null;
            $this->tpl = is_string($replacements)
                    ? self::multisplit_re( $tpl, $replacements)
                    : self::multisplit( $tpl, (array)$replacements);
            $this->_parsed = true;
            if (true === $compiled) $this->_renderer = self::compile( $this->tpl );
        }
        return $this;
    }
    
    public function render($args=null)
    {
        if (!$args) $args = array();
        
        if ( false === $this->_parsed )
        {
            // lazy init
            $this->parse( );
        }
        
        if ($this->_renderer) 
        {
            $f = $this->_renderer;
            return $f( $args );
        }
        
        $out = ''; $argslen = count($args);
        foreach($this->tpl as $t)
        {
            if ( 1 === $t[ 0 ] )
            {
                $out .= $t[ 1 ];
            }
            else
            {
                $s = $t[ 1 ];
                if ( is_int($s) && 0 > $s ) $s += $argslen;
                $out .= $args[ $s ];
            }
        }
        return $out;
    }
}    
}