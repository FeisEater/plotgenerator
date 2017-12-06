def safe_append(dict, key, value):
  if key not in dict:
    dict[key] = [value]
  else:
    dict[key].append(value)

def safe_extend(dict, key, list):
  if key not in dict:
    dict[key] = list
  else:
    dict[key].extend(list)

def dump_output(output):
  for msg in output:
    print(msg)
  del output[:]