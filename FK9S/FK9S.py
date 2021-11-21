import base64
import curses
import json
import os
import re
import subprocess

#page record:
#ns pod

#define accepted keyboard charactor
letter_codes = [ord(ch) for ch in 'rqblLP'] + [258, 259, 10]
actions = ['Restart', 'Exit', 'Basic', 'Log','CLog','CPod'] + ['Down', 'Up', 'Enter']
actions_dict = dict(zip(letter_codes, actions))

#get terminal info
no_c, no_r = os.get_terminal_size()

#define init content
welcome_content = "Hello, welcome to beta0 FK9s tool, please choose a namespace and press \"Enter\" Button"
head0 = "+" * (no_c - 1) + '\n'
head = ["version: Beta1 "]
#head.append("Any suggestion please mail to sherlock.zhu@ericsson.com")
head.append("◢▆▅▄▃崩╰(〒皿〒)╯溃▃▄▅▇◣")
head.append(". ")
head.append("-" * (no_c - 1))

#define cmd dict
cmd_dict = {
    'init' : 'kubectl get ns',
    'pod' : 'kubectl get pod',
    'append1' : '|awk \'{a=substr($1,1,58);b=substr($3,1,9);printf("%-60s %-7s %-10s %-10s %-5s %-18s %-20s\\n",a,$2,b,$4,$5,$6,$7)}\'',
    'top' : 'kubectl top',
    'd_node' : 'kubectl describe node',
    'event' : 'kubectl get events',
    'log' : 'kubectl logs'
}

def get_user_action(keyboard):
    char = 'N'
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]

#run command
def os_run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    error_mes = 'Oops! seems some error occurd, please report below error code to sherlock.zhu@ericsson.com: \n'
    return result.stdout.decode() if result.returncode == 0 else (error_mes + base64.b32encode(result.args.encode('UTF-8')).decode() + '\n' + base64.b32encode(result.stdout).decode())

def cpu_cal(cpu_n):
    return int(cpu_n.strip('m')) if 'm' in cpu_n else int(cpu_n) * 1000

def mem_cal(mem_n):
    #Mem unit dict
    cal_dict = {
        'Ki': 1024,
        'Mi': 1024 ** 2,
        'Gi': 1024 ** 3,
        'K': 1000,
        'M': 1000 ** 2,
        'G': 1000 ** 3,
    } 
    mem_u = re.sub(r'\d', r'', mem_n)   
    return int(mem_n.strip(mem_u))  * cal_dict[mem_u] if mem_u else int(mem_n)

class WorkField:
    def __init__(self):
        self.row_hight = no_r - 7
        self.current_page = None
        self.current_firstline = 0
        self.current_endline = 0
        self.content = None
        self.current_row_no = 0
        self.normal_page = ['pod_basic', 'container_list', 'Log']
        self.reset()
    
    #initialization
    def reset(self):
        self.current_page = 'ns'
        self.current_row_no = 1
        self.content = os_run(cmd_dict['init']).split('\n')
        self.content.pop()
    
    #new page parameter initialization
    def page_init(self, fline, c_row):
        self.current_row_no = c_row
        self.current_firstline = fline
        self.current_endline = min(1 + self.row_hight, len(self.content))

    #change selected line
    def c_highlight(self, direct):
        if direct == 'Down':
            if self.current_row_no < len(self.content) - 1:
                self.current_row_no += 1  
                if self.current_row_no >= self.current_endline:
                    self.current_firstline += 1
                    self.current_endline += 1
            else: 
                self.current_row_no = 1
                self.current_firstline = 1
                self.current_endline = min(1 + self.row_hight, len(self.content))
        else:
            if self.current_row_no > 1:
                self.current_row_no -= 1
                if self.current_row_no < self.current_firstline:
                    self.current_firstline -= 1
                    self.current_endline -= 1
            else:
                self.current_row_no = len(self.content) - 1
                self.current_endline =  len(self.content)
                self.current_firstline = max(1, self.current_endline - self.row_hight)


    #functions to draw the window
    def draw(self, screen):
    #define print solution
        def cast(string, color_pair = curses.color_pair(0)):
            screen.addstr(string + '\n', color_pair)
        screen.erase()
        #reset cursor location
        screen.addstr(0, 0, head0)
        for i in head: cast(i)
        #firstly check display page then decide what to do
        if self.current_page == 'ns': 
            cast(welcome_content)
            for i in range(len(self.content)): cast(self.content[i], curses.color_pair(1)) if i == self.current_row_no else cast(self.content[i])
        if self.current_page == 'pod':
            #secondly check if content longer than screen high
            content_hight = len(self.content)
            cast(self.content[0])
            for i in range(self.current_firstline, self.current_endline): 
                if i == self.current_row_no: 
                    cast(self.content[i], curses.color_pair(1)) 
                elif i in issue_line or self.cpod == False: 
                    cast(self.content[i], curses.color_pair(2))
                else:
                    cast(self.content[i])
        if self.current_page in self.normal_page:
            #secondly check if content longer than screen high
            content_hight = len(self.content)
            cast(self.content[0])
            for i in range(self.current_firstline, self.current_endline): 
                if i == self.current_row_no: 
                    cast(self.content[i], curses.color_pair(1)) 
                else:
                    cast(self.content[i])


