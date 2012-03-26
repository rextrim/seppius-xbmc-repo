#-------------------------------------------------------------------------------
# Юppod decoder (for seasonvar.ru)
#-------------------------------------------------------------------------------

def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    hash1 = ["J", "y", "7", "4", "L", "k", "w", "p", "x", "v", "n", "s", "Q", "i", "U", "e", "Y", "2", "8", "N", "T", "9", "H", "M", "u", "="]
    hash2 = ["I", "c", "z", "0", "m", "o", "6", "G", "D", "l", "t", "W", "f", "R", "d", "Z", "3", "b", "X", "B", "5", "g", "a", "V", "1", "r"]

    #-- decode
    for i in range(0, len(hash1)):
        re1 = hash1[i]
        re2 = hash2[i]

        param = param.replace(re1, '___')
        param = param.replace(re2, re1)
        param = param.replace('___', re2)

    i = 0
    while i < len(param):
        j = 0
        while j < 4 and i+j < len(param):
            loc_3[j] = dec.find(param[i+j])
            j = j + 1

        loc_4[0] = (loc_3[0] << 2) + ((loc_3[1] & 48) >> 4);
        loc_4[1] = ((loc_3[1] & 15) << 4) + ((loc_3[2] & 60) >> 2);
        loc_4[2] = ((loc_3[2] & 3) << 6) + loc_3[3];

        j = 0
        while j < 3:
            if loc_3[j + 1] == 64:
                break

            loc_2 += unichr(loc_4[j])

            j = j + 1

        i = i + 4;

    return loc_2
