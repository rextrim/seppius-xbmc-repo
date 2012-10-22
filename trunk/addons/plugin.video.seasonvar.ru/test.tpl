page = require('webpage').create();


page.onLoadFinished = function (status)
{
  if (status == 'success')
  {	
    var ua = page.evaluate(function () {
	    $script$;	

            return document.getElementsByTagName('html')[0].innerHTML;
        });
        console.log(ua);	
	
    	
    phantom.exit();
  }
  else
  {
    console.log('Connection failed.');
    phantom.exit();
  };
};

page.content = '<html><body><p>Hello world</p></body></html>';
