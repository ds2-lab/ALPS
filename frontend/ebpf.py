import struct
import os
import json

def update_policy(key, p1, p2):
    if p2 == 1:
        p2 *= 1000
    else:
        p2 = p2 * 1000
    key_bytes = struct.pack("I", key)
    p1_bytes = struct.pack("Q", p1)
    p2_bytes = struct.pack("Q", p2)


    key_str = str(key_bytes.hex())
    sliced_key = [key_str [i:i+2] for i in range(0, len(key_str), 2)]
    formatted_key = " ".join(sliced_key)

    p1_str = str(p1_bytes.hex())
    sliced_p1 = [p1_str [i:i+2] for i in range(0, len(p1_str), 2)]
    formatted_p1 = " ".join(sliced_p1)

    p2_str = str(p2_bytes.hex())
    sliced_p2 = [p2_str [i:i+2] for i in range(0, len(p2_str ), 2)]
    formatted_p2 = " ".join(sliced_p2)
    os.system("./bpftool map update id {} key hex {} value hex {} {}".format(168, formatted_key, formatted_p1, formatted_p2))

def read_execution(key):
    key_bytes = struct.pack("I", key)
    key_str = str(key_bytes.hex())
    sliced_key = [key_str [i:i+2] for i in range(0, len(key_str), 2)]
    formatted_key = " ".join(sliced_key)
    values = os.popen('./bpftool map lookup name execution_map key hex {}'.format(formatted_key)).read()
    data = json.loads(values)

    total = int(data["value"]["total"])
    amount = int(data["value"]["amount"])

    if amount == 0:
        return 20
    else:
        avg = total/(amount*1000)
        print(key, total, amount)
        return total/(amount*1000)