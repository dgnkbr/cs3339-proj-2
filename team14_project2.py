# Updated for python 3
# Disassembles MIPS binary and simulates through code
# Input: Mips binary
# Output: Dissasembled MIPS code and Simulation
# Requires MIPS binary as arg: 	-i [BINARY_FILE.TXT]
# Requires output as arg:		-o [DISSASEMBLED_MIPS_FILE_NAME]
#	 (will create DISSASEMBLED_MIPS_FILE_NAME_dis.txt and  DISSASEMBLED_MIPS_FILE_NAME_sim.txt)
# Optional Args:
#	-v OR -verbose: Enables verbose memory output
#	-d OR -debug: Enables debug output

import sys
import fileinput

opcodeBin = []  # <type 'list'>: ['Invalid Instruction', 'ADDI', 'SW', 'Invalid Instruction', 'LW', 'BLTZ', 'SLL',...]
instrSpaced = [] # <type 'list'>: ['0 01000 00000 00001 00000 00000 001010', '1 01000 00000 00001 00000 00000 001010',...]
arg1 = [] # <type 'list'>: [0, 0, 0, 0, 0, 1, 1, 10, 10, 0, 3, 4, 152, 4, 10, 1, 0, 112, 0]
arg2 = [] # <type 'list'>: [0, 1, 1, 0, 1, 0, 10, 3, 4, 5, 0, 5, 0, 5, 6, 1, 1, 0, 0]
arg3 = [] # <type 'list'>: [0, 10, 264, 0, 264, 48, 2, 172, 216, 260, 8, 6, 0, 6, 172, -1, 264, 0, 0]
arg1Bin = [] # <type 'list'>: ['', '\tR1', '\tR1', '', '\tR1', '\tR1', '\tR10', '\tR3', '\tR4', .....]
arg2Bin = [] # <type 'list'>: ['', ', R0', ', 264', '', ', 264', ', #48', ', R1', ', 172', ', 216', ...]'
arg3Bin = [] # <type 'list'>: ['', ', #10', '(R0)', '', '(R0)', '', ', #2', '(R10)', '(R10)', '(R0)',...]
mem = [] # <type 'list'>: [-1, -2, -3, 1, 2, 3, 0, 0, 5, -5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
binMem = [] # <type 'list'>: ['11111111111111111111111111111111', '11111111111111111111111111111110', ...]
valid = []
opcode = []
pc = 96
memStart = 0
global file, file2
shift = []
func = []
registers = [0 for i in range(32)]
regDict = {x: 'R' + str(x) for x in range(32)}
# opcodeDict has to be modified from orig values because we are using first bit as valid bit! values over 0x1F must have 0x20 subtracted
opcodeDict = {2: 'J', 3: 'JAL', 5: 'BNE', 6: 'BLEZ', 8: 'ADDI', 28: 'MUL', 3: 'LW', 11: 'SW'}
funcDict = {0: "SLL", 2: 'SRL', 8: 'JR', 10: 'MOVZ', 13: 'BREAK', 32: 'ADD', 34: 'SUB', 36: 'AND', 37: 'OR', 38: 'XOR', 28: 'MUL'}
pcDict = {}

# verbose flag; enables verbose memory output
verbose = False
for i in range(len(sys.argv)):
	if sys.argv[i] == ("-v" or "-verbose") and i < (len(sys.argv) - 1):
		verbose = True
# global debug bool; turns on various debug lines
debug = False
for i in range(len(sys.argv)):
	if sys.argv[i] == ("-d" or "-debug") and i < (len(sys.argv) - 1):
		debug = True

