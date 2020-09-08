import math


def rotate_left(n, k, n_bits):
    k %= n_bits

    return ((n << k) | (n >> (n_bits - k))) & ((1 << n_bits) - 1)


def rotate_right(n, k, n_bits):
    k %= n_bits

    return (n >> k) | ((n & ((1 << k) - 1)) << (n_bits - k))


def RC5_key_generator(num_k, w=64, r=18, b=128):
    # impart cheia in octeti

    k = []

    for i in range(b):
        k.append(num_k & 255)

        num_k >>= 8

    # generez constantele P si Q

    e = 2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274
    phi = 1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374

    P = ((e - 2) * ((1 << w) - 0))
    Q = ((phi - 1) * ((1 << w) - 0))

    auxp1 = math.floor(P)
    auxp2 = math.ceil(P)

    if auxp1 & 1 == 0:
        P = auxp2
    else:
        P = auxp1

    auxq1 = math.floor(Q)
    auxq2 = math.ceil(Q)

    if auxq1 & 1 == 0:
        Q = auxq2
    else:
        Q = auxq1

    # generez restul cheii

    L = [0 for i in range(b)]
    u = w // 8
    c = math.ceil(b / u)

    for i in range(b):
        L[i // u] = (L[i // u] << 8) + k[i]

    s = [P]

    for i in range(1, 2 * (r + 1)):
        s.append((s[i - 1] + Q) & ((1 << w) - 1))

    i = 0
    j = 0
    a = 0
    b = 0
    cnt = 0

    while cnt < 3 * max(c, 2 * (r + 1)):
        s[i] = rotate_left(s[i] + a + b, 3, w)
        a = s[i]

        L[j] = rotate_left(L[j] + a + b, a + b, w)
        b = L[j]

        i += 1
        j += 1
        i %= 2 * (r + 1)
        j %= c

        cnt += 1

    return s


def RC5_block_encryptor(block, s, w=64, r=18):  # receives INTEGER, returns INTEGER

    mod = 1 << w

    # sparg in cele doua bucati L si R

    R = block & (mod - 1)

    block >>= w

    L = block

    # execut algoritmul

    L += s[0]
    R += s[1]

    L %= mod
    R %= mod

    for i in range(1, r):
        L = rotate_left(L ^ R, R, w)
        L += s[2 * i]
        L %= mod

        R = rotate_left(L ^ R, L, w)
        R += s[2 * i + 1]
        R %= mod

    return (L << w) | R


def RC5_block_decryptor(block_encrypted, s, w=64, r=18):  # receives INTEGER, returns INTEGER

    mod = 1 << w

    R = block_encrypted & (mod - 1)

    block_encrypted >>= w

    L = block_encrypted

    for i in range(r - 1, 0, -1):
        R = rotate_right((R - s[2 * i + 1]) % mod, L, w) ^ L

        L = rotate_right((L - s[2 * i]) % mod, R, w) ^ R

    R -= s[1]
    L -= s[0]

    R %= mod
    L %= mod

    return (L << w) | R
