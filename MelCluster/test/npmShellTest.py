import sys
import MelCluster
import time

#should accept data from https://www.npmjs.com/package/python-shell
#prints the previously input data
def main():
	data = 'No previous data'
	while True:
		newData = sys.stdin.readline()
		print(data)
		data = newData

		#change this to change delay time
		time.sleep(3)

		if newData == '-1':
			break

if __name__ == '__main__':
	main()