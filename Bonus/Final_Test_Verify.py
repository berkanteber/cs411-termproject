import math
import random, string
import warnings
import sys, os
import pyprimes
import hashlib
import DSA, TxBlockGen, PoW

BlockChainTestOn = 1 # set ot 1 if you want to validate the block chain
ValidateTxOn = 1     # set to 1 if you want to validate a transaction

blockCount = int(sys.argv[1]) # number of link in the block chain (you can change)
TxCount = 8    # number of transactions in a block (you can change, but set it to a power of two)
PoWLen = 6     # the number of 0s in PoW (you can change)
TxLen = 10     # no of lines in a transaction (do not change)
LinkLen = 4    # no of lines in a link of the chain (do not change)

# Validate the block chain
if BlockChainTestOn:
    BlockChainFileName = "LongestChain.txt"
    if os.path.exists(BlockChainFileName) == True:
        BlockChainFile = open(BlockChainFileName, "r")
        blocks = BlockChainFile.readlines()
        blockCnt = len(blocks)/LinkLen
        PoW = blocks[LinkLen-1][:-1]

        if PoW != hashlib.sha3_256("".join(blocks[0:LinkLen-1])).hexdigest():
            print "Block chain does not validate:(("
            sys.exit()

        if PoW[0:PoWLen] != "0"*PoWLen:
            print "Invalid proof of work:(("
            sys.exit()

        for i in range(1,blockCnt):
            PrevHash = blocks[LinkLen*i-1]
            if(PrevHash != blocks[LinkLen*i]):
                print "Block chain does not validate:(("
                sys.exit()
            PoW = blocks[(i+1)*LinkLen-1][:-1]
            if PoW != hashlib.sha3_256("".join(blocks[i*LinkLen:(i+1)*LinkLen-1])).hexdigest():
                 print "Block chain does not validate:(("
                 sys.exit()
            if PoW[0:PoWLen] != "0"*PoWLen:
                print "Invalid proof of work:(("
                sys.exit()

        print "Block chain validates:))", "\n"
        BlockChainFile.close()
    else:
        print "Error: ", BlockChainFileName, "does not exist"
        sys.exit()

# Pick a random transaction in a random block and validate it
if ValidateTxOn:
    for cntr in range(1, int(sys.argv[2]) + 1):
        blockNo = random.randint(0,blockCount-1)
        txNo = random.randint(0,TxCount-1)

        print "Trial:", cntr, "\t",
        print "Block: ", blockNo, "\t",
        print "Transaction: ", txNo, "\t",

        # open the transaction block file blockNo and read all transactions in it
        TxBlockFileName = "TransactionBlock"+str(blockNo)+".txt"
        if os.path.exists(TxBlockFileName) == False:
            print "Error"
            sys.exit()

        TxBlockFile = open(TxBlockFileName, "r")
        lines = TxBlockFile.readlines()
        TxBlockFile.close()

        # read the transaction txNo from the file and verify its signature
        transaction = lines[txNo*TxLen:(txNo+1)*TxLen]
        SignedPart = "".join(transaction[0:TxLen-2])
        p = int(transaction[2][3:])
        q = int(transaction[3][3:])
        g = int(transaction[4][3:])
        beta = int(transaction[5][25:])
        r = int(transaction[8][15:])
        s = int(transaction[9][15:])
        if DSA.SignVer(SignedPart, r, s, p, q, g, beta)!=1:
            print "Error"
            sys.exit()

        # Check if the transaction really belongs to that block
        # using "LongestChain.txt file"
        # The method is hash tree
        BlockChainFileName = "LongestChain.txt"
        if os.path.exists(BlockChainFileName) == False:
            print "Error"
            sys.exit()
        BlockChainFile = open(BlockChainFileName, "r")
        blocks = BlockChainFile.readlines()

        # read the root hash from the BlockChainFileName file
        rootHash = blocks[LinkLen*blockNo+1]

        # compute the hash tree from the transaction
        # Construct the hash tree
        hashTree = []
        for i in range(0,TxCount):
            transaction = "".join(lines[i*TxLen:(i+1)*TxLen])
            hashTree.append(hashlib.sha3_256(transaction).hexdigest())

        t = TxCount
        j = 0
        while(t>1):
            for i in range(j,j+t,2):
                hashTree.append(hashlib.sha3_256(hashTree[i]+hashTree[i+1]).hexdigest())
            j += t
            t = t>>1
        h = hashTree[2*TxCount-2]

        if h != rootHash[:-1]:
            print "Error"
            sys.exit()

        print "OK"
        BlockChainFile.close()

    print ""
    print "All %d transactions validate:))" % int(sys.argv[2])
