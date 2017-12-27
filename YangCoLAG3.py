# -*- coding: utf-8 -*-

from __future__ import print_function

####
# WORKs: That is, duplicates Galana results
#######

# Yang's Variational Learner (adapted from Sakas 2015)
# Given:
# 1)      n, the number of parameters
# 2)      W=(w1, w2, . . . , wn), a vector of weights, 
#           where each wi is stipulated to be between 0 and 1
# 3)      the current grammar (i.e., a vector of parameter values):
#            Gcurr =(p1, p2,  . . . , pn),
#            where each pi is a either a 1 value or a 0 value

##  Pseudo-code#
#	For each wi in W, set wi to 0.5
#	For each randomly chosen input sentence s from the target language: 
#	   For each parameter pi in Gcurr :
#            a. with probability wi , choose the value of pi to be 1;
#            b. with probability 1 - wi , choose the value of pi to be 0 ; 
#	Parse s with Gcurr
#	If s can be parsed by Gcurr, "reward" the weights in W accordingly.


################ Yang Reward-only Learner aligned with code below ###########################
#
# 1)    set all elements of Wcurr to .5 (Wcurr is the W in above Pseudo-code)
# 2)    Gcurr = chooseBasedOn(Wcurr)  -- Choose a grammar randomly weighted by weights in Wcurr vector 
# 3)    s = chooseSentUnif() -- Choose a random sentence from the target language
# 4)    Test if Gcurr can parse (licenses) s
# 5)    if Gcurr can parse s, reward the system by nudging weights: Wcurr = reward(Wcurr) else do nothing
# 6)    if all weights fall within threshold t, output number of sentences and exit
# 7)    goto 2)


from collections import defaultdict
import random
import datetime
import csv

##########
# Globals - Note "grammars" and "sentences" are globally stored as integer "ids"
##########    except for Gtarg and Gcurr (see below)

# ***NEW***, with relevance:

# Dictionary of key:grammID; value:set of sentIDs
LDsents     = defaultdict(set)

# a list of all valid CoLAG grammar IDs, stored as a dict for efficient lookup
CoLAG_Gs = {} # Wm note: This should probably be a set of grammar IDs
                        

#################
### BEGIN Globals
#################

n = 13 # number of parameters
r = .0005  # learning rate
cr = .0001  # conservative learning rate

trials = 10 # number of simulated learning trials to run
max_sents =  50000 # max number of sents before ending a trial
threshold = .02 # when all weights are within a threshold, stop

Wcurr = [] # current weights
Gcurr = [] # current grammar
Gtarg = [] # target grammar
Ltarg = [] # list of sentences (or actually sentIDs) licensed by Gtarg


# Input file, the CoLAG Domain, 3 columns, Grammar ID, Sent ID and Structure ID
LD_File = "./william-code/COLAG_2011_ids.txt"
Irrelevance_String_File = "./irrelevance-output.txt"

Out_Data_Path            = "./"
Out_Data_File_base       = "OUTDATA_REL"
Out_Data_Date_Time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
Out_Data_File = Out_Data_Path+Out_Data_File_base+Out_Data_Date_Time_stamp+".csv"

Notes = "" # Prompt user for notes for the current run


##############
# END Globals
##############


###########
# Global Functions
##########################
def setupLD() :

  global LDsents, LDstructs, CoLAG_Gs, Notes
 

  File = open(LD_File,"r")
  for line in File:
    line = line.rstrip()
   
    [g,       sent,   struct]    = line.split("\t")
    [grammID, sentID, structID, relString] = [int(g), int(sent), int(struct), "~~~~~~~~~~~~~"]
    # when we do relevance we need a way to load proper relevance string, the above is a dummy
                                                                                                 
    # if haven't hit grammID yet in the file, add to list of CoLAG_GS and to LD
    if grammID not in CoLAG_Gs:
        CoLAG_Gs[grammID]=0
        LDsents[grammID]=set()
    
    LDsents  [grammID].add(sentID) # key:int, value:set of ints


def reward(relstr):
  global Wcurr, Gcurr
  for i in range(n):
    if relstr[i] == '~':
      # param is irrelevant, ignore it.
      continue
    update_rate = r
    if relstr[i] == '*':
        # param is ambiguous, be conservative.
        update_rate = cr
    if Gcurr[i]=='0':
      Wcurr[i] -= update_rate * Wcurr[i];
    else:
      Wcurr[i] += update_rate * (1.0-Wcurr[i]);


def converged():
  global Wcurr
  for i in range(n):
    if not (1-Wcurr[i] <  threshold  or Wcurr[i] < threshold): 
      return False
  return True

#def converged(): We may add something like below for sub/super and other problem parameters
#  global Wcurr
#  for i in range(5):
#    if not (1-Wcurr[i] <  threshold  or Wcurr[i] < threshold): 
#      return False
#  for i in range(7,n):
#    if not (1-Wcurr[i] <  threshold  or Wcurr[i] < threshold): 
#      return False
#  return True



def canParse(s,l): # is sentence ID s in language dictionary l?
    if s in l:  # inefficient if l is a list
      return True
    else:
      return False

