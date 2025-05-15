b = int(input("base"))
c = [-1]

while True:
	for num in range(len(c)):
		if c[num] < b:
			c[num] += 1
		else:
			c[num] = 0
			try:
				c[num+1] += 1
			except:
				c.append(1)
			if c[num+1] > b:
				c[num] = 0
			
	input(f"{c}")