import pandas as pd
import argparse

# TrieNode class
class TrieNode:

  def __init__(self, character):
    self.character = character # the character the node represents
    self.next_states = [] # a list of the IDs of the child nodes
    self.fail_state = 0 # the ID of the fail state
    self.output = [] # a list of all the complete keywords encountered so far as we have gone through the input text
  
  def printNode(self):
    print("char:", self.character, "next states:", self.next_states, "fail state:", self.fail_state, "output:", self.output)

# method that returns the child index of the trie, if it exists
def getChildID( keywordTree, letter, threadNo):

  childID = None
  
  for state in keywordTree[threadNo].next_states:
    if keywordTree[state].character == letter:
      childID = state
      break
    
  return childID

# method that inserts a letter node to the trie, returns the last threadNo
def insertToTrie(keywordTree, commonNodeIndex, patternLength, pattern, threadNo):

  for newNodeIndex in range(commonNodeIndex, patternLength):
      keywordTree.append(TrieNode(pattern[newNodeIndex]))
      lastIndex = len(keywordTree) - 1
      keywordTree[threadNo].next_states.append( lastIndex)
      threadNo = lastIndex
  
  return threadNo

# method that builds the trie with failure links with inputted patterns
def buildTree(keywordTree, patterns):

  # append root
  keywordTree.append(TrieNode(" "))

  # add pattern to trie
  for pattern in patterns:
    threadNo = 0
    newNodeIndex = 0
    commonNodeIndex = 0
    patternLength = len(pattern)

    # check if letter is already a child
    childID = getChildID( keywordTree, pattern[commonNodeIndex], threadNo)

    # iterate through thread until child is not found
    while commonNodeIndex < patternLength and childID != None:
      threadNo = childID
      commonNodeIndex+=1
      if commonNodeIndex < patternLength:
        childID = getChildID( keywordTree, pattern[commonNodeIndex], threadNo)

    # add new node for letter at the end of thread
    threadNo = insertToTrie(keywordTree, commonNodeIndex, patternLength, pattern, threadNo)
    
    # add output letter for pattern
    keywordTree[threadNo].output.append(pattern)

  # adjust failure links
  adjustFailureLinks(keywordTree)

def failureLinksHelper(keywordTree, element, queue):

  # get children of popped element
  for childID in range(len(keywordTree[element].next_states)):

    # handle next state elements
    child = keywordTree[element].next_states[childID]
    queue.append(child)

    next_state = iterateThruFailState(keywordTree, keywordTree[child].character, keywordTree[element].fail_state)

    keywordTree[child].fail_state = 0 if getChildID(keywordTree, keywordTree[child].character,next_state) == None else getChildID(keywordTree, keywordTree[child].character,next_state)

    output_child = keywordTree[child].output + keywordTree[keywordTree[child].fail_state].output
    keywordTree[child].output = output_child

# method that returns the next state after iterating through fail states
def iterateThruFailState(keywordTree, character, next_state):
  
  while getChildID( keywordTree, character,next_state) == None and next_state != 0:
    next_state = keywordTree[next_state].fail_state
  
  return next_state

# method that forms the failure links on the trie
def adjustFailureLinks(keywordTree):

  # will perform BFS using queue
  queue = []

  # root's children have fail states 0, add them to queue
  for node in keywordTree[0].next_states:
    keywordTree[node].fail_state = 0
    queue.append(node)

  # pop elements until queue is empty
  while(len(queue) > 0):

    # get children of popped element
    failureLinksHelper(keywordTree, queue.pop(), queue)

# method that prints the trie
def printTree(keywordTree, patterns):

  print("Build tree\n----------------------------------------------------------------------")

  for i in range(len(keywordTree)):
    keywordTree[i].printNode()

# search and display text
def ahoCorasickSearch(keywordTree, text):

  print("\nSearch\n----------------------------------------------------------------------")

  # search every text
  threadNo = 0
  
  # for each char in text
  for i in range(len(text)):

    threadNo = iterateThruFailState(keywordTree, text[i], threadNo)     

    # return to root
    threadNo = 0 if getChildID(keywordTree, text[i], threadNo) == None else getChildID(keywordTree, text[i], threadNo)
    
    # display node output
    for j in keywordTree[threadNo].output:
      print("keyword:",j,"index:",i+1-len(j))



def run(args):
  fileName = args.input_fn #"/content/gdrive/My Drive/Colab Notebooks/bhw3/input.txt"
  dataset = pd.read_csv(fileName, header=None)

  patterns = dataset[0][0].split(" ")
  sequences = dataset[0][1]

  keywordTree = [] # will collect TrieNode elements

  buildTree(keywordTree, patterns)

  printTree(keywordTree, patterns)

  ahoCorasickSearch(keywordTree, sequences)

def main():
  parser=argparse.ArgumentParser(description="Aho Corasick Pattern Search.")
  
  parser.add_argument("-i", "--inputFile", help="txt format input file will contain 2 lines. \
  The first line will hold patterns that are separated by space and the text is given in the second line. \
  Output will be printed in the standard output.", dest="input_fn", type=str, required=True)

  parser.set_defaults(func=run)
  args=parser.parse_args()
  args.func(args)

if __name__=="__main__":
  main()