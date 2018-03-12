from colag.colag import Colag, COLAG_TSV, IRRELEVANCE_OUTPUT



def main():

	grammar = input("Enter grammer and I'll find the supersets: ")
	c = Colag.from_tsvs(COLAG_TSV, IRRELEVANCE_OUTPUT)
	supersets = c.find_supersets(grammar)
	print(supersets)


if __name__ == "__main__":
    main()