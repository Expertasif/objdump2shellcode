#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2017 Milton Valencia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Script name     : objdump2shellcode.py
# Version         : 3.2
# Created date    : 5/27/2017
# Last update     : 9/5/2017
# Author          : wetw0rk
# Architecture	  : x86, and x86-x64
# Python version  : 3.5 (works on 2.7 aswell)
# Designed OS     : Linux (preferably a penetration testing distro)
# Dependencies    : none, besides objdump; installed on most os's
# Description     : This is 1000000000 times easier than manually
#                   copying/pasting custom shellcode generated by
#                   objdump. I noticed Black Arch is hosting this
#                   this tool aswell :D so I added more features!
#		    Note: Sometimes 64bit binarys can be finiky I
#		    recommend reading from stdin if you encounter
#		    any issues when dumping, as formatting has not
#		    failed me yet.
#

import os, sys, subprocess, argparse

instructions	= []
no_junk		= []
op_line		= []

# for our info dump function
lang = {
	"python"	: "#",
	"perl"		: "#",
	"c"		: "//"
}

class colors:

	def __init__(self):
		pass

	RED	= '\033[31m'
	END	= '\033[0m'
	BOLD	= '\033[1m'
	YELLOW	= '\033[93m'

def format_list():

	supported_norm = [
	'hex',
	'nasm',
	'c',
	'perl',
	'python',
	'bash',
	'csharp',
	'dword',
	'java',
	'num',
	'powershell',
	'ruby',
	]

	supported_comment = [
	'python',
	'c',
	'perl',
	]

	sn = "\t"
	sc = "\t"

	# normal dumpable languages
	print("Normal output:")
	for i in range(len(supported_norm)):
		sn += "{:s}, ".format(supported_norm[i])

	print(sn[:len(sn)-2])

	# comment supported languages
	print("Comment dump:")
	for i in range(len(supported_comment)):
		sc += "{:s}, ".format(supported_comment[i])

	print(sc[:len(sc)-2])

	print("No badchar detection support:\n\tcsharp, dword, num, powershell, java, nasm")

