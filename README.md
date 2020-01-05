# JS-like-HTMLParser
Python 3 (tested only on 3.8) <br /> Fixing some bugs while creating others.
HTML Parser made by me, much simplier than the builtin version. It includes the DOM class which has a structure similar to the JavaScript element one.


Final version for now, might upgrade it later. <br />
(There are probably better options but I wanted to do it by myself) <br />
Part of a bigger project to be able to recreate page content on standalone programs.

Documentation: (Minimal since it's for personal use)
```
DOM
   .tag   //tag name
   .attrs //dictionary with the attributes of the tag
          #!# not tested with PHP, it might break
   .text  //text outside tags.  In case of a comment or the doctype; contains the string within the tags
   .type  //span - a start tag without a matching closing tag
          //div  - a start tag with a matching closing tag
          //comment
          //doctype
          //script  - currently only for php
   .appendChild(el, number = None)
          //inserts the (DOM)el at a specific position
   .setAttr(key, value)
          //sets an attribute       #!# not tested
   .__str__(text = False, type = False) 
          //returns the document's tree-like string
          //text - if true, returns the string with text
          //type - if true, returns the string with .type after the tag name
          
parser = HTMLParser2(document.html)               //initializes parser
document = HTMLParser2(document.html).document    //returns a DOM element (somewhat similar to js' document)
```

Possible future updates:
-Style/CSS analysis <br />
-JS analysis <br />
-PHP analysis (idk php that well) <br />
-HTML generator <br />

Made by Tomasz Kaspersky
