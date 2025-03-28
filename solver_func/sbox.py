#石川さんにいただいたコード
class Sbox:
	def __init__(self, sbox):
		self.sbox = sbox
		self.SBOXSIZE = self.SboxSize()

	def SboxSize(self):
		"""
		This function is used to calculate the size of a given sbox
		"""
		s = format(len(self.sbox), "b")
		# print(s)
		num_of_1_in_the_binary_experission_of_the_len_of_sbox = s.count("1")
		assert num_of_1_in_the_binary_experission_of_the_len_of_sbox == 1   #sboxのサイズが2の累乗になっているかのチェック
		return (len(s) - 1)

	def BitProduct(self, u, x):
		"""
		Return the value of the bitproduct function Pi_u(x)
		"""
		if (u & x) == u:
			return 1
		else:
			return 0

	def GetTruthTable(self, u):
		"""
		Retrieve the truth table of the boolean function Pi_u(y), where y = sbox(x)
		"""
		temp = [u for i in range(len(self.sbox))]
		table = list(map(self.BitProduct, temp, self.sbox))
		flag = 0
		if u==1:
			flag = 1
			# print(temp)
			# print(table)
			# for i in range(2**8):
			# 	print(format(self.sbox[i], "b"),end = " ,")
		return table, flag

	def ProcessTable(self, table, flag):
		"""
		Process the truth table to get the ANF of the boolean function
		we use table size to calculate the SBOXSIZE
		"""

		for i in range(0, self.SBOXSIZE):
			# if flag:
			# 	print("i = ",i)
			for j in range(0, 2**i):
				# if flag:
				# 	print("j = ", j)
				for k in range(0, 2**(self.SBOXSIZE - 1 - i)):
					# if flag:
					# 	print("k = ", k)
					table[k + 2**(self.SBOXSIZE - 1 - i) + j*(2**(self.SBOXSIZE - i))] =\
					table[k + 2**(self.SBOXSIZE - 1 - i) + j*(2**(self.SBOXSIZE - i))] ^\
					table[k + j*(2**(self.SBOXSIZE - i))]

	def CreatANF(self):
		"""
		Return the ANF of the sbox, moreover, this function also return the ANF of boolean function which
		is the product of some coordinates of the sbox output
		"""
		ANF = [[]for i in range(0, len(self.sbox))]
		for i in range(1, len(self.sbox)):
			table, flag = self.GetTruthTable(i) 
			self.ProcessTable(table,flag)
			sqr = []
			for j in range(0, len(self.sbox)):
				if table[j] != 0:
					sqr.append(j)
			ANF[i] = sqr
		return ANF

	def CreateDivisionTrails(self):
		"""
		Return all the division trails of a given sbox
		"""
		ANF = self.CreatANF()
		# print(ANF[3])
		# print(len(ANF))
		# for line in ANF:
		# 	print(len(line))
		# for i in range(8):
		# 	print(len(ANF[2**i]))
		INDP = []
	    # add zero vector into the division trails
		sqr = [0 for i in range(2 * self.SBOXSIZE)]
		# print(sqr)
		INDP.append(sqr)
		# start from the non-zero vector
		for i in range(1, len(self.sbox)):
			# print(i)
			sqn = []
			# start from the non-zero vector
			for j in range(1, len(self.sbox)):
				# print(ANF[j])
				flag = False
				for entry in ANF[j]:
					if (i | entry) == entry: 
						flag = True
						break
				if flag:
					sqn1 = []
					flag_add = True
					for t1 in sqn:
						if (t1 | j) == j:
							flag_add = False
							break
						elif (t1 | j) == t1:
							sqn1.append(t1)
					if flag_add:
						for t2 in sqn1:
							sqn.remove(t2)
						sqn.append(j)
			for num in sqn:
				a = format(i, "0256b")
				b = format(num, "0256b")
				a = list(reversed(list(map(int, list(a)))))
				b = list(reversed(list(map(int, list(b)))))
				a = a[0:self.SBOXSIZE]
				b = b[0:self.SBOXSIZE]
				a.reverse()
				b.reverse()
				INDP.append((a+b))
		return INDP

	def PrintfDivisionTrails(self, filename):
		"""
		Write all division trails of an sbox into a file
		"""
		INDP = self.CreateDivisionTrails()
		fileobj = open(filename, "w")
		fileobj.write("Division Trails of sbox:\n")
		for l in INDP:
			fileobj.write(str(l) + "\n")
		fileobj.write("\n")
		fileobj.close()