class format_dump():

	def __init__(self, ops, mode, var_name, badchars):
		self.ops	= ops
		self.mode	= mode
		self.var_name	= var_name
		self.badchars	= badchars

	def character_analysis(self, num, results):

		global op_line

		spotted = []

		if self.badchars != None:
			# if we have bad characters split
			# them in order spot them later.
			sep_chars = self.badchars.split(",")

			for i in range(len(sep_chars)):
				if sep_chars[i] in self.ops:
					spotted += ("{:s}".format(sep_chars[i])),

		print("Payload size: {:d} bytes".format(int(len(self.ops)/4)))

		# here we begin to spot the badchars should we find one
		# we will replace it with a bold and red opcode, simply
		# making identification an ease
		indiv_byte = len(spotted)-1     	# loop counter for bad characters

		# when debugging shellcode we want to splice differently
		if num == 1337:
			for i in range(len(op_line)):
				while indiv_byte > -1:
					if spotted[indiv_byte] in op_line[i]:
						highlight_byte = "{:s}{:s}{:s}{:s}".format(colors.BOLD, colors.RED, spotted[indiv_byte], colors.END).lstrip()
						op_line[i] = op_line[i].replace(spotted[indiv_byte], highlight_byte)
						results += i,
					indiv_byte -= 1

				indiv_byte = len(spotted)-1	# reset the loop counter
		else:
			# tactical dumping begins here
			splits = [self.ops[x:x+num] for x in range(0,len(self.ops),num)]
			for i in range(len(splits)):
				while indiv_byte > -1:
					if spotted[indiv_byte] in splits[i]:
						highlight_byte = "{:s}{:s}{:s}{:s}".format(colors.BOLD, colors.RED, spotted[indiv_byte], colors.END)
						splits[i] = splits[i].replace(spotted[indiv_byte], highlight_byte)
					indiv_byte -= 1

				indiv_byte = len(spotted)-1	# reset the loop counter

			for i in range(len(splits)):
				results += splits[i],

		return

	def informational_dump(self):

		global no_junk, instructions, op_line, done

		num	= 1337
		results = []
		done	= []

		if self.mode == "python":
			for i in range(len(no_junk)):
				op_line += "\\x{:s}".format(no_junk[i].replace(" ", "\\x")),
			self.character_analysis(num, results)
			for i in range(len(op_line)):
				if i in results:
					done += ("{:s} += \"{:s}\"{:s}{:s}\t{:s} {:s} <== WARNING BADCHARS{:s}".format(
						self.var_name,
						op_line[i],
						colors.BOLD,
						colors.YELLOW,
						lang[self.mode],
						instructions[i],
						colors.END)
					).expandtabs(62),
				else:
					done += ("{:s} += \"{:s}\"\t{:s} {:s}".format(
						self.var_name,
						op_line[i],
						lang[self.mode],
						instructions[i])
					),

			print('{:s} = ""'.format(self.var_name))
			for i in range(len(done)):
				print("{:s}".format(done[i]).expandtabs(40))

		if self.mode == "perl":
			for i in range(len(no_junk)):
				op_line += "\\x{:s}".format(no_junk[i].replace(" ", "\\x")),
			self.character_analysis(num, results)
			for i in range(len(op_line)):

				if i == (len(op_line)-1) and i in results:
					done += ("\"{:s}\"{:s};{:s}\t{:s} {:s} <== WARNING BADCHARS{:s}".format(
						op_line[i],
						colors.BOLD,
						colors.YELLOW,
						lang[self.mode],
						instructions[i],
						colors.END)
					).expandtabs(62),

				elif i == (len(op_line)-1):
					done += ("\"{:s}\";\t{:s} {:s}".format(
						op_line[i],
						lang[self.mode],
						instructions[i])
					),

				elif i in results:
					done += ("\"{:s}\"{:s}.{:s}\t{:s} {:s} <== WARNING BADCHARS{:s}".format(
						op_line[i],
						colors.BOLD,
						colors.YELLOW,
						lang[self.mode],
						instructions[i],
						colors.END)
					).expandtabs(62),
				else:
					done += ("\"{:s}\".\t{:s} {:s}".format(
						op_line[i],
						lang[self.mode],
						instructions[i])
					),

			print('{:s} = ""'.format(self.var_name))
			for i in range(len(done)):
				print("{:s}".format(done[i]).expandtabs(40))


		if self.mode == "c":
			for i in range(len(no_junk)):
				op_line += "\\x{:s}".format(no_junk[i].replace(" ", "\\x")),

			self.character_analysis(num, results)
			for i in range(len(op_line)):

				if i == (len(op_line)-1) and i in results:
					done += ("\"{:s}\"{:s};{:s}\t{:s} {:s} <== WARNING BADCHARS{:s}".format(
						op_line[i],
						colors.BOLD,
						colors.YELLOW,
						lang[self.mode],
						instructions[i],
						colors.END)
					).expandtabs(62),

				elif i == (len(op_line)-1):
					done += ("\"{:s}\";\t{:s} {:s}".format(
						op_line[i],
						lang[self.mode],
						instructions[i])
					),

				elif i in results:
					done += ("\"{:s}\"{:s}{:s}\t{:s} {:s} <== WARNING BADCHARS{:s}".format(
						op_line[i],
						colors.BOLD,
						colors.YELLOW,
						lang[self.mode],
						instructions[i],
						colors.END)
					).expandtabs(62),
				else:
					done += ("\"{:s}\"\t{:s} {:s}".format(
						op_line[i],
						lang[self.mode],
						instructions[i])
					),

			print('unsigned char {:s}[] = ""'.format(self.var_name))
			for i in range(len(done)):
				print("{:s}".format(done[i]).expandtabs(40))



	def tactical_dump(self):

		results = []

		if self.mode == "python":
			num = 60
			self.character_analysis(num, results)
			print('{:s} = ""'.format(self.var_name))
			for i in range(len(results)):
				print("{:s} += \"{:s}\"".format(self.var_name, results[i]))

		if self.mode == "c":
			num = 60
			self.character_analysis(num, results)
			print("unsigned char {:s}[] = ".format(self.var_name))
			for i in range(len(results)):
				if i == (len(results) -1):
					print("\"{:s}\";".format(results[i]))
				else:
					print("\"{:s}\"".format(results[i]))

		if self.mode == "bash":
			num = 56
			self.character_analysis(num, results)
			for i in range(len(results)):
				if i == (len(results) -1):
					print("$'{:s}'".format(results[i]))
				else:
					print("$'{:s}'\\".format(results[i]))

		if self.mode == "ruby":
			num = 56
			self.character_analysis(num, results)
			print("{:s} = ".format(self.var_name))
			for i in range(len(results)):
				if i == (len(results) -1):
					print("\"{:s}\"".format(results[i]))
				else:
					print("\"{:s}\" +".format(results[i]))

		if self.mode == "hex":
			op	= []
			num	= 8
			asm_raw = ""
			self.character_analysis(num, results)
			for i in range(len(results)):
				op += results[i].split("\\x")
			for i in range(len(op)):
				if op[i] == '':
					pass
				else:
					asm_raw += "{:s}".format(op[i])

			print(asm_raw)

		if self.mode == "perl":
			num = 60
			self.character_analysis(num, results)
			print("my ${:s} =".format(self.var_name))
			for i in range(len(results)):
				if i == (len(results) -1):
					print("\"{:s}\";".format(results[i]))
				else:
					print("\"{:s}\" .".format(results[i]))

		if self.mode == "csharp":
			print("byte[] {:s} = new byte[{:d}] {:s}".format(self.var_name, int(len(self.ops)/4), "{"))
			sharp = ""
			asm_ops = self.ops.split("\\x")
			for i in range(len(asm_ops)):
				if asm_ops[i] == '':
					pass
				else:
					sharp += "0x{:s},".format(asm_ops[i])
			split = [sharp[x:x+75] for x in range(0,len(sharp),75)]
			for i in range(len(split)):
				snip = len(split[i]) - 1
				if i == (len(split)-1):
					print(split[i][:snip] + " };")
				else:
					print(split[i])

		if self.mode == "dword":
			dword = ""
			dlist = []
			asm_ops = self.ops.split("\\x")
			for i in range(len(asm_ops)):
				if asm_ops[i] == '':
					pass
				else:
					dword += "{:s}".format(asm_ops[i])
			splits = [dword[x:x+8] for x in range(0,len(dword),8)]
			for i in range(len(splits)):
				s = splits[i]
				dlist += "0x" + "".join(map(str.__add__, s[-2::-2] ,s[-1::-2])),
			for i in range(int(len(dlist)/8+1)):
				print(", ".join(dlist[i*8:(i+1)*8]))

		if self.mode == "nasm":
			nasm = ""
			asm_ops = self.ops.split("\\x")
			for i in range(len(asm_ops)):
				if asm_ops[i] == '':
					pass
				else:
					nasm += "0x{:s},".format(asm_ops[i])
			split = [nasm[x:x+40] for x in range(0,len(nasm),40)]
			for i in range(len(split)):
				snip = len(split[i]) - 1
				print("db " + split[i][:snip])

		if self.mode == "num":
			raw_ops = ""
			asm_ops = self.ops.split("\\x")
			for i in range(len(asm_ops)):
				if asm_ops[i] == '':
					pass
				else:
					raw_ops += "0x%s, " % (asm_ops[i])
			split = [raw_ops[x:x+84] for x in range(0,len(raw_ops),84)]
			for i in range(len(split)):
				snip = len(split[i]) - 2
				if i == (len(split)-1):
					print(split[i][:snip])
				else:
					print(split[i])

		if self.mode == "powershell":
			raw_ops = ""
			asm_ops = self.ops.split("\\x")
			for i in range(len(asm_ops)):
				if asm_ops[i] == '':
					pass
				else:
					raw_ops += "0x%s," % (asm_ops[i])
			split = [raw_ops[x:x+50] for x in range(0,len(raw_ops),50)]
			for i in range(len(split)):
				snip = len(split[i]) - 1
				if i == 0:
					print("[Byte[]] {:s} = {:s}".format(self.var_name, split[i][:snip]))
				else:
					print("${:s} += {:s}".format(self.var_name, split[i][:snip]))

		if self.mode == "java":
			print("byte {:s}[] = new byte[]".format(self.var_name))
			print("{")
			javop = ""
			javlt = []
			asm_ops = self.ops.split("\\x")
			for i in range(len(asm_ops)):
				if asm_ops[i] == '':
					pass
				else:
					javop += "{:s}".format(asm_ops[i])
			splits = [javop[x:x+2] for x in range(0,len(javop),2)]
			for i in range(len(splits)):
				s = splits[i]
				javlt  += "(byte) 0x" + "".join(map(str.__add__, s[-2::-2] ,s[-1::-2])),
			for i in range(int(len(javlt)/8+1)):
				if i < (len(javlt)/8):
					print("\t" + ", ".join(javlt[i*8:(i+1)*8]) + ",")
				else:
					print("\t" + ", ".join(javlt[i*8:(i+1)*8]))
			print("};")

