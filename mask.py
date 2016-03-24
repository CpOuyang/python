def encrypt(string=''):
    import hashlib
    import base64
    from operator import xor

    __key1 = 'PKMKey22856'
    __key2 = 'SekEy24110'

    h1 = hashlib.md5(__key1.encode()).hexdigest()
    h2 = hashlib.md5(__key2.encode()).hexdigest()
    h3 = hashlib.md5((h1 + h2).encode().upper()).hexdigest()
    h4 = hashlib.md5((h2 + h1).encode().upper()).hexdigest()
    h5 = hashlib.md5((h3 + h4).encode().upper()).hexdigest()
    h = (h5 + h4 + h3 + h2 + h1).upper()

    __oops = string.encode()
    ans = ''
    for i in range(len(__oops)):
        ans += chr(xor(__oops[i], ord(h[i])))
    return base64.b64encode((ans + '#').encode()).decode()


def decrypt(string=''):
    import base64
    import hashlib
    import re
    from operator import xor

    __key1 = 'PKMKey22856'
    __key2 = 'SekEy24110'

    h1 = hashlib.md5(__key1.encode()).hexdigest()
    h2 = hashlib.md5(__key2.encode()).hexdigest()
    h3 = hashlib.md5((h1 + h2).encode().upper()).hexdigest()
    h4 = hashlib.md5((h2 + h1).encode().upper()).hexdigest()
    h5 = hashlib.md5((h3 + h4).encode().upper()).hexdigest()
    h = (h5 + h4 + h3 + h2 + h1).upper()

    __oops = re.sub(r'(.*)(#)', r'\1', base64.b64decode(string).decode()).encode()
    ans = ''
    for i in range(len(__oops)):
        ans += chr(xor(__oops[i], ord(h[i])))
    return ans
