from os import walk

f : list[str] = []
for (dirpath, dirnames, filenames) in walk("G:\\"):
    f.extend(filenames)
    break

files = []
for fp in f:
    if fp.find(".py") >= 0:
        files.append(fp)

print(fp)