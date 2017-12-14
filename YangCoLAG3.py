
# 1)    set all elements of Wcurr to .5
# 2)    Gcurr = chooseBasedOn(Wcurr)
# 3)    s = penalty (Gcurr, Gtarg)
# 4)    based on s, make a random decision if Gcurr can parse s
# 5)    if Gcurr can parse s, Wcurr = reward(Wcurr) else Wcurr = punish(Wcurr)
# 6)    if all weights fall within threshold t, output number of sentences and exit
# 7)    goto 2)

from collections import defaultdict
import bisect
import random
import cProfile
import datetime

##########
# Globals - Note "grammars" and "sentences" are globally stored as integer "ids"
##########    except for Gtarg, and Gcurr (see below)

#LD = defaultdict(list) # the Language Domain
                       # key = grammar, value = list of sentences licensed by the grammar
                       # !!! the list of sentences should be a dict for efficient lookup !!!
LD = defaultdict(lambda: defaultdict(int))
                        
LD_File = "/Users/Wm1/Desktop/CoLAG_Research/YangPython/COLAG_2011_ids.txt"
# The CoLAG Domain, 3 columns, Grammar ID, Sent ID and Structure ID

debug_file = "/Users/Wm1/Desktop/CoLAG_Research/YangPython/debug.txt"
debug_freq = defaultdict(int)

Sent_Dist_File = "/Users/Wm1/Desktop/CoLAG_Research/YangPython/COLAG_2011_sents_w_freq.txt"
# a freq distribution of the CoLAG sentences
#  now mostly 0 except for those English CHILDES
#  sentences that occur in CoLAG
# Four Columns: Sent ID, illocutionary force, sentence pattern and frequency

Out_Data_File = "/Users/Wm1/Desktop/CoLAG_Research/YangPython/OUTDATA.csv"


n = 13 # number of parameters
r = .0005  # learning rate
trials = 100  # number of simulated learning trials to run
max_sents =  5000000 # max number of sents before ending a trial
B = 5 # batch threshold if used
threshold = .02 # when all weights are within a threshold, stop
Wcurr = [] # current weights
Gcurr = [] # current grammar
Gtarg = [] # target grammar
Freq_Sent =[] # a sorted list of tuple pairs (frequency, sentence)

Weighted_Sents = object # an object to draw sentences from the target language
                        # based on a frequency distribution. See Class WeghtedRandomGenerator below
                      

#     Gs = LD.keys() # a list of all valid CoLAG grammar IDs
# Convert list into a dictionary, 
# a dictionary of CoLAG Grammars - value of 0 is a dummy value;
#   a dictionary is used for efficient  lookup.

CoLAG_Gs = {}
#    for g in Gs:
#        CoLAG_Gs[g]=0


# set target grammar equal to CoLAG English
Gtarg = [0,0,0,1,0,0,1,1,0,0,0,1,1]
GtargID = int("0001001100011",2)

Ltarg = [] # list os sentences licensed by Gtarg

###########
# END Globals
##############

############
# CLASS WeightedRandomGenerator
#
# Takes the sorted gloable list Freq_Sent of tuple pairs (frequency, sentence) and creates
#   a running total of frequencies at instantiation.
#   getRand() returns a tuple randomly chosen weighted by the frequencies
#  NOTE: The frequencies must be sorted on frequency.

class WeightedRandomGenerator:
    def __init__(self):
        self.totals = []
        running_total = 0

        for f in Freq_Sent:
            running_total += f[0] # frequency is first in pair
            self.totals.append(running_total)

    def getRand(self):
        rnd = random.random() * self.totals[-1]
        idx = bisect.bisect_right(self.totals, rnd)
        return Freq_Sent[idx]

###########
# Global Functions
##########################
def setupLD() :
  File = open(LD_File,"r")
  for line in File:
    line = line.rstrip()
    # grab the ID's - all are int's so map works
    [grammID, sentID, structID] = map(int, line.split("\t"))

    if grammID not in CoLAG_Gs:
        CoLAG_Gs[grammID]=0
        LD[grammID]={}
    # add grammID, SentID as key, 0 is dummy value (and ignore structID)
    global LD, CoLAG_Gs
    LD[grammID][sentID]=0

def setupLtargAndSentenceFrequencies() : 
  global Weighted_Sents
  global Freq_Sent
  global Ltarg
  Ltarg = LD[GtargID].keys() # Ltarg is a list of sentIDs
  Ldist =[]
  # dictionary to temporarily hold the frequencies of all Colag Sentence
  #   patterns
  freqs = defaultdict(int)

  # go to the file to grab frequencies of sentence patterns
  File = open(Sent_Dist_File,"r")
  for line in File:
    line = line.rstrip()
    # grab columns all as strings
    [col1, col2, col3, col4] = line.split("\t")
    # then convert relevant to ints
    [sentID, freq] = [int(col1), int(col4)]
    # add to dictionary - key:sentID, value:frequency
    freqs[sentID] = freq

  # now create a list of sentence distributions (Ldist) corresponding exactly
  #  (by index) to Ltarg

  for sent in Ltarg:
    Ldist.append(freqs[sent])

  # now create the global (sent, frequency) tuple list
  Freq_Sent = zip(Ldist,Ltarg)
  Freq_Sent.sort()

  # and the GLOBAL weighted random generator object
  Weighted_Sents = WeightedRandomGenerator()

   