class main():

	#def __init__(self):

		def disassemble(self):
			global file, file2
			global opcodeBin
			global opcode#
			global instrSpaced
			global arg1
			global arg1Bin#
			global arg2
			global arg2Bin#
			global arg3
			global arg3Bin#
			global mem
			global binMem
			global valid#
			global shift
			global func
			global memStart

			def parseRInstruction(instr, ctr):
				if opcodeBin[ctr] == '11100':
					opcode.append(opcodeDict[int(opcodeBin[ctr], 2)])
				else:
					opcode.append(funcDict[int(func[ctr], 2)])
				arg1.append(regDict[int(arg1Bin[ctr], 2)])
				arg2.append(regDict[int(arg2Bin[ctr], 2)])
				arg3.append(regDict[int(arg3Bin[ctr], 2)])
				shamt = int(shift[ctr], 2)
				# tab for debug readability
				if debug:
					print ('\t',)
				# sll, srl
				if (func[ctr] == '000000' or func[ctr] == '000010') and arg1Bin[ctr] == '00000':
					# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg3[ctr] + ', ' + arg2[ctr] + ', #' + str(shamt)
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg3[ctr] + ', ' + arg2[ctr] + ', #' + str(shamt) + '\n')
				# jr
				elif arg1Bin[ctr] != '00000' and arg2Bin[ctr] == '00000':
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg1[ctr] + '\n')
				# mul
				elif func[ctr] == '000010' and int(opcodeBin[ctr], 2):
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg3[ctr] + ', ' + arg1[ctr] + ', ' + arg2[ctr] + '\n')
				# and, or, xor, movz
				else:
					# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg3[ctr] + ', ' + arg1[ctr] + ', ' + arg2[ctr]
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg3[ctr] + ', ' + arg1[ctr] + ', ' + arg2[ctr] + '\n')
				return

			def parseJInstruction(instr, ctr):
				opcode.append(opcodeDict[int(opcodeBin[ctr], 2)])
				imm = int(arg1Bin[ctr] + arg2Bin[ctr] + arg3Bin[ctr] + shift[ctr] + func[ctr], 2)
				# bitshit immediate value 2
				imm <<= 2

				### PC = nPC; nPC = (PC & 0xf0000000) , this is resulting in 0, not sure if supposed to update pc
				# hexshifter = 0xf0000000
				###
				# newPC = pc & hexshifter
				### print pc
				### print newPC

				arg1.append('')
				arg2.append('')
				arg3.append('')
				# tab for debug readability
				if debug:
					print ('\t',)

				# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + '#' + str(imm)
				file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + '#' + str(imm) + '\n')
				return

			def parseIInstruction(instr, ctr):
				# append opcode to list from opcode dictionary
				opcode.append(opcodeDict[int(opcodeBin[ctr], 2)])
				imm = arg3Bin[ctr] + shift[ctr] + func[ctr]
				arg1.append(regDict[int(arg1Bin[ctr], 2)])
				arg2.append(regDict[int(arg2Bin[ctr], 2)])
				#arg3.append(imm)
				if imm[0] == '1':
					inversedLine = imm.replace('1', '2').replace('0', '1').replace('2', '0')
					imm = str((0 - int(inversedLine, 2) - 1))
					arg3.append(imm)
				else:
					arg3.append(str(int(imm, 2)))
				# tab for debug readability
				if debug:
					print ('\t',)
				# check if offset I instruction
				# sw
				if opcodeBin[ctr] == '00011' or opcodeBin[ctr] == '01011':
					# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg2[ctr] + ', ' + str(imm) + '(' + arg1[ctr] + ')'
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg2[ctr] + ', ' + str(int(imm, 2)) + '(' + arg1[ctr] + ')' + '\n')
				# blez
				elif opcodeBin[ctr] == '00110':
					# check if negative
					if imm[0] == '1':
						inversedLine = imm.replace('1', '2').replace('0', '1').replace('2', '0')
						imm = str((0 - int(inversedLine, 2) - 1) * 4)
					# simulate shift right x2, change to actual shift?
					else:
						imm = int(imm, 2) * 4
					# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg1[ctr] + ', #' + str(imm)
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg1[ctr] + ', #' + str(imm) + '\n')
				# bne
				elif opcodeBin[ctr] == '00101':
					imm = int(imm, 2) * 4
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg1[ctr] + ', ' + arg2[ctr] + ', #' + str(imm) + '\n')
				else:
					# check if negative
					if imm[0] == '1':
						inversedLine = imm.replace('1', '2').replace('0', '1').replace('2', '0')
						imm = str((0 - int(inversedLine, 2)) - 1)
					# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg2[ctr] + ', ' + arg1[ctr] + ', #' + str(imm)
					file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + opcode[ctr] + '\t' + arg2[ctr] + ', ' + arg1[ctr] + ', #' + str(int(imm, 2)) + '\n')
				return

			def parseInvalidInstruction(instr, ctr):
				###
				### If NOT VALID, append '' to all lists
				###
				opcode.append('')
				opcodeBin.append('')
				arg1Bin.append('')
				arg2Bin.append('')
				arg3Bin.append('')
				arg1.append('')
				arg2.append('')
				arg3.append('')
				shift.append('')
				func.append('')
				# tab for debug readability
				if debug:
					print ('\t',)
				# print instrSpaced[ctr] + '\t' + str(pc) + '\t' + 'Invalid Instruction'
				file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + 'Invalid Instruction' + '\n')
				return

			def parseNOPInstruction(instr, ctr):
				opcode.append('NOP')
				arg1.append('')
				arg2.append('')
				arg3.append('')

				if debug:
					print ('\t',)

				file.write(instrSpaced[ctr] + '\t' + str(pc) + '\t' + 'NOP' + '\n')

				return

			def isBreak(line):
				if line == '10000000000000000000000000001101':
					return True
				else:
					return False

			def parseData(pc, ctr, fileIn):
				global memStart
				# counter to return to memory portion of file
				x = 0
				for line in fileinput.input(fileIn):
					# return to memory
					if x > ctr:
						if memStart == 0:
							memStart = pc
						# remove newline/tab
						line = line.replace('\n', '').replace('\t', '')
						# print line,
						file.write(line,)
						binMem.append(line)
						# if negative
						if line[0] == '1':
							# flip bits of memory
							inversedLine = line.replace('1', '2').replace('0', '1').replace('2', '0')
							# subtract one
							negated = (0 - int(inversedLine, 2)) - 1
							mem.append(negated)
							# print '\t' + str(pc) + '\t' + str(negated)
							file.write('\t' + str(pc) + '\t' + str(negated) + '\n')
						else:
							mem.append(int(line, 2))
							# print '\t' + str(pc) + '\t' + str(int(line, 2))
							file.write('\t' + str(pc) + '\t' + str(int(line, 2)) + '\n')
						ctr = ctr + 1
						pc = pc + 4
					x = x + 1
				fileinput.close()
				return

			def addInstrSpaced(instr):
				# parse instruction into spaced version.
				# better way to do with string.format?
				temp = []
				temp.append(instr[0] + ' ')
				temp.append(instr[1:6] + ' ')
				temp.append(instr[6:11] + ' ')
				temp.append(instr[11:16] + ' ')
				temp.append(instr[16:21] + ' ')
				temp.append(instr[21:26] + ' ')
				temp.append(instr[26:32])
				out = ''.join(temp)
				instrSpaced.append(out)
				return

			def parseFile(fileIn):
				global valid
				global opcodeBin
				global arg1Bin
				global arg2Bin
				global arg3Bin
				global pc

				# main parse loop
				i = 0
				for line in fileinput.input(fileIn):
					# remove newline char
					line = line.replace('\n', '').replace('\t', '')
					if debug:
						print (i)
					###
					### CHECK FOR BREAK
					###
					if isBreak(line) is True:
						opcode.append('BREAK')
						addInstrSpaced(line)
						# print instrSpaced[i] + '\t' + str(pc) + '\t' + 'BREAK'
						file.write(instrSpaced[i] + '\t' + str(pc) + '\t' + 'BREAK' + '\n')
						fileinput.close()
						#increment pc because moving to next instruction/memory
						pc = pc + 4
						parseData(pc, i, fileIn)
						break
					#add to instrSpaced list
					addInstrSpaced(line)
					if debug:
						print ('\t'+instrSpaced[i])
					# check to see if valid instruction
					valid.append(True if (int(line, 2) >> 31) == 1 else False)
					if valid[i] == False:
						parseInvalidInstruction(line, i)
					else:
						# pull opcode out of line
						opcodeBin.append(line[1:6])
						# pull arg1
						arg1Bin.append(line[6:11])
						# pull arg2
						arg2Bin.append(line[11:16])
						# pull ar3
						arg3Bin.append(line[16:21])
						# pull shift
						shift.append(line[21:26])
						# pull func
						func.append(line[26:32])
						# if opcode == 0 for R instruction
						if (opcodeBin[i] == '00000' or opcodeBin[i] == '11100') and (shift[i] != '00000' or func[i] != '000000'):
							parseRInstruction(line, i)
						# if opcode == 2 for J instruction or opcode == 0 and func == 8
						elif opcodeBin[i] == '00010' or (opcodeBin[i] == '00000' and func[i] == '001000'):
							parseJInstruction(line, i)
						elif opcodeBin[i] == '00000' and func[i] == '000000' and shift[i] == '00000':
							parseNOPInstruction(line, i)
						else:
							parseIInstruction(line, i)

					i = i + 1
					pc = pc + 4
					# print debug newline
					if debug:
						print
				return

			parseFile(inputFile)
			return

		def simulate(self):
			global file2
			global valid
			global opcodeBin
			global arg1Bin
			global arg2Bin
			global arg3Bin
			global pc
			global instr
			y = 96
			for x in opcode:
				pcDict[y] = x
				y += 4
			if debug:
				print (pcDict)
			c = 1
			instr = 0
			if opcode[instr] == '':
				instr = instr + 1
				pc = pc + 4
			def statePrint():
				print ("=====================")
				#TODO: needs to change according to what type of instruction?
				#TODO: change like stateWrite so less than 8 mem elements prints
				#TODO: enable verbose flag in printing
				print ('cycle:'+str(c)+'\t'+str(pc)+'\t'+'\n')
				print ("registers:")
				for x in range(4):
					print ("r" + str(x * 8).zfill(2) + ":\t",)
					for y in range(8):
						# removes brackets from sublists while printing str representation of list
						print (str(registers[y + x * 8]).replace('[', '').replace(']', ''),)
						if y < 7:
							print ('\t',)
						else:
							print()
				print ("\ndata:")
				for x in range(len(mem)/8):
					print (str(memStart + (x * 8*4)) + ':\t',)
					for y in range(8):
						print (str(mem[y + x * 8]).replace('[', '').replace(']', ''),)
						if y < 7:
							print ('\t',)
						else:
							print()
				print
				return
			def stateWrite():
				file2.write("\nregisters:\n")
				for x in range(4):
					file2.write("r" + str(x * 8).zfill(2) + ":\t", )
					for y in range(8):
						# removes brackets from sublists while printing str representation of list
						file2.write(str(registers[y + x * 8]).replace('[', '').replace(']', ''), )
						if y < 7:
							file2.write('\t', )
						else:
							file2.write('\n')
				file2.write("\ndata:\n")
				# if less then 8 elements, set length to 1 to print first z ( next loop ) elements
				length = float(len(mem))/float(8)
				if length > 0 and length < 1:
					length = 1
				for x in range(int(length)):
					# if memory is blank, do not show line; to match with expected output
					# can be enabled/disabled by -verbose (-v) flag
					if not verbose:
						empty = True
						# check to see if all 8 bytes are 0
						for e in mem[0+(8*x):7+(8*x)]:
							if e != 0:
								empty = False
						if not empty:
							file2.write(str(memStart + (x * 8 * 4)).zfill(3) + ':\t', )
					else:
						file2.write(str(memStart + (x * 8 * 4)).zfill(3) + ':\t', )
					# if less than 8 elements, only print first z elements
					z = 0
					if len(mem) < 8:
						z = len(mem)
					else:
						z = 8
					for y in range(z):
						if not verbose:
							if empty:
								break
						file2.write(str(mem[y + x * 8]).replace('[', '').replace(']', ''), )
						if y < (z-1):
							file2.write('\t', )
						else:
							file2.write('\n')
				file2.write('\n')
				return
			def j():
				global pc, instr

				file2.write("=====================\n")
				imm = int(arg1Bin[instr] + arg2Bin[instr] + arg3Bin[instr] + shift[instr] + func[instr], 2)
				# bitshit immediate value 2
				imm <<= 2
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + '#' + str(imm) + '\n')

				pc = imm
				instr = (pc - 96)/4
				return
			def jr():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg1[instr] + '\n')

				destAddr = int(arg1[instr].replace('R', ''))
				pc = registers[destAddr]
				instr = (pc - 96)/4
				return
			def bne():
				global pc, instr

				file2.write("=====================\n")
				file2.write(
					'cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg1[instr] + ', #' + str(
						int(arg3[instr]) * 4) + '\n')

				imm = int(arg3Bin[instr] + shift[instr] + func[instr], 2)

				src1 = registers[int(arg1[instr].replace('R', ''))]
				src2 = registers[int(arg2[instr].replace('R', ''))]

				dest = imm
				if src1 != src2:
					pc = pc + 4 + (4 * dest)
					instr = (pc - 96) / 4
				else:
					pc = pc + 4
					instr = instr + 1
				return
			def blez():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg1[instr] + ', #' + str(int(arg3[instr]) * 4) + '\n')

				imm = int(arg3Bin[instr] + shift[instr] + func[instr], 2)

				src = registers[int(arg1[instr].replace('R', ''))]
				dest = imm
				if src <= 0:
					pc = pc + 4 + (4 * dest)
					instr = (pc - 96) / 4
				else:
					pc = pc + 4
					instr = instr + 1
				return
			def add():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[instr] + ', ' + arg2[instr] + '\n')

				src1Reg = int(arg1[instr].replace('R', ''))
				src2Reg = int(arg2[instr].replace('R', ''))
				destReg = int(arg3[instr].replace('R', ''))
				registers[destReg] = registers[src1Reg] + registers[src2Reg]
				pc = pc + 4
				instr = instr + 1
				return
			def addi():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg2[instr] + ', ' + arg1[instr] + ', #' + arg3[instr] + '\n')
				
				srcReg = int(arg1[instr].replace('R', ''))
				destReg = int(arg2[instr].replace('R', ''))
				imm = int(arg3[instr])
				registers[destReg] = registers[srcReg] + imm
				pc = pc + 4
				instr = instr + 1
				return
			def sub():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) +'\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[instr] + ', ' + arg2[instr] + '\n')

				destReg = int(arg3[instr].replace('R', ''))
				src1Reg = int(arg1[instr].replace('R', ''))
				src2Reg = int(arg2[instr].replace('R', ''))
				registers[destReg] = registers[src1Reg] - registers[src2Reg]
				pc = pc + 4
				instr = instr + 1
				return
			def sw():
				global pc, instr, mem

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) +'\t' + opcode[instr] + '\t' + arg2[instr] + ', ' + arg3[instr] + '(' + arg1[instr] + ')' + '\n')

				destAddress = int(arg3[instr].replace('R', ''))
				destAddress += registers[int(arg1[instr].replace('R', ''))]
				src = int(arg2[instr].replace('R', ''))
				# allocate memory if needed
				if len(mem) == 0:
					for x in range(((destAddress - memStart) / 4) + 8):
						mem.append(0)
				mem[(destAddress-memStart)/4] = int(registers[src])
				pc = pc + 4
				instr = instr + 1
				return
			def lw():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg2[instr] + ', ' + arg3[instr] + '(' + arg1[instr] + ')' + '\n')

				destReg = int(arg2[instr].replace('R', ''))
				srcAddress = int(arg3[instr].replace('R', ''))
				srcAddress += registers[int(arg1[instr].replace('R', ''))]
				registers[destReg] = mem[(srcAddress-memStart) / 4]
				pc = pc + 4
				instr = instr + 1
				return
			def sll():
				global pc, instr

				file2.write("=====================\n")
				shamt = int(shift[instr], 2)
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg2[instr] + ', #' + str(shamt) + '\n')

				destReg = int(arg3[instr].replace('R', ''))
				srcReg = int(arg2[instr].replace('R', ''))
				registers[destReg] = registers[srcReg] << shamt
				pc = pc + 4
				instr = instr + 1
				return
			def srl():
				global pc, instr

				file2.write("=====================\n")
				shamt = int(shift[instr], 2)
				file2.write(
					'cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg2[
						instr] + ', #' + str(shamt) + '\n')

				destReg = int(arg3[instr].replace('R', ''))
				srcReg = int(arg2[instr].replace('R', ''))
				registers[destReg] = registers[srcReg] >> shamt
				pc = pc + 4
				instr = instr + 1
				return
			def mul():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[instr] + ', ' + arg2[instr] + '\n')

				src1Reg = int(arg1[instr].replace('R', ''))
				src2Reg = int(arg2[instr].replace('R', ''))
				destReg = int(arg3[instr].replace('R', ''))
				registers[destReg] = registers[src1Reg] * registers[src2Reg]
				pc = pc + 4
				instr = instr + 1
				return
			def and_():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[instr] + ', ' + arg2[instr] + '\n')

				src1 = int(arg1Bin[instr], 2)
				src2 = int(arg2Bin[instr], 2)
				destReg = int(arg3[instr].replace('R', ''))
				registers[destReg] = registers[src1] & registers[src2]
				pc = pc + 4
				instr = instr + 1
				return
			def or_():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[instr] + ', ' + arg2[instr] + '\n')

				src1 = int(arg1Bin[instr], 2)
				src2 = int(arg2Bin[instr], 2)
				destReg = int(arg3[instr].replace('R', ''))
				registers[destReg] = registers[src1] | registers[src2]
				pc = pc + 4
				instr = instr + 1
				return
			def xor():
				global pc, instr

				file2.write("=====================\n")
				file2.write(
					'cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[
						instr] + ', ' + arg2[instr] + '\n')

				src1 = int(arg1Bin[instr], 2)
				src2 = int(arg2Bin[instr], 2)
				destReg = int(arg3[instr].replace('R', ''))
				registers[destReg] = registers[src1] ^ registers[src2]
				pc = pc + 4
				instr = instr + 1
				return
			def movz():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + opcode[instr] + '\t' + arg3[instr] + ', ' + arg1[instr] + ', ' + arg2[instr] + '\n')

				destReg = int(arg3[instr].replace('R', ''))
				cmpReg = int(arg2[instr].replace('R', ''))
				srcReg = int(arg1[instr].replace('R', ''))
				if registers[cmpReg] == 0:
					registers[destReg] = registers[srcReg]
				pc = pc + 4
				instr = instr + 1
				return
			def nop():
				global pc, instr

				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc) + '\t' + 'NOP' + '\n')

				pc = pc + 4
				instr = instr + 1
				return
			def breakInstr():
				file2.write("=====================\n")
				file2.write('cycle:' + str(c) + '\t' + str(pc)+ '\t' + 'BREAK' + '\n')
				return
			instruction={   'J' : j,
							'JR' : jr,
							'BNE' : bne,
							'BLEZ' : blez,
							'ADD' : add,
							'ADDI' : addi,
							'SUB' : sub,
							'SW' : sw,
							'LW' : lw,
							'SLL' : sll,
							'SRL' : srl,
							'MUL' : mul,
							'AND' : and_,
							'OR' : or_,
							'XOR' : xor,
							'MOVZ' : movz,
							'NOP' : nop
			}

			# main sim loop
			# while not break instruction, simulate through instructions
			# exit loop on break instruction
			while (1):
				if opcode[instr] == 'BREAK':
					breakInstr()
					stateWrite()
					if debug:
						statePrint()
					break
				if opcode[instr] == '':
					instr = instr + 1
					pc = pc + 4
				instruction[opcode[instr]]()
				stateWrite()
				if debug:
					statePrint()
				c = c + 1
			file2.close()
			return

