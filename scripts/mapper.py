import sys 

def main(): 
	for line in sys.stdin: 
		if "SMS" in line: 
			print line

if __name__ == '__main__':
	main()