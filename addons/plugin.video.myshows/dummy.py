__author__ = 'Admin'
import re ,json
x=r'Boston Legal 02-27 NTV.mkv'
def Debug(s):
    try:print s
    except: print s.encode('utf-8')

def filename2match(filename):
    results={'label':filename}
    urls=['(.+)s(\d+)e(\d+)', '(.+) (\d+)[x|-](\d+)']
    for file in urls:
        match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
        if match:
            results['showtitle'], results['season'], results['episode']=match[0]
            results['showtitle']=results['showtitle'].replace('.',' ').strip()
            Debug('[filename2match] '+str(results))
            return results
    urls=['(.+)(\d{4})\.(\d{2,4})\.(\d{2,4})']
    for file in urls:
        match=re.compile(file, re.I | re.IGNORECASE).findall(filename)
        if match:
            results['showtitle']=match[0][0].replace('.',' ').strip()
            results['date']='%s.%s.%s' % (match[0][3],match[0][2],match[0][1])
            Debug('[filename2match] '+str(results))
            return results

print filename2match(x)