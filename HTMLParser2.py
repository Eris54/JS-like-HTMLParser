from re import match, compile, findall, search
#########################################################
# FUCK HTMLPARSER IM GONNA DO BETTER WITHOUT AS MUCH RE #
#########################################################

#need to rename id because it will be used by my own DOM
#identificator = id

#
# starttag = re.compile(r"<(?:(?!/).)*?[^/]*>", re.I) #<tag>
# starttag = re.compile(r"<[^<]+?[^/]>", re.I) #<tag>
# starttag = re.compile(r"<[^<]+?[^/]>", re.I) #<tag>
# setag = re.compile(r".(?:(?!<).)*?/>", re.I) #<tag/> //start-end tag
# endtag = re.compile(r"</.+?[^/]>", re.I) #</tag>
# def printRe(m, msg):
#     print(msg)
#     if m:
#         for i in m:
#             print(i)
#     else:
#         print("Nothing found :/")
#
# printRe(re.findall(starttag, "<div lol /> <a> something <br/> <div ></div as>"), "\nstart:")
# printRe(re.findall(setag, "<div lol > <a> something <br /><br/> <hsi> </div as>"), "\nstart-end:")
# printRe(re.findall(endtag, "<div lol > <a> something <br/> </div as>"), "\nend:")
"""
DOM =
[
    head:[
        ""
        meta:[
            ""
            charset:"UTF-8"
            ""
        ]
        ""
        title:[
            ""
            "Table"
            ""
        ]
        ""
    ]
    body:[
        ""
        {table:[
            tbody:[]
        ]}
        ""
    ]
]
"""
attrKey = compile(r"(?<= )[\w]+(?==)")
attrValue = compile(r'(?<==")[A-Za-z_]+(?=")')

class DOM:
    def __init__(self, tag = None, attrs = None, text = None, type = None):
        self.text = text # it will own the tag inside the DOM in order to keep the order(?)
        self.attrs = attrs
        self.tag = tag
        self.type = type
        self.children = []

    def appendChild(self, name, number = None):
        if not number:
            number = len(self.children)
        if name in self.__dict__:
            if isinstance(self.__dict__[name], list):
                self.__dict__[name] = [self.__dict__[name], DOM()]
                element = self.__dict__[name][1]
            else:
                self.__dict__[name].insert(number, DOM())
                element = self.__dict__[name][number]
        else:
            self.__dict__[name] = DOM()
            element = self.__dict__[name]
        if not element.tag:
            element.tag = name
        element.parent = self
        if number:
            self.children.insert(number, element)
        else:
            self.children.append(element)

    def setAttr(self, key, value):
        self.attrs[key] = value

    # def __getitem__(self, item):
    #     return self.children[item]




class HTMLParser2:
    document = DOM(type = "document", tag = "document")

    def __init__(self, path):
        self.scope = self.document
        self.html = open(path, 'r').read()
        self.parse()

    def addTagEl(self, name):
        exec(name + " = DOM()")
        exec("self.availableTagElements.append()" + "")

    def parse(self):
        #string.strip() is used to remove white space character before and after the data
        s = self.html.find("<", 0) + 1  #start
        e = 0                           #end //it's inverted for text
        while True:
            #Finding tags
            e = self.html.find(">", s)
            if s == 0:
                break

            #data between < > (inner HTML) - self.html[s:e]
            self.anTag(self.html[s:e].strip(), s)

            #Finding text
            s = self.html.find("<", s) + 1
            if s == 0:
                break
            e += 1

            #data between > < (outerHTML) - self.html[e:s-1]
            #[e:s-1], otherwise it would include the tag <
            self.anData(self.html[e:s-1].strip(), e)

            #Ending

    def anTag(self, rawtag, cursor):       #Analyzing tags, return False if tag is unrecognized
        #print("'", tag, "'", sep="")
        #def __init__(self, tag = None, attrs = None, text = None, type = None):
        if rawtag[0:3] == "!--":                #<!--comment-->
            self.scope.appendChild(DOM(tag = "comment", text = rawtag[3:-2], type = "comment"))
            pass

        elif rawtag[0] == "!":                  #<!DOCTYPE>
            self.scope.appendChild(DOM(tag = "doctype", type = "doctype"))

        elif rawtag[0] == "?":                  #<?PHP>
            self.scope.appendChild(DOM(tag = "php", text = rawtag[4:-1], type="script"))
            #idk php lol that's all I'm doing right now
            #TODO

        elif rawtag[-1] == "/":                #<inline tag/> //only according to XTML standards
            #print(self.getAttrs(rawtag))
            self.scope.appendChild(DOM(tag = search(r"[\w]*", rawtag).group(), attrs = self.getAttrs(rawtag)))

        elif match(r"[\w]", rawtag):            #<start tag>
            ram = DOM(tag = search(r"[\w]+", rawtag).group(), attrs = self.getAttrs(rawtag))
            searchEndTag = search(r"<[ ]*?/[ ]*?" + ram.tag, self.html)

            # find if the tag ends (otherwise it's an inline tag
            if searchEndTag:
                #appends as child of current scope and becomes scope
                self.scope.appendChild(ram)
                self.scope = ram
            else:   #it's an inline tag
                ram.type = "inline"
                self.scope.appendChild(ram)
                pass

            #print(search(r"[\w]+", rawtag).group())
            #could do it in a more efficient way with this tag after the endtag, but this might be useful to scope
            pass

        elif rawtag[0] == "/":                  #</endtag>
            pass

        else:
            print("Tag not recognized. Tag:\n" + rawtag)
            return False
        return True

    def getAttrs(self, rawtag):     #get attrs as a dictionary
        return dict(zip(findall(attrKey, rawtag), findall(attrValue, rawtag))) #attrKeyue is compiled before the DOM class

    def anData(self, data, cursor):     #Analyzing data
        #print(data)
        pass


HTMLParser2("TestTable.html")
