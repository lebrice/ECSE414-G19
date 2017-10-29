import random as rd
import time
import ssl

random_function = ssl.RAND_bytes


def getSamplesLargeNumber(p, iterations):
    aValues = []
    while len(aValues) != iterations:
        sample = rd.randrange(2, p - 1)
        if sample not in aValues:
            aValues.append(sample)
    return aValues


def primeClaim(s, p, a, d):
    for i in range(s):
        power = pow(a, pow(2, i) * d, p)
        if power == p - 1:
            return True
        elif i == 0:
            if power == 1 or power == p - 1:
                return True
    return False


def genRandom(bits):
    rand = 0
    bytes = bits // 8 + 8
    while rand.bit_length() < bits:
        rand = int.from_bytes(random_function(bytes), byteorder='big')
    if not rand & 1:
        rand += 1
    return rand


def checkIfPrime(p, iterations=64):
    if p == 2:
        return True
    elif not p & 1:
        return False

    pow2 = p - 1
    s = 0
    while pow2 % 2 == 0:
        pow2 >>= 1
        s += 1
    d = (p - 1) // pow(2, s)

    # ensure enough values for 64 Miller-Rabin tests
    if p < iterations:
        iterations = p // 2
    # check if prime is larger than 2^15 - 1, as rd.sample needs ssize_t
    # ssize_t can store values of at least the range [-1 ... 2^15-1] per POSIX
    if p > pow(2, 15) - 1:
        aValues = getSamplesLargeNumber(p, iterations)
    else:
        aValues = rd.sample(range(2, p - 1), iterations)
    while aValues:
        if not primeClaim(s, p, aValues.pop(), d):
            return False
    return True


primes = {
    1: 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA237327FFFFFFFFFFFFFFFF}

a = time.time()
newPrime = genRandom(200)
while not checkIfPrime(newPrime):
    newPrime += 2
print(newPrime)
# print(checkIfPrime(primes[1]))
print(time.time() - a)