def reward() :  # CHECK
  global Wcurr, Gcurr
  for i in range(n):
    if Gcurr[i]==0:
      Wcurr[i] -= r*Wcurr[i];
    else:
      Wcurr[i] += r*(1.0-Wcurr[i]);

def punish() : # CHECK
  global Wcurr, Gcurr
  for i in range(n):
    if Gcurr[i]==0:
      Wcurr[i] += r*(1.0-Wcurr[i]);
    else:
      Wcurr[i] -= r*Wcurr[i];

def converged():
  global Wcurr
  for i in range(n):
    if not (1-Wcurr[i] <  threshold  or Wcurr[i] < threshold): 
      return False
  return True

def canParse(s,l): # is sentence ID s in language dictionary l?
  if s in l:  # inefficient
    return True
  else:
    return False
  
def chooseGrammarBasedOn(weights):
    Gtmp =[]
    for i in range(n):
        x = random.random()
        if x < weights[i]: # checked against Charles code
            Gtmp.append(1)
        else:
            Gtmp.append(0)
        
    return Gtmp
  
def chooseSentDist(): 
    # based on distribution
    freq_sent_pair = Weighted_Sents.getRand()
    return freq_sent_pair[1] # the second item is the sentence

def chooseSentUnif():  
#UNIFORM
    x = random.randint(0,len(Ltarg)-1)
    sID = Ltarg[x]
# DEBUG DEBUG
#    debug_freq[sID] += 1
############################################
    return sID


def bin2Dec(bList): # bList is a list of 1's and 0's
    binStr = ""
    for b in bList:
        binStr += str(b)
    return int(binStr,2)     
    
    
    
def csvOutput(File, run, cnt, G, W):
    Gout =""
    Wout =""
    for i in range(n):
      Gout += str(G[i])
    for i in range(n):
      Wout += str(round(W[i],15))+","

    outStr = str(run)+","+str(cnt)+","+str(bin2Dec(G))+","+"'"+Gout+","+Wout+"\n"
    File.write(outStr)
  
############################################
## MAIN MAIN MAIN reward only learner
############################################
def run():

    global Wcurr, Gcurr, OUTDATA

    print "Setting up ..."
    setupLD()
    setupLtargAndSentenceFrequencies()

    OUTDATA = open(Out_Data_File,"w")

    overallStart = datetime.datetime.now()    
    print "Running ..."

    for runNum in range(trials):
      start = datetime.datetime.now()
      Wcurr = [.5 for i in range(n)] # initialize weights to 0.5

      Gcurr = [-1]
      GcurrID = bin2Dec(Gcurr)
      numSents = 0
      b = 0

      while not converged() and numSents < max_sents:

          Gcurr = chooseGrammarBasedOn(Wcurr)
          GcurrID = bin2Dec(Gcurr)
          while GcurrID not in CoLAG_Gs:
               Gcurr = chooseGrammarBasedOn(Wcurr)
               GcurrID=bin2Dec(Gcurr)

          s = chooseSentUnif()
          #s = chooseSentDist()
          
          numSents = numSents + 1
         
          if canParse(s,LD[GcurrID]):
              reward()

      

      csvOutput(OUTDATA, runNum, numSents, Gcurr , Wcurr)      

      end = datetime.datetime.now()
      elapsed = end - start
      overallElapsed = end - overallStart 
      if runNum % 1 == 0:
        print "RUN: ", runNum, "took", str(elapsed), "Overall so far: ", overallElapsed


run()

#cProfile.run('run()')

#DEBUG:
#for key in debug_freq:
#  print debug_freq[key], key
    
OUTDATA.close()

print "Done."

"""

############################################
## MAIN MAIN MAIN Batch Leaner
############################################
setupLD()
setupLtarg()

Wcurr = [.5 for i in range(n)]
numSents = 0
b = 0

while notConverged():
       
    Gcurr = chooseGrammarBasedOn(Wcurr)

    s = chooseSent()

    numSents = numSents + 1
   
    if canParse(s,Ltarg):
        b = b + 1
    else:
        b = b - 1

    if b == B:
      reward()
      b = 0
     
    if b == -B:
      punish()
      b = 0
       
    if numSents % 100000 == 0:
      print numSents, Gcurr, Wcurr

"""
