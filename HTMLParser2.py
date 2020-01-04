from re import match, compile, findall, search

attrKey = compile(r"(?<= )[\w]+(?==)")
attrValue = compile(r'(?<==")[A-Za-z_]+(?=")')

class DOM:
    def __init__(self, tag = None, attrs = None, text = None, type = None):
        self.text = text
        self.attrs = attrs
        self.tag = tag
        self.type = type
        self.children = []
        self.parent = None

    def appendChild(self, el = None, number = None):
        if not number:
            number = len(self.children)
        if el.tag in self.__dict__:
            if isinstance(self.__dict__[el.tag], list):
                self.__dict__[el.tag].insert(number, el.tag)
            else:
                self.__dict__[el.tag] = [self.__dict__[el.tag], el] # = the older member and the newer
        else:
            self.__dict__[el.tag] = el
        el.parent = self
        self.children.insert(number, el)

    def setAttr(self, key, value):
        self.attrs[key] = value


    def __str__(self, level=0, type = False, text = False):
        string = ""
        if self.tag == 'text' and self.text != '' and text:
            string = "|\t" * (level) + "text: \"" + self.text + "\"\n"
        elif self.tag != 'text':
            if type:
                string = "|\t" * (level) + self.tag + "." + self.type + "\n"
            else:
                string = "|\t" * (level) + self.tag + "\n"

        for child in self.children:
            string += child.__str__(level + 1, type, text)
        return string


class HTMLParser2:
    document = DOM(type = "document", tag = "document")

    def __init__(self, path):
        self.scope = self.document
        self.cursorEnd = 0
        self.cursor = 0
        self.html = open(path, 'r').read()
        self.parse()

    def parse(self):
        s = self.html.find("<", 0) + 1  #start
        e = 0                           #end //it's inverted for text
        while True:
            #Finding tags
            e = self.html.find(">", s)
            if s == 0:
                break

            #data between < > (inner HTML) - self.html[s:e]
            self.cursor = s
            self.anTag(self.html[s:e].strip())
            #string.strip() is used to remove white space character from the beginning and the end of a string

            #Finding text
            s = self.html.find("<", s) + 1
            if s == 0:
                break
            e += 1

            #data between > < (outerHTML) - self.html[e:s-1]
            #[e:s-1], otherwise it would include the tag <
            self.cursor = e
            self.anText(self.html[e:s-1].strip())
        #Parse loop ended

    def anTag(self, rawtag):       #Analyzing tags, return False if tag is unrecognized
        # <!--comment-->
        if rawtag[0:3] == "!--":
            self.scope.appendChild(DOM(tag = "comment", text = rawtag[3:-2], type = "comment"))
            pass

        # <!DOCTYPE>
        elif rawtag[0:8].lower() == "!doctype":
            self.scope.appendChild(DOM(tag = "doctype", text=rawtag, type = "doctype"))

        # <?PHP>
        elif rawtag[0] == "?":
            self.scope.appendChild(DOM(tag = "php", text = rawtag[4:-1], type="script"))
            #idk php lol that's all I'm doing right now
            #TODO

        # <span tag/>   //only according to XTML standards
        elif rawtag[-1] == "/":
            #print(self.getAttrs(rawtag))
            self.scope.appendChild(DOM(tag = search(r"[\w]*", rawtag).group(), attrs = self.getAttrs(rawtag)))

        # <start tag>
        elif match(r"[\w]", rawtag):
            temptag = DOM(tag = search(r"[\w]+", rawtag).group(), attrs = self.getAttrs(rawtag))
            EndTag = search(r"<[ ]*?/[ ]*?" + temptag.tag, self.html[self.cursor:])
            NewStart = search(r"<[ ]*?" + temptag.tag + r"[^>]*>", self.html[self.cursor:])

            # find if the tag ends else: it's an span tag
            if EndTag:
                #if the same tag start over again
                if NewStart and NewStart.start() < EndTag.start():
                    temptag.type = "span"
                    self.scope.appendChild(temptag)

                else:
                    #appends as child of current scope and becomes scope
                    temptag.type = "div"
                    self.cursorEnd = EndTag.start()
                    self.scope.appendChild(temptag)
                    self.scope = temptag

            else:   #it's an span tag
                temptag.type = "span"
                self.scope.appendChild(temptag)


        elif rawtag[0] == "/":                  #</endtag>
            temptag = search(r"[\w]+", rawtag[1:]).group()
            if temptag == self.scope.tag:
                self.scope = self.scope.parent
            else:
                print("Error! A different closing tag was expected:\n"
                      + self.scope.tag + "\n" + temtag.tag + " was expected!")

        else:
            print("Tag format not recognized. Tag:\n" + rawtag)
            return False
        return True

    def getAttrs(self, rawtag):
        #get attrs as a dictionary
        return dict(zip(findall(attrKey, rawtag), findall(attrValue, rawtag))) #attrKeyue is compiled before the DOM class

    def anText(self, text_):
        #Analyzing text
        counter = 0
        tag = ""
        self.scope.appendChild(DOM(tag = "text", text = text_.strip(), type = "text"))