import sys
from queue import Queue

clause_premise = []
inferred = []


def pl_fc(symbols=None):
    global clause_premise, inferred
    if symbols is None:
        symbols = []
    q = Queue()
    for sym in symbols:
        q.put(sym)

    while not q.empty():
        s = q.get()
        if s not in inferred:
            inferred.append(s)
        for clause in clause_premise:
            if clause["count"] > 0 and s in clause["tail"]:
                clause["count"] = clause["count"] - 1
                if clause["count"] == 0:
                    # add head value into queue
                    for head in clause["head"]:
                        q.put(head)


def handle_premise(clauses=None):
    global clause_premise
    if clauses is None:
        clauses = ["THEN"]
    for cl in clauses:
        premise = {"tail": [], "head": []}
        elements = cl.split("THEN")

        # first process tail
        element = elements[0].strip()
        symbols = element.split("AND")
        premise["count"] = len(symbols)
        for sym in symbols:
            premise.setdefault("tail", []).append(sym.strip())
        # second process head
        element1 = elements[1].strip()
        symbols1 = element1.split("AND")
        for sym1 in symbols1:
            premise.setdefault("head", []).append(sym1.strip())
        clause_premise.append(premise)


def main():
    global inferred
    print("handle input data!")
    text = sys.argv[1]
    clauses = []
    symbols = []
    data_file = open(text)
    for line in data_file.readlines():
        if "THEN" in line:
            clauses.append(line.strip())
        else:
            symbols.append(line.strip())
    print("KB has " + str(len(clauses)) + " conditional clauses and " + str(len(symbols)) + " propositional symbols.")
    print("")
    print("Clauses:")
    if len(clauses) == 0:
        print("        None")
    else:
        for cl in clauses:
            print("        " + cl)
    print("Symbols:")
    if len(symbols) == 0:
        print("        None")
    else:
        for sym in symbols:
            print("        " + sym)

    print("")
    handle_premise(clauses)
    # print(clause_premise)
    pl_fc(symbols)
    # print(inferred)

    while True:
        value = input("Query symbol (or end): ")
        if value == "end":
            break
        if value in inferred:
            print("Yes! "+value+" is entailed by out knowledge-base.")
        else:
            print("No. "+value+" is not entailed by out knowledge-base.")
        print("")


if __name__ == '__main__':
    main()
