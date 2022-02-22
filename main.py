import pymysql
import pandas as pd
import sshtunnel
from sshtunnel import SSHTunnelForwarder
import os
import tkinter
import threading

tally_list = []
magnum_ip_list = ['0']
# VIP_ins = ['0001','0002','0003','0004','0005','0006','0007','0008','0009','0010','0011','0012','0013','0014','0015','0016',
#            '0017','0018','0019','0020','0021','0022','0023','0024','0025','0026','0027','0028','0029','0030','0031','0032',
#            '0033','0034','0035','0036']
VIP_ins = []
for i in range(1,37):
  input = '0'+'0'+str(i)
  VIP_ins.append(input)



def create_queries():
    global tally_list
    tally_list = []
    print(vip_name.get())
    for i in range(0, 36):
        raw_entry = '{"tally_3": ' + str(i + 73) + ', "tally_1": ' + str(i + 1) + ', "tally_2": ' + str(i + 37) + ', ' \
                                                                                                                  '"umd_pid":' + str(
            i + 1) + ', "tally_4": ' + str(i + 109) + ' }'
        vip_input = ' where name = ' + f"'{vip_name.get()}-SRC-{VIP_ins[i]}'" + ';'
        tally_list.append(f"update ports set properties='{raw_entry}'" + f"{vip_input}")
        # print(vip_input)
        # print((tally_list[i]))

###################### THIS FUNCTION WILL PREVENT UI FROM BECOMING UNRESPONSIVE WHEN IT'S TRYING TO ACCESS
# A SERVER THAT'S NOT ACCESSIBLE. THREADING LETS YOU RUN MULTIPLE PROCESSES (TKINTER, FUNCTION) AT THE
# SAME TIME ##################################

def pid_thread():
    th = threading.Thread(target=set_pids)
    th.start()


##### takes ip and
def set_pids():
    global tally_list

    magnum_ip = str(ip_address.get())
    result_display = tkinter.Label(text="Enter Magnum IP & VIP name", bg="#444941", fg="white", font=('Arial', 12))
    result_display.place(x=210, y=400, width=360, height=65)

    if len(ip_address.get()) == 0:
        result_display.config(text="ENTER MAGNUM IP")
        window.after(3000, result_display.destroy)
    elif len(vip_name.get()) == 0:
        result_display.config(text="ENTER VIP NAME")
        window.after(3000, result_display.destroy)
    else:
        result_display.destroy
        MySQL_hostname = 'MAGNUM' #MySQL Host
        sql_username = 'root'#Username
        sql_password = os.environ.get('sql_password') #Password
        sql_main_database = 'pantheos' #Database Name
        sql_port = 3306
        ssh_host = magnum_ip #SSH Host
        ssh_user = 'etdev' #SSH Username
        ssh_pass = 'pantheosdev' #SSH Username
        ssh_port = 22

        try:

            result_display.config(text="Trying to connect")
            server = SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_password=ssh_pass,
                    # ssh_pkey=mypkey,
                    remote_bind_address=('127.0.0.1', 3306))
            server.start()
            print(server.local_bind_port)  # show assigned local port

        except sshtunnel.BaseSSHTunnelForwarderError:
            result_display.config(text=f"No Connection; Please check IP/credentials", fg='#FF7272')
            window.after(5000, result_display.destroy)
        else:
            result_display.config(text=f"Connected to DB", fg='#C2F784')
            create_queries()
            conn = pymysql.connect(
                # host='127.0.0.1',
                  user=sql_username,
                    # passwd=sql_password,
                    db=sql_main_database,
                    port=server.local_bind_port
                                   )

            cursor = conn.cursor()  ###to execute update/insert commands, use cursor function

            for x in range(0, 36):
                sql = tally_list[x]
                # print("hello")
                # print(tally_list[x])
                cursor.execute(sql)

            ####### this is to confirm that the new VIP's properties have been updated ##########
            ####### by querying for VIP's SRC-0009 tally-3 state & confirming it's 81  ##########
            query = f"select properties from ports where name = '{vip_name.get()}-SRC-0009'"
            data = pd.read_sql_query(query, conn)
            conn.commit()
            conn.close()

            tally_list = []
            try:
                # print(data)
                # print(data["properties"])
                # print(data["properties"][0])
                column_data = str(data["properties"][0])
                # print(column_data[12])
                if column_data[12] == '8' and column_data[13] == '1':
                    result_display.config(text=f"Successfully updated all PIDs for {vip_name.get()}", fg="#C2F784")
                else:
                    result_display.config(text="Updated but with errors!", fg="#FF7272")
                window.after(5000, result_display.destroy)
            except IndexError:
                result_display.config(text=f"Error: {vip_name.get()} does not exist", fg="#FF7272")
            window.after(5000, result_display.destroy)