for i in range(len(sys.argv)):
	if sys.argv[i] == "-i" and i < (len(sys.argv) - 1):
		inputFile = sys.argv[i + 1]
		if debug:
			print ('INPUT_FILE=' + inputFile)
	if sys.argv[i] == "-o" and i < (len(sys.argv) - 1):
		outputFile = sys.argv[i + 1]
		if debug:
			print ('OUTPUT_FILE=' + outputFile)
outputfiledis = outputFile + "_dis.txt"
outputfilesim = outputFile + "_sim.txt"
file = open(outputfiledis, "w")
file2 = open(outputfilesim, "w")

main().disassemble()
if debug:
	print ("\n\n|//////////////////////////////////////////////////DATA DUMP\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\|")
	print ("OPCODE:\t\t",)
	print (opcode)
	print ("ARG1:\t\t",)
	print (arg1)
	print ("ARG2:\t\t",)
	print (arg2)
	print ("ARG3:\t\t",)
	print (arg3)
	print ("OPCODE_BIN:\t",)
	print (opcodeBin)
	print ("ARG1_BIN:\t",)
	print (arg1Bin)
	print ("ARG2_BIN:\t",)
	print (arg2Bin)
	print ("ARG3_BIN:\t",)
	print (arg3Bin)
	print ("SHIFT: \t\t",)
	print (shift)
	print ("FUNC:\t\t",)
	print (func)
	print ("MEM:\t\t",)
	print (mem)
	print ("MEM_BIN:\t",)
	print (binMem)
	print ("|\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\|//////////////////////////////////////////////////////|\n\n")
pc = 96
main().simulate()

quit(0)
