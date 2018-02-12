# Generate RELEVANCE strings for all CoLAG sentence patterns
#  (Note: easy to rewrite for all CoLAG tree structures).

# Revelvance string is a 13 character string -- one character for each of the 13 parameters in CoLAG
# Each character is one of:

#    * ambiguous,
#    ~ irrelevant,
#    1 unambiguous for the 1 vale,
#    0 unambiguous for the 0 value

# So, for example, give sentence s, a relevance string of 0101~0**~010* would indicate that
# for sentence s:
#   Only CoLAG grammars with paramters P1, P3, P6, P10 and P12 set to the 0 value can generate s.
#   Only CoLAG grammars with paramters P2, P4, P11 set to the 1 value can generate s.
#   Parameters P7, P8 and P13 require either a 0 value or a 1 value depending on the settings of other
#      parameters - i.e., the settings of P7, P8 and P13 are ambiguous wrt sentence pattern s
#   Parameters P5 and P9 are irrelevant to the generation of s, i.e., for every grammar that licenses s,
#      there exists a "minimal pair" grammar with P5 (or p8) toggled to it's opposite value all other
#      parameter values remaining intact.
# *****************
####  MAYBE URGENT NOTE: the algorithm only checks one P at a time. Need to think about multiple Ps
#                        I.e., if we know p5 is irrelevant, then we don't don't need a minimal pair
#                        wrt p5 -- p5 can be either zero or one hence a two-pair would be fine.
#******************

from collections import defaultdict
import datetime

LD_Sents_only_File = "../data/COLAG_2011_sents.txt"
# CoLAG sentIDs, and Illoc and sent strings only

LD_NG_GrammIDs_File = "../data/NG_GrammIDs.txt"
# No Good, disallowed grammar IDs due to parameter constraints in CoLAG

LD_File = "../data/COLAG_2011_ids.txt" #COLAG_2011_ids.txt"
# The CoLAG Domain, 3 columns, Grammar ID, Sent ID and Structure ID

OUT_File = "./COLAG_2011_sentID_rel_new.txt" # COLAG_2011_ids_rel.txt"

def binary(n, digits=8):
    return "{0:0>{1}}".format(bin(n)[2:], digits)

# Returns a relevance string given:
#   A sentence ID (SID),
#   A set of all grammars in CoLAG that license SID
#   The number of parameters in CoLAG (n=13)
#   The disallowed grammars due to CoLAG constraints: NGGSet No Good Grammar Set
def genRelevanceStr(Gset, n, SID, NGGSet):
    # empty relevance string
    retVal = ""

    # List of ambig/irrelevant P's
    irrList = []

    # COMPUTE 1 and 0 (unambiguous)
    Glist = list(Gset) # convert to list to use indices

    # for all parameters
    for i in range(n):

         compareChar = Glist[0][i] # compareChar will be 0 or 1 based on first G (Glist[0])

         j = 1 # set j for second G in list
         Glen = len(Glist)

         pValChange = False

         while (j<Glen and not pValChange):
           if (Glist[j][i] != compareChar):
               pValChange = True
           else:
               j += 1
         #Post condition: j is past Glist - there was no pValChange
                        # j < len(Glist) - there was at least one pValChange
         if j == Glen:
           retVal = retVal + compareChar
         else:
           retVal = retVal +"~"
           irrList.append(i) # save indicies where P is ambig or irrel

        # Consider all ~'s and confirm they are irrelvant if not overwrite ~ with *

        # This is Newer Algorithm from Irrelevance and Ambiguity - 2017. Dated 11/21/17 in file.

        # Gdisallowed = all CoLAG grammars that are disallowed by parameter constraints
        # Given sentence pattern Si
        # Gset = all grammars that generate Si
        # Relstr = set 0 and 1 for unambiguous values, set ~ elsewhere

        # For all Pi (i = 1 to 13, where Relstr[i] == ~):
        #         For all Gj in Gset:
        #                 Gnew = Gj toggled Pi  ##(Gnew and Gj are minimal pairs with only Pi toggled)
        #                 If Gnew notin (Gset or Gdisallowed):
        #                         Relstr[i] = *

    # For all Pi (i = 1 to 13, where Relstr[i] == ~):
    for i in irrList:

    #    For all G in Gset:
         for G in Gset:

    #        Gnew = G toggled Pi  ##(Gnew and G are minimal pairs with only Pi toggled)
             if G[i]=='1':
                bit = '0'
             else:
                bit = '1'
             Gnew = G[:i] + bit + G[i+1:]

    #	     If Gnew notin (Gset or Gdisallowed):
    #           Relstr[i] = *
             if Gnew not in Gset and Gnew not in NGGSet:
                retVal = retVal[:i] + "*" + retVal[i+1:]

    return retVal

def main():
    #*******************
    #*  MAIN
    #***********************

    print("Creating sent and struct tables ...")
    begin = datetime.datetime.now()

    print()


    # Create lookup dictionaries:

    #   key: sentID ; value: set of grammars that generate sentID
    sentLookupTable     = defaultdict(set)

    # key: sentID; value: illoc+" "+sent
    sentTable       = defaultdict(str)


    runNum = 0
    SentFile = open(LD_Sents_only_File,"r")
    for line in SentFile:
        line = line.rstrip()
        [sentIDstr, illocStr, sentStr] = line.split("\t")
        [sentID, illoc, sent] = [int(sentIDstr), illocStr, sentStr]

        sentTable[sentID] = illoc +"\t"+ sent

    # Disallowed Grammars
    NG_Grammars = set()

    NGGFile = open(LD_NG_GrammIDs_File,"r")
    for line in NGGFile:
        NG_Grammars.add('{0:013b}'.format(int(line.rstrip())))
    NGGFile.close()

    File = open(LD_File,"r")
    OUT  = open(OUT_File,"w")
    for line in File:
      line = line.rstrip()

      # grab the ID's - all are int's so map works
      [grammID, sentID, structID] = map(int, line.split("\t"))

      # setup dictionary to look up all 13-bit grammars that generate sentID
      sentLookupTable[sentID].add(binary(grammID,13))

      if runNum % 1000000 == 0:
        end = datetime.datetime.now()
        elapsed = end - begin
        print("Sent num: ",  runNum, " took ", str(elapsed))
      runNum +=1

    print()
    print("Generating relevance strings ...")
    print()

    ## Generate relevance strings
    for sentID, Gset in sentLookupTable.items():

        # sentID = structSentTable[structID]
        sent   = sentTable[sentID]
        outStr = str(sentID)+"\t"+sent+"\t"+genRelevanceStr(Gset, 13, sentID, NG_Grammars)+"\n"
        OUT.write(outStr)

        if sentID % 10000 == 0:
            end = datetime.datetime.now()
            elapsed = end - begin
            print(sentID, " Elapsed time: ", str(elapsed))

    end = datetime.datetime.now()
    elapsed = end - begin
    print(sentID, " Elapsed time: ", str(elapsed))

    OUT.close()
    File.close()
    SentFile.close()
    end = datetime.datetime.now()
    elapsed = end - begin
    print("Elapsed time: ", str(elapsed))

if __name__ == "__main__":
    main()