def objdump(dumpfile, mode, badchars, comment_code, var_name):

	global no_junk, instructions

	no_addr		= []
	opcodes		= []
	ops		= ""

	# detect if the file exists
	if os.path.isfile(dumpfile) is False:
		print("File non-existent!")
		sys.exit()

	# run objdump to disassemble the binary
	try:
		intel_dump = subprocess.Popen(['objdump', '-D', dumpfile, '-M', 'intel', '--insn-width=15'],
			stdout=subprocess.PIPE).communicate()[0]
	except:
		print("[-] error running command")
		sys.exit()

	# here we begin to clean the output accordingly; this
	# once a function however after consideration ideally
	# we want to reuse the dumping class for stdin, etc
	newline_split = intel_dump.decode().split("\n")

	for i in range(len(newline_split)):
		# split up every line by a [tab] and remove address
		addr_splt = newline_split[i].split('\t')[1:3]
		# get rid of blank lines
		if len(addr_splt) > 0:
			no_addr += addr_splt
		else:
			pass

	# separate opcodes and instructions
	list_len = len(no_addr)
	for i in range(list_len):
		if (i & 1) == 1:
			instructions += no_addr[i],
		else:
			opcodes += no_addr[i],

	# cut off the junk and format (\xde\xad\xbe\xef)
	for i in range(len(opcodes)):
		no_junk  += opcodes[i].rstrip(" "),
	for i in range(len(opcodes)):
		opcodes[i] = opcodes[i].rstrip(" ")
	for i in range(len(opcodes)):
		ops += "\\x%s" % opcodes[i].replace(" ", "\\x")

	# now we send it off for formatting
	if comment_code:
		format = format_dump(ops, mode, var_name, badchars)
		format.informational_dump()
	else:
		format = format_dump(ops, mode, var_name, badchars)
		format.tactical_dump()