if __name__ == "__main__":

	# PRESENT Sbox
	# cipher = "PRESENT"

	cipher = "PRESENT"
	sbox_pre = [0xc, 0x5, 0x6, 0xb, 0x9, 0x0, 0xa, 0xd, 0x3, 0xe, 0xf, 0x8, 0x4, 0x7, 0x1, 0x2]

	cipher = "Orthros"
	sbox_ort = [0x1,0x0,0x2,0x4,0x3,0x8,0x6,0xd,0x9,0xa,0xb,0xe,0xf,0xc,0x7,0x5]

	sbox_aes = [0x63,  0x7c,   0x77,   0x7b,   0xf2,   0x6b,   0x6f,   0xc5,   0x30,   0x01,   0x67,   0x2b,   0xfe,   0xd7,   0xab,   0x76,
    0xca,   0x82,   0xc9,   0x7d,   0xfa,   0x59,   0x47,   0xf0,   0xad,   0xd4,   0xa2,   0xaf,   0x9c,   0xa4,   0x72,   0xc0,
    0xb7,   0xfd,   0x93,   0x26,   0x36,   0x3f,   0xf7,   0xcc,   0x34,   0xa5,   0xe5,   0xf1,   0x71,   0xd8,   0x31,   0x15,
    0x04,   0xc7,   0x23,   0xc3,   0x18,   0x96,   0x05,   0x9a,   0x07,   0x12,   0x80,   0xe2,   0xeb,   0x27,   0xb2,   0x75,
    0x09,   0x83,   0x2c,   0x1a,   0x1b,   0x6e,   0x5a,   0xa0,   0x52,   0x3b,   0xd6,   0xb3,   0x29,   0xe3,   0x2f,   0x84,
    0x53,   0xd1,   0x00,   0xed,   0x20,   0xfc,   0xb1,   0x5b,   0x6a,   0xcb,   0xbe,   0x39,   0x4a,   0x4c,   0x58,   0xcf,
    0xd0,   0xef,   0xaa,   0xfb,   0x43,   0x4d,   0x33,   0x85,   0x45,   0xf9,   0x02,   0x7f,   0x50,   0x3c,   0x9f,   0xa8,
    0x51,   0xa3,   0x40,   0x8f,   0x92,   0x9d,   0x38,   0xf5,   0xbc,   0xb6,   0xda,   0x21,   0x10,   0xff,   0xf3,   0xd2,
    0xcd,   0x0c,   0x13,   0xec,   0x5f,   0x97,   0x44,   0x17,   0xc4,   0xa7,   0x7e,   0x3d,   0x64,   0x5d,   0x19,   0x73,
    0x60,   0x81,   0x4f,   0xdc,   0x22,   0x2a,   0x90,   0x88,   0x46,   0xee,   0xb8,   0x14,   0xde,   0x5e,   0x0b,   0xdb,
    0xe0,   0x32,   0x3a,   0x0a,   0x49,   0x06,   0x24,   0x5c,   0xc2,   0xd3,   0xac,   0x62,   0x91,   0x95,   0xe4,   0x79,
    0xe7,   0xc8,   0x37,   0x6d,   0x8d,   0xd5,   0x4e,   0xa9,   0x6c,   0x56,   0xf4,   0xea,   0x65,   0x7a,   0xae,   0x08,
    0xba,   0x78,   0x25,   0x2e,   0x1c,   0xa6,   0xb4,   0xc6,   0xe8,   0xdd,   0x74,   0x1f,   0x4b,   0xbd,   0x8b,   0x8a,
    0x70,   0x3e,   0xb5,   0x66,   0x48,   0x03,   0xf6,   0x0e,   0x61,   0x35,   0x57,   0xb9,   0x86,   0xc1,   0x1d,   0x9e,
    0xe1,   0xf8,   0x98,   0x11,   0x69,   0xd9,   0x8e,   0x94,   0x9b,   0x1e,   0x87,   0xe9,   0xce,   0x55,   0x28,   0xdf,
    0x8c,   0xa1,   0x89,   0x0d,   0xbf,   0xe6,   0x42,   0x68,   0x41,   0x99,   0x2d,   0x0f,   0xb0,   0x54,   0xbb,   0x16]

	pre = Sbox(sbox_pre)
	filename = "solver_func/sbox_integral/out_table_ref/PRESENT.txt"
	pre.PrintfDivisionTrails(filename)

	# ort = Sbox(sbox_ort)
	# filename = "solver_func/sbox_integral/out_table_ref/Orthros.txt"
	# ort.PrintfDivisionTrails(filename)

	# aes = Sbox(sbox_aes)
	# filename = "solver_func/sbox_integral/out_table_ref/AES.txt"
	# aes.PrintfDivisionTrails(filename)
