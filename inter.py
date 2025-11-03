#Operands file
import pV


dO = ['set']
class CheckLine:
    def __init__(self, brokenLine, sec):
        self.brL = brokenLine
        self.sec = sec

    def CCCset(self):
        vn = self.brL[1]
        vv = self.brL[3]
        pV.vars[self.sec].append([vn, vv])
    def runCases(self):
        if self.brL[0] in dO:
            match (self.brL[0]):
                case 'set':
                    self.CCCset()

    def org(self):
        self.runCases()