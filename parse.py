from lex import *

from enum import Enum
class StmtCmpStatus(Enum):
    NOT = 1
    SUB = 2
    SAME = 3


cfg_map={
    "meta":[
            ["fundecl"],
        ],
    "stmthead": [
        [],
        ["if_stmt"],
        ["expr"], ["init_stmt"], ["while_loop"],
        [Token("keyword", "return"), "expr"] 
    ],
    "stmt":[
        # STMT SEPARATOR NECESSARY
            ["stmthead", Token("symbol", ";")]
        ],
    "block":[
        [],
        ["stmt", "block"]
        ],
    "term":[
            ["factor", "termtail"],
        ],
    "termtail":[
        [],
            [Token("operator", "*"), "factor", "termtail"],
            [Token("operator", "/"), "factor", "termtail"],
        ],
    "factor": [
        [Token("ident"), "append"],
        ["numeric"],
        [Token("string")],
        ["bool"],
        [Token("symbol", "("), "expr", Token("symbol", ")")],
        [Token("symbol", "["), "args", Token("symbol", "]")],
    ],
    "numeric":[
            [Token("number")],
            [Token("operator", "-"), Token("number")]
        ],
    "bool":[
            [Token("keyword", "true")],
            [Token("keyword", "false")],
        ],
    "append": [
        [],
        [Token("symbol", "["), "expr", Token("symbol", "]"), "append"],
        [Token("symbol", "("), "args", Token("symbol", ")"), "append"],
    ],
    "exprtail":[
        [],
            [Token("operator", "+"), "term", "exprtail"],
            [Token("operator", "-"), "term", "exprtail"],
            [Token("operator", "=="), "term", "exprtail"],
            [Token("operator", "<="), "term", "exprtail"],
            [Token("operator", ">="), "term", "exprtail"],

        ],
    "expr":[
           ["term", "exprtail"], 
        ],
    "args": [
        [],
        ["expr", "argstail"]
    ],
    "argstail":[
        [],
        [Token("symbol", ","), "expr", "argstail"]
    ],
    "params": [
        [],
        [Token("ident"), "paramstail"]
    ],
    "paramstail":[
        [],
        [Token("symbol", ","), Token("ident"), "paramstail"]
    ],
    "init_stmt": [
        [Token("ident"), Token("operator", "="), "expr"]
    ],
    "fundecl": [
            [Token("keyword", "fn"), Token("ident"), Token("symbol", "("), "params", Token("symbol", ")"), "block", Token("keyword", "nf")]
        ],
    "if_stmt": [
        [Token("keyword", "if"), "expr", "block", "else", Token("keyword", "fi")]
    ],
    "while_loop": [
        [Token("keyword", "whl"), "expr", "block", Token("keyword", "lhw")]
        ],
    "else":[
        [],
        [Token("keyword", "els"), "block"]
    ],
}