############# actual GUI #############
window = tkinter.Tk()
window.title("PID script tool")
window.minsize(width=800, height=600)
window.configure(bg='#01599d')

####### to set the icon of the application ##########
window.tk.call('wm', 'iconphoto', window._w, tkinter.PhotoImage(file='magnum.png'))
canvas = tkinter.Canvas(width=750, height=700, bg='#01599d',highlightthickness=0)

####### to set background image of the window ##########
img = tkinter.PhotoImage(file="MAGNUM-MV-PID-TOOL.png")
canvas.create_image(400, 300, image=img)
canvas.place(x=10, y=10)# canvas.grid(column=2,row=0, padx=10, pady=10)

####### to receive IP address from user ##########
ip_address = tkinter.Entry(font=12, justify='center')
ip_address.place(x=320, y=170, height=35, width=158)

vip_name = tkinter.Entry(font=('Arial', 12, 'bold'), justify='center')
vip_name.place(x=200, y=280, height=50 ,width=260)

#### BUTTON TO START ENTERING PIDS #####################################################
set_pid = tkinter.Button(text="    SET PIDS   ", height=3, font=13, bg="#e7d9ea", activebackground= "#01599d",
                         highlightthickness=0, command=pid_thread)
set_pid.place(x=560, y=280)
window.mainloop()

#################################################################################
# #
# def clear_vip_name():
# #     vip_name.delete(0, tkinter.END)
# #     vip_name.config(text="")

# def connection_test():
#     q = queue.Queue()
#     # threading.Thread(target=get_mem, args=("server01", q)).start()
#     # result = q.get()
#     th = threading.Thread(target=ping_test, args=(q,))
#     ip_address_display = tkinter.Label(text="WAIT!!!", bg="#444941", fg="white", font=('Arial', 12, 'italic'))
#     ip_address_display.place(x=320, y=180, width=200)
#     th.start()
#     result = q.get()
#     print(result)

# def ping_test(q):
#     global magnum_ip_list
#     # magnum_ip_list = []
#     ip_entered = first_octat.get() + '.' + second_octat.get() + '.' + third_octat.get() + '.' + fourth_octat.get()
#     hostname = ip_entered
#     response = os.popen(f"ping {hostname}").read()
#
#     if "Received = 4" in response:
#         ping = "UP Ping Successful"
#         magnum_ip_list[0] = ip_entered
#         print(magnum_ip_list)
#         print(ping)
#         ip_address_display = tkinter.Label(text="", bg="#444941", fg="white", font=('Arial', 12, 'italic'))
#         ip_address_display.place(x=320, y=180, width=200)
#         ip_address_display.config(text=ping)
#         return "good"
#     else:
#         ping = "DOWN Ping Unsuccessful"
#         print(ping)
#         ip_address_display = tkinter.Label(text="", bg="#444941", fg="white", font=('Arial', 12, 'italic'))
#         ip_address_display.place(x=320, y=180, width=200)
#         ip_address_display.config(text=ping)
#         return "bad"
#     q.put(response.read())