def main(stdscr):
    #define colour solution
    #0:black, 1:red, 2:green, 3:yellow, 4:blue, 5:magenta, 6:cyan, 7:white
    curses.init_pair(1, 2, 7)
    curses.init_pair(2, 6, 1)
    curses.use_default_colors()

    #define action function
    class ActResp:
        def __init__(self):
            self._ = None
        
        def init(self):
            return 'Init'
        def exit(self):
            return 'Exit'
        def up_down(self):
            if len(work_field.content) > 2:
                work_field.c_highlight(action)
                return 'Work'
            return 'Wait'
        def Enter(self):
            if work_field.current_page == 'ns':
                work_field.ns = work_field.content[work_field.current_row_no].split()[0]
                work_field.current_page = 'pod'
                cmd = cmd_dict['pod'] + ' -o wide -n ' + work_field.ns + cmd_dict['append1']
                output = os_run(cmd)
                work_field.content = output.split('\n')
                work_field.content.pop()
                work_field.content_cpod = [work_field.content[0],]
                work_field.page_init(1, 1)
                #check pod status
                global issue_line
                issue_line = []
                if len(work_field.content) > 2:
                    for i in range(1,len(work_field.content)):
                        pod_status = work_field.content[i].split()[1:3]
                        work_state = pod_status[0].split('/')
                        if pod_status[1] == 'Running' and work_state[0] == work_state[1]: continue    
                        if pod_status[1] != 'Completed': 
                            issue_line.append(i)
                            work_field.content_cpod.append(work_field.content[i])
                work_field.cpod = True
                return 'Work'
            if work_field.current_page == 'container_list':
                work_field.current_page = 'Log'
                current_con = work_field.content[work_field.current_row_no].split()[0]
                if current_con == 'all': current_con = '--all-containers'
                cmd = ' '.join([cmd_dict['log'], '-n', work_field.ns, work_field.current_pod, current_con])
                output = os_run(cmd).split('\n')
                output_e = list(filter(lambda x: 'warn' in x.lower() or 'err' in x.lower(), output))
                #here need to deal with long content, otherwise will lead curses hight not enough error
                work_field.content = ['--']
                work_field.content_clog = ['--']
                c_width = no_c - 1
                for i in output:
                    while len(i) > c_width:
                        content, i = i[:c_width], i[c_width:]
                        work_field.content.append(content)
                    work_field.content.append(i)
                for i in output_e:
                    while len(i) > c_width:
                        content, i = i[:c_width], i[c_width:]
                        work_field.content_clog.append(content)
                    work_field.content_clog.append(i)
                work_field.page_init(1, 1)
                return 'Work'             
            return 'Wait'
        def Basic(self):
            if work_field.current_page == 'pod':
                work_field.current_page = 'pod_basic'
                work_field.current_pod = work_field.content[work_field.current_row_no].split()[0]
                #get pod info
                cmd_pod = cmd_dict['pod'] + ' -o json -n ' + work_field.ns + ' ' + work_field.current_pod
                pod_info = json.loads(os_run(cmd_pod))
                #some pod don't have product-name, need pre-check
                if "ericsson.com/product-name" in pod_info["metadata"]["annotations"]:
                    pname = pod_info["metadata"]["annotations"]["ericsson.com/product-name"]
                else:
                    pname = 'None'
                #pod located worker
                location = pod_info["spec"]["nodeName"]
                #owner
                owner = pod_info["metadata"]["ownerReferences"][0]["kind"] + ': ' + pod_info["metadata"]["ownerReferences"][0]['name']
                #container
                con = [i['name'] for i in pod_info["spec"]["containers"]]
                if "initContainers" in pod_info["spec"].keys(): con += [i['name'] for i in pod_info["spec"]["initContainers"]]
                # resource used by top
                cmd_res_use = cmd_dict['top'] + ' pod -n '  + work_field.ns + ' ' + work_field.current_pod
                # resource requested by described in node
                cmd_res_all = cmd_dict['d_node'] + ' '  + location + ' | grep '+ current_pod
                res_use = os_run(cmd_res_use).split()
                res_all = os_run(cmd_res_all).split() 
                cpu_usa = '{:.2%}'.format(cpu_cal(res_use[4]) /  cpu_cal(res_all[4]))
                mem_usa = '{:.2%}'.format(mem_cal(res_use[5]) /  mem_cal(res_all[8]))
                cmd_events = cmd_dict['event']  + ' -n ' + work_field.ns + ' -o json '
                events = json.loads(os_run(cmd_events))['items']
                work_field.content = ['Pod Details']
                work_field.content.append('{:<14s}{}'.format('Name: ', work_field.current_pod))
                work_field.content.append('{:<14s}{}'.format('Pro Name: ', pname))
                work_field.content.append('{:<14s}{}'.format('Location: ', location))
                work_field.content.append('{:<14s}{}'.format('Owner: ', owner))
                #pop out container one by one since the second line without head
                work_field.content.append('{:<14s}{}'.format('Containers: ', con.pop()))
                for i in con: work_field.content.append(' ' * 14 + i)
                work_field.content.append('--')                
                work_field.content.append('              {:<15s}{:<15s}{:<15s}'.format('Total', 'Used', 'Usage'))
                work_field.content.append('CPU:          {:<15s}{:<15s}{:<15s}'.format(res_all[4], res_use[4], cpu_usa))
                work_field.content.append('MEM:          {:<15s}{:<15s}{:<15s}'.format(res_all[8], res_use[5], mem_usa))
                work_field.content.append('--')                
                work_field.content.append('Events:')
                #need to adpat message length to avoid long message out of curse window width
                work_field.content.append('{:<23s}{:<20s}{}'.format('LastTimestamp', 'Reason', 'Message'))                
                for i in events:
                    message_len = no_c - 44
                    if i['involvedObject']['name'] == work_field.current_pod:
                        if len(i['message']) <= message_len: 
                            work_field.content.append('{:<23s}{:<20s}{}'.format(i['lastTimestamp'], i['reason'], i['message']))
                        else:
                            content, i['message'] = i['message'][:message_len], i['message'][message_len:]
                            work_field.content.append('{:<23s}{:<20.18s}{}'.format(i['lastTimestamp'], i['reason'], content))
                            while len(i['message']) > message_len:
                                content, i['message'] = i['message'][:message_len], i['message'][message_len:]
                                work_field.content.append('{:<23s}{:<20s}{}'.format(' ', ' ', content))
                            work_field.content.append('{:<23s}{:<20s}{}'.format(' ', ' ', i['message']))
                #reset cursor selection info
                work_field.page_init(1, 1)
                return 'Work'
            return 'Wait'
        def Log(self):
            if work_field.current_page == 'pod':
                work_field.current_page = 'container_list'
                work_field.current_pod = work_field.content[work_field.current_row_no].split()[0]
                cmd_pod = cmd_dict['pod'] + ' -o json -n ' + work_field.ns + ' ' + work_field.current_pod
                pod_info = json.loads(os_run(cmd_pod))
                con = [i['name'] for i in pod_info["spec"]["containers"]]
                if "initContainers" in pod_info["spec"].keys(): con += [i['name'] for i in pod_info["spec"]["initContainers"]]
                work_field.content = ['Please select which container\'s log you want to check: ']
                for i in con: work_field.content.append(i)
                work_field.content.append('all')            
                work_field.page_init(1, 1)
                return 'Work'
            return 'Wait'
        def CLog(self):
            if work_field.current_page == 'Log':
                # with open('record.log','w+') as f:
                #     f.write('output\n')
                #     for i in work_field.content: f.write(i + '\n')
                #     f.write('output_e\n')
                #     for i in work_field.content_clog: f.write(i + '\n')
                work_field.content, work_field.content_clog = work_field.content_clog, work_field.content
                work_field.page_init(1, 1)
                return 'Work'
            return 'Wait'
        def CPod(self):
            if work_field.current_page == 'pod':
                work_field.cpod = not work_field.cpod
                work_field.content, work_field.content_cpod = work_field.content_cpod, work_field.content
                work_field.page_init(1, 1)
                return 'Work'
            return 'Wait'



    #define different process state
    def init():
        work_field.reset()
        return 'Work'

    def wait_key():
        global action
        action = get_user_action(stdscr)
        return resp_dict[action]()

    def work():
        work_field.draw(stdscr)
        return 'Wait'

    #process state collections
    state_actions = {
        'Init' : init,
        'Work' : work,
        'Wait' : wait_key
    }   
    
    #init the process
    work_field = WorkField()
    act_resp = ActResp()
    state = 'Init'
    
    #try action dict to void mutiple if in work function
    #define action dictionary
    resp_dict = {
        'Restart' : act_resp.init,
        'Exit' : act_resp.exit,
        'Up' : act_resp.up_down,
        'Down' : act_resp.up_down,
        'Enter': act_resp.Enter,
        'Basic': act_resp.Basic,
        'Log': act_resp.Log,
        'CLog': act_resp.CLog,
        'CPod': act_resp.CPod
    }

    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)