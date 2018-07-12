import pycurl
import cStringIO

cnt = 0

while (cnt >= 0):
     postdata = "accepted_privacy=true&birth_month=4&birth_year=1982&email=hacker%s@boinc.com&eula=13&nickname=hack+2&password=nothing&password2=nothing&session_id=&udid=355455060304265" % cnt
    buf = cStringIO.StringIO()
    cnt = cnt + 1


    c = pycurl.Curl()
    c.setopt(c.URL, 'http://v3api02.dev.pnap.ny.boinc/accounts/create_account/')
    c.setopt(c.POSTFIELDS, postdata )
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()
 
    print buf.getvalue()
    buf.close()

