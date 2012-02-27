#-------------------------------------------------------------------------------
# Юppod decoder (for igru.net.ua)
#-------------------------------------------------------------------------------

def Decode(param):
    #-- define variables
    loc_3 = [0,0,0,0]
    loc_4 = [0,0,0]
    loc_2 = ''
    #-- define hash parameters for decoding
    dec = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
    hash1 = ["L", "y", "c", "X", "2", "M", "a", "l", "p", "5", "Q", "e", "R", "t", "Z", "Y", "9", "m", "d", "0", "s", "V", "b", "3", "7", "="]
    hash2 = ["i", "B", "v", "U", "H", "4", "D", "n", "k", "8", "x", "T", "u", "G", "w", "f", "N", "J", "6", "W", "1", "g", "z", "o", "I", "r"]

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
