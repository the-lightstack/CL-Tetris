#!/usr/bin/env python3

from time import sleep
from getkey import keys,getkey
import threading
from random import choice

# Global variable
key_queue = []

class Block:
	def __init__(self,x,y,color):
		self.placed = False
		self.x = x	
		self.y = y 
		self.color = color


class Block_Structur:
	
	types = {"I":[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
			 "J":[[1,0,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
			 "L":[[0,0,1,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
			 "O":[[1,1,0,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]],
			 "S":[[0,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]],
			 "T":[[0,1,0,0],[1,1,1,0],[0,0,0,0],[0,0,0,0]],
			 "Z":[[1,1,0,0],[0,1,1,0],[0,0,0,0],[0,0,0,0]],
			}
	colors = {"I":91,"J":92,"L":93,"O":94,"S":95,"T":96,"Z":97}


	def __init__(self,_type,display):
		self.blocks = []	
		self.start_pos = (3,3)		
		self._type = _type
		self.active = True
		self.display = display
		self.color = Block_Structur.colors[self._type]	
		self.init_blocks()
		self.position = list(self.start_pos)#top left of entire block		

	def init_blocks(self):
		own_type = Block_Structur.types[self._type]	
		for i,row in enumerate(own_type):
			for j,col in enumerate(row):
				if col == 1:
					self.blocks.append(Block(self.start_pos[0]+j,self.start_pos[1]+i,self.color))			


	def check_move(self,game_controller):
		try:
			#print("own blocks:")
			#[print(i.x,i.y) for i in self.blocks]
			# Game controller stores the object structs not individual blocks
			global key_queue
			if self.active:
				if len(key_queue)>0:
					#print("Key-queue",key_queue)
					move = key_queue.pop(0)							
					if move == "a":	
						move_valid = True
						for o in self.blocks:
							if o.x-1 < 1: #hits left side wall
								print("Move invalid")
								move_valid = False # do nothing	
							for struct in game_controller.all_structs:
								for block in struct.blocks:
									if o.x-1 == block.x and o.y == block.y:
										move_valid = False	
						if move_valid:
							for i in self.blocks:
								i.x -= 1
							self.position[0] -= 1
						else:
							print("This move is invalid, Sorry!")
					elif move == "d":
						print("Move registered as d")
						move_valid = True
						for o in self.blocks:
							if o.x+1 > self.display.width-2: #hits right side wall
								move_valid = False 
								for struct in game_controller.all_structs:
									for block in struct.blocks:
										if o.x+1 == block.x and o.y == block.y:
											move_valid = False	
						if move_valid:
							#print("Moving Block")
							for i in self.blocks:
								i.x += 1
							self.position[0] += 1
					elif move == "w":
						self.rotate_struct(game_controller)
					
					elif move == "s":
						while 1:
							if self.move_down(game_controller) == "New":
								game_controller.generate_new_active()	
								break
			else:
				print("waisted resources on calling this thing...")
		
		except Exception as e:
			print("Exception in check_move:",e)
			raise e


	def rotate_struct(self,game_controller):

		if self._type == "O":
			return

		rotation_center = [self.position[0]+2,self.position[1]+1]
		
		collide = False	
		for i in self.blocks:
			tmp_x = i.x - rotation_center[0]			
			tmp_y = i.y - rotation_center[1]
			
			new_x = tmp_y + rotation_center[0]
			new_y = -tmp_x + rotation_center[1]	
	
			for b in game_controller.all_structs:
				for a in b.blocks:
					if a.x == new_x and a.y == new_y:
						collide = True		
						break	
					if a.x <= 2 or a.x >= game_controller.display.width-2:
						collide = True
						break
	
			i.x = new_x 
			i.y = new_y


	def move_down(self,game_controller):
		hit_block = False
		for block in self.blocks:
			for struct in game_controller.all_structs:
				for i in struct.blocks:
					if block.y+1 == i.y and block.x == i.x:
						hit_block = True
						break
			if block.y > game_controller.display.height-3:
				hit_block = True 

		if hit_block:
			print("Falling Block is now dead!")
			self.active = False
			game_controller.all_structs.append(self)
			return "New"
		else:
			for i in self.blocks:
				i.y +=1
			self.position[1] += 1

class Display:
	
	def __init__(self,height=20,width=10,update_delay=50):
		self.height=height
		self.width=width
		self.update_delay=update_delay


	def clear_screen(self):
		print("\033c\033[3J", end='',flush=True)	
	

	def disable_cursor(self):
		print("\x1b[?25l")
						

	def draw(self,structs): # always print two 2 spaces, or 1 block (being two colored blocks)
		blocks = []
		for i in structs:
			for b in i.blocks:
				blocks.append(b)
		block_char = "\033[{}m██\033[m"
		text = ""
		for h in range(self.height):
			for w in range(self.width):	
				if w == 0 or w == self.width-1 or h == self.height-1:
					text+="##" 
				else:
					found_block = False
					for b in blocks:
						if b.x == w and b.y == h:
							text += block_char.format(b.color)
							found_block = True	
					if not found_block:
						text += "  "
			text+="\n"	
		print(text)	

class Game_Controller:
	
	def __init__(self,display):
		self.log_thread = threading.Thread(target=self.queue_keys)	
		self.main_thread = threading.Thread(target=self.game_control) 	
		self.block_mover = threading.Thread(target=self.move_structs_down)
		self.player_block_move = threading.Thread(target=self.check_block_move)		
		self.clear_row_thread = threading.Thread(target=self.check_clear_row)		
	
		self.game_speed = .5 
		self.all_structs = []		
		self.active_struct = None
		self.display = display	
		self.generate_new_active()

		self.log_thread.start()
		self.main_thread.start()
		self.block_mover.start()
		self.player_block_move.start()			
		self.clear_row_thread.start()
	
	def move_structs_down(self):
		# remember to add active struct to all structs when placed
		while True:
			resp = self.active_struct.move_down(self)
			if resp == "New":
				self.generate_new_active()	
			sleep(self.game_speed)	


	def generate_new_active(self):
		opts = ["I","J","L","O","S","T","Z"]				
		#new_struct = Block_Structur(choice(opts),self.display)
		new_struct = Block_Structur("O",self.display) # <= Just for testing
		self.active_struct = new_struct		

	def clear_row(self,cleared_row_num):
		for s in self.all_structs:
			for b in s.blocks:
				if b.y == cleared_row_num:
					s.blocks.remove(b)	
				elif b.y < cleared_row_num:
					b.y +=1

	def check_clear_row(self):
		while True:	
			for i in range(1,self.display.height):
				counter = 0
				for s in self.all_structs:
					for block in s.blocks:
						if block.y == i:
							counter += 1	
				if counter == self.display.width-2:
					print("Cleared row ",i)
					self.clear_row(i)
			sleep(0.2)

	def game_control(self):
		while True:
			#self.display.clear_screen()
			structs = self.all_structs+[self.active_struct] 
			self.display.draw(structs)	
			sleep(self.game_speed)
	
	def check_block_move(self):
		while True:
			self.active_struct.check_move(self)
			sleep(0.05)# This delay should be fairly low so the player gets direct move-feedback

	def queue_keys(self):
		global key_queue  
		while True:
			key_queue.append(getkey())

def main():
	
	display = Display()
	
	game_c = Game_Controller(display)

if __name__ == "__main__":
	main()