class Parser():
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens=tokens
        self.tokens.append(Token("end", "end"))
        #self.unpackCfg()
        self.errorCount=0
        self.errorMax=2000
        self.current_stmt=[]
        self.errors=[]
       # self.parsedProgram=[]
        self.programIndex=0
        self.baseProgram=[]
        self.expected=[]
        self.index=-1
        self.setCfgArray()
    
    def setCfgArray(self):
        self.cfgArray=cfg_map["stmt"].copy()+cfg_map["meta"].copy()
        #for k in cfg_map.keys():
        #    for stmt in cfg_map[k]:
        #        self.cfgArray.append(stmt)
    def nextToken(self):
        return self.tokens[self.index+1]

    def currentWithNextToken(self):
        temp=self.current_stmt.copy()
        temp.append(self.nextToken())
        return temp

    def inflateOnce(self, arr, idx):
        res=[]
        for g in cfg_map[arr[idx]]:
            temp=arr.copy()
            temp.pop(idx)
            if isinstance(g, str):
                temp.insert(idx, g)
            else:
                for i in g[::-1]:
                    temp.insert(idx, i)
            res.append(temp)
        return res


    def is_sublist(self, main_list, sub_list):
        idx=0
        if main_list==sub_list:
            return StmtCmpStatus.SAME
        if len(sub_list)>=len(main_list) and all([not isinstance(item, str) for item in main_list]):
            return StmtCmpStatus.NOT
        for i in sub_list:
            if isinstance(main_list[idx], str):
                inflatedGrammer=[ig for ig in self.inflateOnce(main_list, idx) if isinstance(ig[idx], str) or ig[idx]==i]
                max_match=StmtCmpStatus.NOT
                for ig in inflatedGrammer:
                    recursive=self.is_sublist(ig, sub_list)
                    match recursive:
                        case StmtCmpStatus.NOT:
                            continue
                        case StmtCmpStatus.SAME:
                            return StmtCmpStatus.SAME
                        case StmtCmpStatus.SUB:
                            max_match=recursive
                return max_match
            elif main_list[idx]!=i:
                return StmtCmpStatus.NOT
            idx+=1
        return StmtCmpStatus.SUB

    def is_matching(self, main_list, sub_list):
        if main_list==sub_list:
            return True
        if len(sub_list)>=len(main_list) and not any([isinstance(item, str) for item in main_list]):
            return False
        idx=0
        for i in sub_list:
            if isinstance(main_list[idx], str):
                inflatedGrammer=[ig for ig in self.inflateOnce(main_list, idx) if isinstance(ig[idx], str) or ig[idx]==i]
                for ig in inflatedGrammer:
                    if self.is_matching(ig, sub_list):
                        return True
                return False
            elif main_list[idx]!=i:
                return False
            idx+=1
        return True


    def filter_non_matching(self):
        self.cfgArray=[stmt for stmt in self.cfgArray if self.is_matching(stmt, self.current_stmt)]
    def filter_non_part(self):
        self.cfgArray=[stmt for stmt in self.cfgArray if self.is_partOf(stmt, self.current_stmt)]
    

    def printError(self, error):
        errorLine=error[0][-1].line
        if errorLine==0:
            errorLine="EOF"
        error_msg=f"Error on line: {errorLine}. {error[1]}"
        print(error_msg)
        self.errors.append(error_msg)
        self.errorCount+=1
        if self.errorCount>=self.errorMax:
            exit(1)

    def is_partOf(self, main_list, sub_list):
        for idx, val in enumerate(sub_list):
            if val!=main_list[idx]:
                return False
        return True

    def inflateFirst(self, idx=0):
        sIdx=0
        while not isinstance(self.cfgArray[idx][sIdx], str):
            sIdx+=1
        self.cfgArray=self.inflateOnce(self.cfgArray[idx], sIdx)
        self.filter_non_matching()
    def isInflatable(self, arr):
        return any([isinstance(i, str) for i in arr])

    def checkEmptyBracketsError(self):
        if self.current_stmt[-1].content == "]" and self.current_stmt[-2].content == "[":
            error_msg="Unexpected closing bracket. No value inside."
            self.printError([self.current_stmt.copy(), error_msg])
            self.current_stmt.insert(-1, Token("number"))
            self.setCfgArray()
            self.filter_non_matching()
            return True
        return False
    def sendGenericUnexpectedError(self):
        error_msg=f"Unexpected {self.current_stmt[-1]} Token"
        self.printError([self.current_stmt.copy(), error_msg])
        self.current_stmt.pop()
        self.setCfgArray()
    def printInflationPoint(self):
        if self.programIndex>=len(self.baseProgram):
            self.baseProgram.append([])
        for i in self.cfgArray[0]:
            if isinstance(i, str):
                self.baseProgram[self.programIndex].append(i)
                return
    def getInflationPoint(self):
        idx=0
        for i in self.cfgArray[0]:
            if isinstance(i, str):
                return (i, idx)
            idx+=1
    
    def contInflation(self):
        while self.isInflatable(self.cfgArray[0]) and not self.is_partOf(self.cfgArray[0], self.current_stmt):
            #self.printInflationPoint()
            self.inflateFirst(idx=0)
            while len(self.cfgArray)>1:
                self.index+=1
                self.current_stmt.append(self.tokens[self.index])
                self.filter_non_matching()
            if len(self.cfgArray)==0:
                error_msg=f"Unexpected {self.current_stmt[-1]} Token"
                self.printError([self.current_stmt.copy(), error_msg])
                self.current_stmt.pop()
                self.setCfgArray()
                return True
        return False

    def parse(self):
        while self.index < len(self.tokens)-1:
            self.index+=1
            if self.tokens[self.index].type=="unknown":
                self.printError([[self.tokens[self.index]], "Unknown Token"])
                self.current_stmt.append(Token("any", "any"))
                self.setCfgArray()
                continue
            self.current_stmt.append(self.tokens[self.index])
            if len(self.current_stmt)==1 and self.tokens[self.index].type=="end":
                return
            self.filter_non_matching()
            if len(self.cfgArray)>1:
                self.cfgArray=[i for i in self.cfgArray if not all([isinstance(j, str) for j in i])]
            if len(self.cfgArray)==0:
                #if self.checkEmptyBracketsError():
                #    continue
                error_msg=f"Unexpected {self.current_stmt[-1]} Token"
                self.printError([self.current_stmt.copy(), error_msg])
                if self.current_stmt[-1].type!="end":
                    self.current_stmt.pop()
                self.setCfgArray()
                continue
            if(self.contInflation()):
                continue
            currentWithNext=self.currentWithNextToken()
            match self.is_sublist(self.cfgArray[0], currentWithNext):
                case StmtCmpStatus.NOT:
                    if self.cfgArray[0] == self.current_stmt:
                        #self.parsedProgram.append(self.current_stmt.copy())
                        self.programIndex+=1
                        self.current_stmt=[]
                        self.setCfgArray()
                    else:
                        error_msg=self.cfgArray[0][len(currentWithNext)-1]
                        while isinstance(error_msg, str):
                            self.inflateFirst()
                            error_msg=self.cfgArray[0][len(currentWithNext)-1]
                        self.printError([currentWithNext, f"Expected {error_msg} token. Found {currentWithNext[-1]}"])
                        if self.tokens[self.index+1].type=="end":
                            self.tokens.insert(-1, error_msg)
                            continue
                        if error_msg.content==";":
                            self.current_stmt=[]
                            self.setCfgArray()
                            continue
                        self.current_stmt.append(self.cfgArray[0][len(currentWithNext)-1])
                        if error_msg!=self.tokens[self.index+2]:
                            self.index+=1
                        self.setCfgArray()
                        continue
                    continue
                case StmtCmpStatus.SUB:
                    continue
                case StmtCmpStatus.SAME:
                    #self.parsedProgram.append(currentWithNext)
                    self.programIndex+=1
                    self.current_stmt=[]
                    self.index+=1
                    self.setCfgArray()
                    continue


            


if __name__ == "__main__":
    filePath=os.getcwd()+"/"+sys.argv[1]
    with open(filePath, 'r') as file:
        content=file.read()
        tokenizer=Tokenizer(content)
        tokens=tokenizer.tokenize()
        parser=Parser(tokens)
        parser.parse()
        #for stmt in parser.baseProgram:
        #    pass
            #print(stmt, "\n\n")


