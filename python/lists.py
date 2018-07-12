
file = open("in", "r")
book =[]
x = 0
wcount = 0
shelf = []
for line in file.readlines():
	for word in line.split():
		book.append(word)
		wcount = wcount + 1
	x = x + 1
print "A Study in Scarlet report ***\n"
print "Contains %s words." % wcount
print "Contains %s lines." % x
print "Number of it's:", book.count('it')
print "Number of and's:", book.count('and')
print "Number of the's:", book.count('the')
print "Number of Holmes's:", book.count('Holmes')
print "Number of Watson's:", book.count('Watson')
print "Number of deduction's:", book.count('deduction')
print "Number of Mormon's:", book.count('Mormon')
print "Shelving book........"
for z in range(len(book)):
	item = book.pop()
	shelf.append(item)
print "Book: ", len(book)
print "Shelf: ", len(shelf)
#for z in range(len(shelf)):
#	print shelf[z]