def main():

	# handle command line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--dump",     help="binary to use for shellcode extraction (via objdump)")
	parser.add_argument("-s", "--stdin",    help="read ops from stdin (EX: echo \"\\xde\\xad\\xbe\\xef\" | objdump2shellcode -s -f python -b \"\\xbe\")", action="store_true")
	parser.add_argument("-f", "--format",   help="output format (use --list for a list)")
	parser.add_argument("-b", "--badchar",  help="seperate badchars like so \"\\x00,\\x0a\"")
	parser.add_argument("-c", "--comment",  help="comments the shellcode output", action="store_true")
	parser.add_argument("-v", "--varname",  required=False, help="alternative variable name")
	parser.add_argument("-l", "--list",     help="list all available formats", action="store_true")
	args = parser.parse_args()

	# assign arguments
	dumpfile	= args.dump
	mode		= args.format
	badchars	= args.badchar
	comment_code	= args.comment
	stdin		= args.stdin

	# if a list is requested print it
	if args.list == True:
		format_list()
		sys.exit()

	# default variable name if none given
	if args.varname == None:
		var_name = "buf"
	else:
		var_name = args.varname

	# pass to function (thank you @justsam, and greetz)
	if dumpfile != None:
		objdump(dumpfile, mode, badchars, comment_code, var_name)
	# if requested read from stdin
	elif args.stdin == True:
		for line in sys.stdin.readlines():
			ops = line.rstrip()
			format = format_dump(ops, mode, var_name, badchars)
			format.tactical_dump()
	else:
		print(parser.print_help())

if __name__ == '__main__':
	main()

