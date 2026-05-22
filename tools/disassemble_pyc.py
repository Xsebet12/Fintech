import sys
import marshal
import dis
import binascii


def read_header(fp):
    fp.seek(0)
    magic = fp.read(4)
    flags = fp.read(4)
    rest = fp.read(8)
    return magic, flags, rest


def try_load_code(path):
    # Try common header sizes for different Python versions
    offsets = [16, 12, 8]
    last_exc = None
    for off in offsets:
        try:
            with open(path, 'rb') as f:
                f.seek(off)
                code = marshal.load(f)
                return code, off
        except Exception as e:
            last_exc = e
    raise last_exc


def recurse_dis(code_obj, prefix=''):
    print(f"{prefix}Code object: {code_obj.co_name} at {hex(id(code_obj))}")
    print(f"{prefix}  argcount: {getattr(code_obj, 'co_argcount', '?')}, vars: {code_obj.co_varnames}")
    print(f"{prefix}  names: {code_obj.co_names}")
    print(f"{prefix}  constants: {[type(c).__name__ for c in code_obj.co_consts]}")
    print(f"{prefix}--- Disassembly ---")
    for line in dis.Bytecode(code_obj):
        print(prefix + str(line))
    print()
    for const in code_obj.co_consts:
        if isinstance(const, type(code_obj)):
            recurse_dis(const, prefix + '  ')


def main():
    if len(sys.argv) < 2:
        print('Usage: python disassemble_pyc.py <path/to/file.pyc>')
        return
    path = sys.argv[1]
    try:
        with open(path, 'rb') as f:
            magic, flags, rest = read_header(f)
        print('Magic:', binascii.hexlify(magic))
        print('Flags:', int.from_bytes(flags, 'little'))
        print('Header tail (8 bytes):', binascii.hexlify(rest))
    except Exception as e:
        print('Error reading header:', e)
        return

    try:
        code_obj, used_offset = try_load_code(path)
        print('\nSuccessfully loaded code object using offset', used_offset)
        recurse_dis(code_obj)
    except Exception as e:
        print('Failed to load code object:', repr(e))


if __name__ == '__main__':
    main()
