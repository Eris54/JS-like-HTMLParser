from re import match, compile, findall, search, DOTALL, IGNORECASE

attrKey = compile(r"(?<= )[\w]+(?==)")
attrValue = compile(r'(?<==")[A-Za-z_]+(?=")')
tags = compile(r"(<\s*\?php)?(?(1)(.*\?>)|(<\s*[^<>]*>))", DOTALL | IGNORECASE)
div = "."         #name for a tag that has an endtag < > </ >
span = "/"       #name for a tag that doesnt have an endtag < > < />

"""
ffs I told myself I wouldn't make regex too complex
    (<\s*\?php)?    - checks if the tag is a php one
    (?(1)           - conditional, if it finds the pattern from the capture group 1:
    (.*\?>)         - it matches this one, else:
    (<\s*[^<>]*>)   - it matches a normal tag
"""

class DOM:
    def __init__(self, tag = None, attrs = None, text = None, type = ""):
        self.text = text
        self.attrs = attrs
        self.tag = tag
        self.type = type
        self.children = []
        self.parent = None
        self.warning = None

    def appendChild(self, el, pos = None):
        if not pos:
            pos = len(self.children)
        if el.tag in self.__dict__:
            if isinstance(self.__dict__[el.tag], list):
                self.__dict__[el.tag].insert(pos, el.tag)
            else:
                self.__dict__[el.tag] = [self.__dict__[el.tag], el] # = [the older member, the newer]
        else:
            self.__dict__[el.tag] = el
        el.parent = self
        self.children.insert(pos, el)

    def setAttr(self, key, value):
        self.attrs[key] = value

    def findByTag(self, tag, result = []):
        if self.tag == tag:
            result.append(self)
        else:
            for child in self.children:
                result = child.findByTag(tag, result)
        return result

    def findByAttr(self, key, value, result = []):
        try:
            if self.attrs[key] == value:
                result.append(self)
        except KeyError:
            pass

        for child in self.children:
            result = child.findByAttr(key, value, result)

        return result

    def findByClass(self, class_, result = []):
        try:
            if self.attrs["class"] == class_:
                result.append(self)
        except KeyError:
            pass

        for child in self.children:
            result = child.findByAttr(class_, result)
        return result

    def findById(self, id_, result = []):
        try:
            if self.attrs["id"] == id_:
                result.append(self)
        except KeyError:
            pass

        for child in self.children:
            result = child.findByAttr(id_, result)
        return result

    def __str__(self, level=0, type = True, text = False):
        string = ""
        if text:
            if self.tag == 'text' and self.text != '':
                string = "|\t" * (level) + "text: \"" + self.text + "\"\n"
            elif self.tag != 'text':
                if type:
                    if isinstance(self.text, str):
                        string = "|\t" * (level) + self.tag + " " + self.type + ":\n\"\"\"\n" + self.text + "\n\"\"\"\n"
                    else:
                        string = "|\t" * (level) + self.tag + " " + self.type + "\n"
                else:
                    if isinstance(self.text, str):
                        string = "|\t" * (level) + self.tag + ":\"\"\"\n" + self.text + "\"\"\"\n"
                    else:
                        string = "|\t" * (level) + self.tag + "\n"
        else:
            if self.tag != 'text':
                if type:
                    string = "|\t" * (level) + self.tag + " " + self.type + "\n"
                else:
                    string = "|\t" * (level) + self.tag + "\n"
            pass

        if self.warning:
            string += self.warning

        for child in self.children:
            string += child.__str__(level + 1, type, text)
        return string


class HTMLParser2:
    def __init__(self, decoding = 'UTF-8', HTTPResponse = None, path = None, debug = False):
        self.document = DOM(type = "document", tag = "document")
        self.scope = self.document
        self.cursorEnd = 0
        self.cursor = 0
        if HTTPResponse:
            self.html = HTTPResponse.read().decode(decoding)
        elif path:
            self.html = open(path, 'r').read()
        self.parse()
        if debug:
            runningDeb = True
            closing = 0
            while runningDeb:
                closing = self.html.find('<', closing + 3)
                if closing == -1:
                    break
                self.html = self.html[:closing] + "\n" + self.html[closing:]
            with open("HTMLParser2.debug", 'w', encoding = decoding) as f:
                f.write(self.document.__str__(type = True, text = True))
                f.write(self.html)
                f.close()

    def parse(self):
        self.cursor = 0
        match = search(tags, self.html)
        if not match:
            return False
        s = 0        #start text
        e = 0        #end //it's inverted for text
        while True:
            s = match.end() + self.cursor
            self.anTag(match.group()[1:-1])
            self.cursor += match.end()
            match = search(tags, self.html[self.cursor:])
            if not match:
                break
            e = match.start() + self.cursor

            self.anText(self.html[s:e].strip())
        #Parse loop ended

    def anTag(self, rawtag):       #Analyzing tags, return False if tag is unrecognized
        # <!--comment-->
        if rawtag[0:3] == "!--":
            self.scope.appendChild(DOM(tag = "comment", text = rawtag[3:-2], type = "comment"))
            pass

        # <!DOCTYPE>
        elif rawtag[0] == "!":
            self.scope.appendChild(DOM(tag = "doctype", text=rawtag, type = "doctype"))

        # <?PHP?>
        elif rawtag[0] == "?":
            self.scope.appendChild(DOM(tag = "php", text = rawtag[4:-1], type="script"))
            #idk php lol that's all I'm doing right now
            #TODO

        # <span tag/>   //only according to XTML standards
        elif rawtag[-1] == "/":
            self.scope.appendChild(DOM(tag = search(r"[\w]*", rawtag).group(), attrs = self.getAttrs(rawtag), type = span))

        # <start tag>
        elif match(r"[\w]+", rawtag):
            temptag = DOM(tag = search(r"[\w]+", rawtag).group().lower(), attrs = self.getAttrs(rawtag))
            EndTag = search(r"<\s*?/\s*?" + temptag.tag + r"[^<>]*>", self.html[self.cursor:], IGNORECASE)

            # find if the tag ends else: it's an span tag
            if EndTag:
                #appends as child of current scope and becomes scope
                temptag.type = div
                self.cursorEnd = EndTag.start()
                self.scope.appendChild(temptag)
                self.scope = temptag

            else:   #it's a 'span' tag
                temptag.type = span
                self.scope.appendChild(temptag)


        elif rawtag[0] == "/":                  #</endtag>
            temptag = search(r"[\w]+", rawtag[1:]).group()
            if temptag.lower() == self.scope.tag:
                self.scope = self.scope.parent
            else:
                self.scope.warning = "Error! A different closing tag was expected: \""\
                      + self.scope.tag + "\"\n\"" + temptag + "\" was found instead!\n"

        else:
            print("Tag format not recognized. Tag:\n" + rawtag)
            return False
        return True

    def getAttrs(self, rawtag):
        #get attrs as a dictionary
        return dict(zip(findall(attrKey, rawtag), findall(attrValue, rawtag))) #attrKeyue is compiled before the DOM class

    def anText(self, text_):
        #Analyzing text
        self.scope.appendChild(DOM(tag = "text", text = text_.strip(), type = "text"))
        #could just append a plain string, might be useful