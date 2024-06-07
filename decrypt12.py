s = "Gd`4&&&"


def decrypt12(text):
	d = ""
	for ch in text:
		d += chr(ord(ch)+12)
	return d	


print(decrypt12(s))	