def chooseGrammarBasedOn(weights):
    Gtmp = ""
    for i in range(n):

### Maybe force correct setting for Eng Wh-movement (P7=1) and OpTOP (P4=1)
#        if i == 6:
#            Gtmp+="1"
#        elif i == 3:
#            Gtmp+="1"
#        else:  
        x = random.random()
        if x < weights[i]: # checked against Charles code
            Gtmp+="1" # probably more efficient to declare static Gtmp and not append
        else:
            Gtmp+="0"
    return Gtmp
 
def chooseSentUnif():  
    #UNIFORM
    x = random.randint(0,len(Ltarg)-1)
    sID = Ltarg[x]
    return sID

def bin2Dec(bList): # bList is a list of 1's and 0's
    binStr = ""
    for b in bList:
        binStr += str(b)
    return int(binStr,2)     
 
def headerOutput(File, NotesP):
    headerstr = "Learning rate:" + str(r) + ", Threshold:" + str(threshold) + ", Note: " + NotesP + ",CovergedID"+","+"\n"
    File.write(headerstr) 

def csvOutput(File, targ, run, cnt, G, W):
    Gout =""
    Wout =""
    Pout =""
    for i in range(n):
      Gout += str(G[i])
    for i in range(n):
      Wout += str(round(W[i],15))+","

    outStr = str(targ)+","+str(run)+","+str(cnt)+","+str(bin2Dec(G))+","+"'"+Gout+","+Wout+"\n"
    File.write(outStr)

def readRelevanceStrings(filename):
  relDict = {}
  with open(filename) as fh:
    for line in fh:
      sid, irrelStr = line.split()
      sid = int(sid)
      relDict[sid] = irrelStr
  return relDict

# use raw_input for python2, input for python3
try:
    input = raw_input
except NameError:
    pass

############################################
## MAIN MAIN MAIN reward only learner
############################################
def run():

    global Wcurr, Gcurr, OUTDATA

    print("Setting up ...")

    OUTDATA = open(Out_Data_File,'w')

    Notes = input("Enter notes for this run: ")

    print("Working ...")

    headerOutput(OUTDATA, Notes)
    
    setupLD() # sets up all 3072 potential target grammars/languages
              # into global LD variables
  
    # CoLAG English, Japanese, German and French
    GTARGS =  [ [0,0,0,1,0,0,1,1,0,0,0,1,1] ,  \
                [0,1,1,1,1,0,0,0,1,0,0,0,0] ,  \
                [0,1,0,0,0,1,1,0,0,1,1,0,1] ,  \
                [0,0,0,1,0,0,1,0,0,1,0,0,0]    \
              ]  
                
    GTARGIDS = [611, 3856, 2253, 584]
    
    global Ltarg

    relevanceStrDict = readRelevanceStrings('./irrelevance-output.txt')

    for targIdx in range(1): # only Enlgish
        
        Gtarg   = GTARGS[targIdx]       # Gtarg is a 13 element list of 0's and 1's
        GtargID = GTARGIDS[targIdx]     # GtargID is a decimal representation of Gtarg
        Ltarg   = list(LDsents[GtargID]) # Ltarg is a list of sentIDs

        overallStart = datetime.datetime.now()
        print("Running ...")

        for runNum in range(trials):
          start = datetime.datetime.now()

          Wcurr = [.5 for i in range(n)] # initialize weights to 0.5

          Gcurr = ""
          
          numSents = 0
          
          CONVERGED = False

          while not CONVERGED and numSents < max_sents:

              Gcurr = chooseGrammarBasedOn(Wcurr)
              GcurrID = int(Gcurr,2) # not needed: bin2Dec(Gcurr)

              # Yang learner doesn't know about CoLAG constraints, so
              #    needs to loop until it finds a valid grammar. May be
              #    faster way to implement this
              while GcurrID not in CoLAG_Gs:
                   Gcurr   = chooseGrammarBasedOn(Wcurr)
                   GcurrID = int(Gcurr,2)  # not needed: bin2Dec(Gcurr)

              s = chooseSentUnif() # s is a sentID

              numSents = numSents + 1


              # if s can be parsed by Gcurr
              if s in LDsents[GcurrID]: # LD[GcurrID] is a set of sentIDs 
                  
                  # grab relevance string of s
                  relevanceStr = relevanceStrDict[s]
                  #   picks a parse tree that generates s given Gcurr
                  #   the 'parser' returns a string indicating which parameters were irrelevant
                  #   in terms of building the parse tree
                  #  DEGUG: print(s, relevanceStr)
                  reward(relevanceStr)
              else:
                  pass # print("GcurrID: ", GcurrID)


                  

              CONVERGED = converged()       

          csvOutput(OUTDATA, GtargID, runNum, numSents, Gcurr , Wcurr)      

          end = datetime.datetime.now()
          elapsed = end - start
          overallElapsed = end - overallStart 
          if runNum % 1 == 0:
            print("GtargID: ", GtargID, "RUN: ", runNum, "took", str(elapsed), "Overall so far: ", overallElapsed)


run()


OUTDATA.close()

print("Done.")
