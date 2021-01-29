#!/usr/bin/env python3

from time import sleep


class Block:
	def __init__(self):
		self.placed = False
		self.x = -1	
		self.y = -1
		self.color = [91,102]

class Display:
	
	def __init__(self,height=20,width=10,update_delay=50):
		self.height=height
		self.width=width
		self.update_delay=update_delay


	def clear_screen(self):
		print("\033c\033[3J", end='',flush=True)	
	

	def disable_cursor(self):
		print("\x1b[?25l")
						

	def draw(self,blocks): # always print two 2 spaces, or 1 block (being two colored blocks)
		block_char = "\033[{};{}m██\033[m"
		text = ""
		for h in range(self.height):
			for w in range(self.width):	
				if w == 0 or w == self.width-1 or h == self.height-1:
					text+="##" 
				else:
					found_block = False
					for b in blocks:
						if b.x==w and b.y==h:
							text += block_char.format(b.color[0],b.color[1])
							found_block = True	
					if not found_block:
						text += "  "
			text+="\n"	
		print(text)	

def main():
	
	display = Display()
	b = Block()
	b.x = 2
	b.y = 3

	blocks = [b]
	for i in range(20):
		display.clear_screen()
		display.draw(blocks)	
		sleep(.3)
		blocks[0].y+=1
	
if __name__ == "__main__":
	main()










