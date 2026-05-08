import sys
import os
import re

keywords=["if", "fi", "whl", "lhw","fn", "nf", "true", "false", "return", "elf", "els"]
operators=["+", "-", "=", "<", ">", "*", "/", "+=", "-=", "/=", "*=", "=="]
extras=[" ", "\n", "\0", "(", ")", "\"", "\'", "[", "]", "{", "}", ",", ";"]
nonIdent=extras+operators
class Token():
    def __init__(self, tokenType, content="", line=0) -> None:
        self.type=tokenType
        self.content=content
        self.line=line
        pass
    def __eq__(self, other):
        if isinstance(other, Token):
            if self.type=="any" or other.type=="any":
                return True
            if self.type != other.type:
                return False
            match self.type:
                case "ident" | "number" | "string":
                    return True
                case _:
                    return self.content==other.content
        return False
    
    def __str__(self) -> str:
        return f"<{self.type}, {self.content}>"
    
    def __repr__(self) -> str:
        return f"<{self.type}, {self.content}>"


class Tokenizer():
    def __init__(self, text: str) -> None:
        self.text=text
        self.text+="\0"
        self.tokens=[]
        self.currentToken=""
        self.index=-1
        self.line=1
        self.numberPattern=r"^[-+]?\d+(\.\d+)?$"
    def nextChar(self):
        return self.text[self.index+1]
    def addToken(self, tType: str):
        self.tokens.append(Token(tType, self.currentToken, self.line))
        self.currentToken=""
    def is_valid_integer(self):
        return bool(re.fullmatch(self.numberPattern, self.currentToken))
    def tokenizeString(self) -> int:
        self.index+=1
        while(self.text[self.index] not in ["\'", "\""]):
            if(self.text[self.index]=="\0"):
                self.addToken("unknown")
                return 1
            self.currentToken+=self.text[self.index]
            self.index+=1
        self.currentToken+=self.text[self.index]
        self.addToken("string")
        return 0
    def tokenize(self) -> list[Token]:
        while self.index<len(self.text)-1:
            self.index+=1
            self.currentToken+=self.text[self.index]
            match self.currentToken:
                case " " | "\0":
                    self.currentToken=""
                    continue
                case "\n":
                    self.currentToken=""
                    self.line+=1
                    continue
                case "(" | ")" | "{" | "}" | "[" | "]" | "," | ";":
                    self.addToken("symbol")
                    continue
                case "\"" | "\'":
                    res=self.tokenizeString()
                    if res==1:
                        return self.tokens
                    continue
                case _ if self.currentToken in operators:
                    if(self.nextChar() in operators):
                        continue
                    self.addToken("operator")
                    continue
                case _ if self.currentToken in keywords:
                    if(self.nextChar() in nonIdent):
                        self.addToken("keyword")
                    continue
                case _:
                    if(self.nextChar() in nonIdent):
                        tktype="ident"
                        if(self.is_valid_integer()):
                            tktype="number"
                        elif (any(ni in self.currentToken for ni in nonIdent) or self.currentToken[0].isnumeric()):
                            tktype="unknown"
                        self.addToken(tktype)
                    continue
        return self.tokens




if __name__ == "__main__":
    filePath=os.getcwd()+"/"+sys.argv[1]
    with open(filePath, 'r') as file:
        content=file.read()
        tokenizer=Tokenizer(content)
        for i in tokenizer.tokenize():
            print(i.type+":"+i.content)


