#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import string

digits39 = string.digits + string.lowercase
digits62 = string.digits + string.lowercase + string.uppercase

def int2base(x, base):
	digs = digits39 if base == 39 else digits62
	if x < 0: sign = -1
	elif x==0: return '0'
	else: sign = 1
	x *= sign
	digits = []
	while x:
  		digits.append(digs[x % base])
	  	x /= base
	if sign < 0:
  		digits.append('-')
	digits.reverse()
	return ''.join(digits)


def unpack(p, a, c, k, e=None, d=None):
	''' unpack
	Unpacker for the popular Javascript compression algorithm.

	@param  p  template code
	@param  a  radix for variables in p
	@param  c  number of variables in p
	@param  k  list of c variable substitutions
	@param  e  not used
	@param  d  not used
	@return p  decompressed string
	'''
	# Paul Koppen, 2011
	for i in xrange(c-1,-1,-1):
		if k[i]:
			p = re.sub('\\b'+int2base(i,a)+'\\b', k[i], p)
	return p