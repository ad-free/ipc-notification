# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re


def check_special_chars(char):
	if re.match("^[a-zA-Z0-9]*$", char):
		return True
	return False


def logger_format(message, func_name):
	log_format = {
		'message': message,
		'func_name': func_name
	}
	return log_format
