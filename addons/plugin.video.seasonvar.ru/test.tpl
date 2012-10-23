page = require('webpage').create();
var code1 = page.evaluate(function () {
	    var r = $script$;
            return r; //document.getElementsByTagName('body')[0].innerHTML;
        });

var code = 'function SWF(swf_player,b,c,d,e,f,flashvar,g){document.write("<pl>"+flashvar.pl+"</pl><swf>"+swf_player+"</swf>");};'+code1.replace('new swfobject.embedSWF','SWF');

page1 = require('webpage').create();
page1.content = '<html><body><script type="text/javascript">' + code + '</script></body></html>';


var res = page1.evaluate(
	function () 
	{
	    return document.getElementsByTagName('pl')[0].innerHTML+','+document.getElementsByTagName('swf')[0].innerHTML;
        });

console.log(res);

phantom.exit();

