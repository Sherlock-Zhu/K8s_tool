import base64
import curses
import json
import os
import re
import subprocess

# define accepted keyboard charactor
letter_codes = [ord(ch) for ch in 'bcCdDeEhlnpPqrsSWY'] + [258, 259, 10]
actions = ['basic', 'configmap', 'crd', 'deployment',
           'daemonset', 'secret', 'describe',
           'hpa', 'log', 'node', 'pod',
           'pvc', 'exit', 'restart', 'service',
           'statefulset', 'switch', 'yaml'
           ] + ['down', 'up', 'enter']
actions_dict = dict(zip(letter_codes, actions))

# get terminal info
no_c, no_r = os.get_terminal_size()

# define head content
welcome_content = ('Hello, welcome to beta0 FK9s tool, please choose a '
                   'namespace and press "Enter" Button')
heads = ('|version: Beta0.2' + '-' * (no_c - 72) +
         'Any question please mail to sherlock.zhu@ericsson.com|\n')
head1 = ('|' + welcome_content + ' ' * (no_c - 88) + '|\n' + '| (●\'◡\'●)ﾉ♥' +
         ' ' * (no_c - 13) + '|\n' + '|' + ' ' * (no_c - 3) + '|')
head23 = ('|<c>  configmap      <C>  crd            <d>  deployment     '
          '<D>  daemonset      <e>  secret         <h>  hpa            ' +
          ' ' * (no_c - 123) + '|\n' +
          '|<n>  node           <p>  pod            <P>  pvc            '
          '<s>  service        <S>  statefulset    ' +
          ' ' * (no_c - 103) + '|')
head_p = ('|<q>  quit           <r>  reset          <b>  basic          '
          '<l>  log            <E>  description    <Y>  Yaml           '
          '<W>  switch error   ' + ' ' * (no_c - 143) + '|')
head_s2 = ('|<q>  quit           <r>  reset          <E>  description    '
           '<Y>  Yaml           <W>  switch error   ' +
           ' ' * (no_c - 103) + '|')
head_n2 = ('|<q>  quit           <r>  reset          <E>  description    '
           '<Y>  Yaml           ' + ' ' * (no_c - 103) + '|')
head_l = ('|<q>  quit           <r>  reset          <W>  switch error   ' +
          ' ' * (no_c - 63) + '|')
head_n3 = ('|<q>  quit           <r>  reset          ' +
           ' ' * (no_c - 43) + '|')

# define cmd dict
cmd_dict = {
    'top': 'kubectl top',
    'log': 'kubectl logs',
    'des': 'kubectl describe',
    'get': 'kubectl get'
}
error_mes = ('Oops! seems some error occurd, please report below '
             'error code to sherlock.zhu@ericsson.com:')


def get_cmd(dict_key, content=None):
    return cmd_dict[dict_key] + ' ' \
           + content if content else cmd_dict[dict_key]


def get_user_action(keyboard):
    char = 'N'
    while char not in actions_dict:
        char = keyboard.getch()
    return actions_dict[char]


# run command
def os_run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, shell=True)
    if result.returncode == 0:
        return result.stdout.decode(), 0
    else:
        return (error_mes + '\n'
                + base64.b32encode(result.args.encode('UTF-8')).decode()
                + '\n' + base64.b32encode(result.stdout).decode() + '\n'), 1


def cpu_cal(cpu_n):
    return int(cpu_n.strip('m')) if 'm' in cpu_n else int(cpu_n) * 1000


def mem_cal(mem_n):
    # Mem unit dict
    cal_dict = {
        'Ki': 1024,
        'Mi': 1024 ** 2,
        'Gi': 1024 ** 3,
        'K': 1000,
        'M': 1000 ** 2,
        'G': 1000 ** 3,
    }
    mem_u = re.sub(r'\d', r'', mem_n)
    return int(mem_n.strip(mem_u)) * cal_dict[mem_u] if mem_u else int(mem_n)


def main(stdscr):
    # define colour solution
    # 0:black, 1:red, 2:green, 3:yellow, 4:blue, 5:magenta, 6:cyan, 7:white
    curses.use_default_colors()
    curses.init_pair(1, 2, 7)
    curses.init_pair(2, 6, 1)

    # define print function
    class workField:
        def __init__(self):
            self.row_hight = no_r - 7
            self.current_page = None
            self.current_firstline = 0
            self.current_endline = 0
            self.content = None
            self.current_row_no = 0
            self.page_state = ['pod', 'deployment', 'statefulset', 'daemonset',
                               'service', 'pvc', 'node']
            self.page_normal = ['pod_basic', 'container_list', 'log', 'error',
                                'configmap', 'secret', 'hpa', 'crd', 'crd_2',
                                'yaml', 'describe', 'ns']
            self.page_level_1 = ['ns']
            self.page_level_2 = ['pod', 'deployment', 'statefulset', 'node',
                                 'daemonset', 'service', 'configmap',
                                 'secret', 'hpa', 'pvc', 'crd', 'crd_2']
            self.page_level_3 = ['container_list', 'pod_basic', 'error',
                                 'yaml', 'describe', 'log']
            self.page_2_level_2 = self.page_level_3 + self.page_level_2
            self.reset()

        # initialization
        def reset(self):
            self.current_page = 'ns'
            self.current_row_no = 1
            self.content = os_run(get_cmd('get', 'ns'))[0].split('\n')
            self.content.pop()

        # new page parameter initialization
        def page_init(self, fline, c_row):
            self.current_row_no = c_row
            self.current_firstline = fline
            self.current_endline = min(1 + self.row_hight, len(self.content))

        # change selected line
        def c_highlight(self, direct):
            if direct == 'down':
                if self.current_row_no < len(self.content) - 1:
                    self.current_row_no += 1
                    if self.current_row_no >= self.current_endline:
                        self.current_firstline += 1
                        self.current_endline += 1
                else:
                    self.current_row_no = 1
                    self.current_firstline = 1
                    self.current_endline = min(1 + self.row_hight,
                                               len(self.content))
            else:
                if self.current_row_no > 1:
                    self.current_row_no -= 1
                    if self.current_row_no < self.current_firstline:
                        self.current_firstline -= 1
                        self.current_endline -= 1
                else:
                    self.current_row_no = len(self.content) - 1
                    self.current_endline = len(self.content)
                    self.current_firstline = max(1, self.current_endline
                                                 - self.row_hight)

        # functions to draw the window
        def draw(self, screen):
            # define print solution
            def cast(string, color_pair=curses.color_pair(0)):
                screen.addstr(string + '\n', color_pair)

            def draw_head(*head):
                # reset cursor location
                screen.addstr(0, 0, heads)
                for i in head:
                    cast(i)
                screen.addstr('|')
                screen.addstr(heade[0], curses.color_pair(1))
                screen.addstr(heade[1] + '|\n')

            def format_output(content):
                format_str = ''
                for i in resp_dict[self.current_page][2:]:
                    format_str += '{:<' + str(i) + '.' + str(i-1) + '}'
                return format_str.format(*[i.strip() for i in
                                         filter(None, content.split('  '))]
                                         [:resp_dict[self.current_page][1]])

            heade = [self.current_page,
                     '-' * (no_c - 3 - len(self.current_page))]
            screen.erase()
            # firstly check display page then decide what to do
            if self.current_page in self.page_level_1:
                draw_head(head1)
                for i in range(len(self.content)):
                    if i == self.current_row_no:
                        cast(self.content[i], curses.color_pair(1))
                    else:
                        cast(self.content[i])
            elif self.current_page in self.page_state:
                if self.current_page == 'pod':
                    draw_head(head23, head_p)
                else:
                    draw_head(head23, head_s2)
                if len(self.content) == 1:
                    cast(self.content[0])
                    return 0
                cast(format_output(self.content[0]))
                for i in range(self.current_firstline, self.current_endline):
                    if i == self.current_row_no:
                        cast(format_output(self.content[i]),
                             curses.color_pair(1))
                    elif (i in issue_line) and (self.cstate is True):
                        cast(format_output(self.content[i]),
                             curses.color_pair(2))
                    else:
                        cast(format_output(self.content[i]))
            elif self.current_page in self.page_normal:
                if self.current_page in self.page_level_2:
                    draw_head(head23, head_n2)
                elif self.current_page == 'log':
                    draw_head(head23, head_l)
                else:
                    draw_head(head23, head_n3)
                cast(self.content[0])
                for i in range(self.current_firstline, self.current_endline):
                    if i == self.current_row_no:
                        cast(self.content[i], curses.color_pair(1))
                    else:
                        cast(self.content[i])

    # define action function
    class ActResp:
        def __init__(self):
            self.command_r = 0

        def init(self):
            return 'init'

        def exit(self):
            return 'exit'

        def up_down(self):
            if len(work_field.content) > 2:
                work_field.c_highlight(action)
                return 'work'
            return 'wait'

        def enter(self):
            if work_field.current_page == 'ns':
                work_field.ns = (work_field.content
                                 [work_field.current_row_no].split()[0])
                work_field.current_page = 'pod'
                return self.pod()
            if work_field.current_page == 'container_list':
                work_field.current_page = 'log'
                current_con = (work_field.content
                               [work_field.current_row_no].split()[0])
                if current_con == 'all':
                    current_con = '--all-containers'
                cmd = ' '.join([get_cmd('log'), '-n', work_field.ns,
                               work_field.current_pod, current_con])
                output = os_run(cmd)[0].split('\n')
                output_e = list(filter(lambda x: 'warn' in x.lower()
                                or 'err' in x.lower(), output))
                # here need to deal with long content
                # otherwise will lead curses hight not enough error
                work_field.content = ['--']
                work_field.content_c = ['--']
                c_width = no_c - 1
                for i in output:
                    while len(i) > c_width:
                        content, i = i[:c_width], i[c_width:]
                        work_field.content.append(content)
                    work_field.content.append(i)
                for i in output_e:
                    while len(i) > c_width:
                        content, i = i[:c_width], i[c_width:]
                        work_field.content_c.append(content)
                    work_field.content_c.append(i)
                work_field.page_init(1, 1)
                return 'work'
            if work_field.current_page == 'crd':
                work_field.current_page = 'crd_2'
                crd = work_field.content[work_field.current_row_no].split()[0]
                cmd = ' '.join([get_cmd('get', crd), '-n', work_field.ns])
                work_field.content = os_run(cmd)[0].split('\n')
                work_field.content.pop()
                work_field.page_init(1, 1)
                return 'work'
            return 'wait'

        def basic(self):
            if work_field.current_page == 'pod':
                work_field.current_page = 'pod_basic'
                work_field.current_pod = (work_field.content
                                          [work_field.current_row_no]
                                          .split()[0])
                # get pod info
                cmd_pod = ' '.join([get_cmd('get', 'pod'), '-o json -n',
                                   work_field.ns, work_field.current_pod])
                pod_info = json.loads(os_run(cmd_pod)[0])
                # some pod don't have product-name, need pre-check
                if ("ericsson.com/product-name" in
                   pod_info["metadata"]["annotations"]):
                    pname = (pod_info["metadata"]["annotations"]
                             ["ericsson.com/product-name"])
                else:
                    pname = 'None'
                # pod located worker
                location = pod_info["spec"]["nodeName"]
                # owner
                owner = (pod_info["metadata"]["ownerReferences"][0]["kind"]
                         + ': '
                         + pod_info["metadata"]["ownerReferences"][0]['name'])
                # container
                con = [i['name'] for i in pod_info["spec"]["containers"]]
                if "initContainers" in pod_info["spec"].keys():
                    con += [i['name'] for i in
                            pod_info["spec"]["initContainers"]]
                # resource used by top
                cmd_res_use = ' '.join([get_cmd('top'), 'pod -n',
                                       work_field.ns, work_field.current_pod])
                # resource requested by described in node
                cmd_res_all = ' '.join([get_cmd('des', 'node'), location,
                                       '| grep', work_field.current_pod])
                res_use_t, res_use_r = os_run(cmd_res_use)
                res_all_t, res_all_r = os_run(cmd_res_all)
                cpu_usa = mem_usa = 'n/a'
                if res_use_r == 1 or res_all_r == 1:
                    res_use = res_all = ('n/a ' * 9).split()
                else:
                    res_use = res_use_t.split()
                    res_all = res_all_t.split()
                    if cpu_cal(res_all[4]) != 0:
                        cpu_usa = '{:.2%}'.format(cpu_cal(res_use[4]) /
                                                  cpu_cal(res_all[4]))
                    if mem_cal(res_all[8]) != 0:
                        mem_usa = '{:.2%}'.format(mem_cal(res_use[5]) /
                                                  mem_cal(res_all[8]))
                cmd_events = ' '.join([get_cmd('get', 'event'), '-n',
                                      work_field.ns, '-o json'])
                events = json.loads(os_run(cmd_events)[0])['items']
                work_field.content = ['Pod Details']
                work_field.content.append(
                    '{:<14s}{}'.format('Name: ', work_field.current_pod))
                work_field.content.append(
                    '{:<14s}{}'.format('Pro Name: ', pname))
                work_field.content.append(
                    '{:<14s}{}'.format('Location: ', location))
                work_field.content.append('{:<14s}{}'.format('Owner: ', owner))
                # pop out container one by one
                # since the second line without head
                work_field.content.append(
                    '{:<14s}{}'.format('Containers: ', con.pop()))
                for i in con:
                    work_field.content.append(' ' * 14 + i)
                work_field.content.append('--')
                work_field.content.append(
                    '              {:<15s}{:<15s}{:<15s}'.format(
                        'Total', 'Used', 'Usage'))
                work_field.content.append(
                    'CPU:          {:<15s}{:<15s}{:<15s}'.format(
                        res_all[4], res_use[4], cpu_usa))
                work_field.content.append(
                    'MEM:          {:<15s}{:<15s}{:<15s}'.format(
                        res_all[8], res_use[5], mem_usa))
                work_field.content.append('--')
                work_field.content.append('Events:')
                # need to adpat message length to avoid \
                # long message out of curse window width
                work_field.content.append('{:<23s}{:<20s}{}'.format(
                    'LastTimestamp', 'Reason', 'Message'))
                for i in events:
                    message_len = no_c - 44
                    if i['involvedObject']['name'] == work_field.current_pod:
                        if len(i['message']) <= message_len:
                            work_field.content.append(
                                '{:<23s}{:<20s}{}'.format(
                                    i['lastTimestamp'], i['reason'],
                                    i['message']))
                        else:
                            content = i['message'][:message_len]
                            i['message'] = i['message'][message_len:]
                            work_field.content.append(
                                '{:<23s}{:<20.18s}{}'.format(
                                    i['lastTimestamp'], i['reason'], content))
                            while len(i['message']) > message_len:
                                content = i['message'][:message_len]
                                i['message'] = i['message'][message_len:]
                                work_field.content.append(
                                    '{:<23s}{:<20s}{}'.format(
                                        ' ', ' ', content))
                            work_field.content.append(
                                '{:<23s}{:<20s}{}'.format(
                                    ' ', ' ', i['message']))
                # reset cursor selection info
                work_field.page_init(1, 1)
                return 'work'
            return 'wait'

        def log(self):
            if work_field.current_page == 'pod':
                work_field.current_page = 'container_list'
                work_field.current_pod = \
                    work_field.content[work_field.current_row_no].split()[0]
                cmd_pod = ' '.join([get_cmd('get', 'pod'), '-o json -n',
                                   work_field.ns, work_field.current_pod])
                pod_info = json.loads(os_run(cmd_pod)[0])
                con = [i['name'] for i in pod_info["spec"]["containers"]]
                if "initContainers" in pod_info["spec"].keys():
                    con += [i['name'] for i
                            in pod_info["spec"]["initContainers"]]
                work_field.content = ['Please select which container\'s'
                                      'log you want to check: ']
                for i in con:
                    work_field.content.append(i)
                work_field.content.append('all')
                work_field.page_init(1, 1)
                return 'work'
            return 'wait'

        def switch_state(self):
            if work_field.current_page in ['log'] + work_field.page_state:
                work_field.cstate = not work_field.cstate
                work_field.content, work_field.content_c = (
                    work_field.content_c, work_field.content)
                work_field.page_init(1, 1)
                return 'work'
            return 'wait'

        # level2 page without state
        def normal_page_level2(self, item, wide_lo):
            if work_field.current_page in work_field.page_2_level_2:
                work_field.current_page = item
                cmd = ' '.join([get_cmd('get', item), wide_lo, work_field.ns])
                output, self.command_r = os_run(cmd)
                work_field.content = output.split('\n')
                work_field.content.pop()
                work_field.page_init(1, 1)
                return 'work'
            return 'wait'

        # level2 page with state
        def state_page_level2(self, item, wide_lo):
            def issue_append(i):
                issue_line.append(i)
                work_field.content_c.append(work_field.content[i])
            run_result = self.normal_page_level2(item, wide_lo)
            if run_result == 'wait':
                return 'wait'
            if self.command_r == 1:
                work_field.current_page = 'error'
                return 'work'
            work_field.content_c = [work_field.content[0], ]
            # check item status
            global issue_line
            issue_line = []
            if len(work_field.content) > 2:
                if item == 'pod':
                    for i in range(1, len(work_field.content)):
                        pod_status = work_field.content[i].split()[1:3]
                        work_state = pod_status[0].split('/')
                        if (pod_status[1] == 'Running'
                           and work_state[0] == work_state[1]):
                            continue
                        if pod_status[1] != 'Completed':
                            issue_append(i)
                elif item in ['deployment', 'statefulset']:
                    for i in range(1, len(work_field.content)):
                        work_state = \
                            work_field.content[i].split()[1].split('/')
                        if work_state[0] != work_state[1]:
                            issue_append(i)
                elif item == 'daemonset':
                    for i in range(1, len(work_field.content)):
                        work_state = work_field.content[i].split()
                        if work_state[1] != work_state[3]:
                            issue_append(i)
                elif item == 'service':
                    for i in range(1, len(work_field.content)):
                        work_state = work_field.content[i].split()[3]
                        if work_state == '<pending>':
                            issue_append(i)
                elif item in ['pvc', 'node']:
                    for i in range(1, len(work_field.content)):
                        work_state = work_field.content[i].split()[1]
                        if work_state not in ['Bound', 'Ready']:
                            issue_append(i)
                work_field.cstate = True
            return 'work'

        def deploy(self):
            return self.state_page_level2('deployment', '-n')

        def pod(self):
            return self.state_page_level2('pod', '-o wide -n')

        def statefulset(self):
            return self.state_page_level2('statefulset', '-n')

        def daemonset(self):
            return self.state_page_level2('daemonset', '-n')

        def service(self):
            return self.state_page_level2('service', '-n')

        def configmap(self):
            return self.normal_page_level2('configmap', '-o wide -n')

        def secret(self):
            return self.normal_page_level2('secret', '-n')

        def hpa(self):
            return self.normal_page_level2('hpa', '-n')

        def pvc(self):
            return self.state_page_level2('pvc', '-n')

        def crd(self):
            return self.normal_page_level2('crd', '-n')

        def node(self):
            return self.state_page_level2('node', '-o wide -n')

        def long_text_handle(self, cmd):
            output = os_run(cmd)[0].split('\n')
            work_field.content = ['--']
            c_width = no_c - 1
            for i in output:
                while len(i) > c_width:
                    content, i = i[:c_width], i[c_width:]
                    work_field.content.append(content)
                work_field.content.append(i)
            work_field.page_init(1, 1)
            return 'work'

        def describe(self):
            if work_field.current_page in work_field.page_level_2:
                item = work_field.current_page
                work_field.current_page = 'describe'
                current_con = (work_field.content
                               [work_field.current_row_no].split()[0])
                cmd = ' '.join([get_cmd('des', item), '-n', work_field.ns,
                               current_con])
                return self.long_text_handle(cmd)
            return 'wait'

        def yaml(self):
            if work_field.current_page in work_field.page_level_2:
                item = work_field.current_page
                work_field.current_page = 'yaml'
                current_con = (work_field.content
                               [work_field.current_row_no].split()[0])
                cmd = ' '.join([get_cmd('get', item), '-o yaml -n',
                               work_field.ns, current_con])
                return self.long_text_handle(cmd)
            return 'wait'

    # define different process state
    def init():
        work_field.reset()
        return 'work'

    def wait_key():
        global action
        action = get_user_action(stdscr)
        return resp_dict[action][0]()

    def work():
        work_field.draw(stdscr)
        return 'wait'

    # process state collections
    state_actions = {
        'init': init,
        'work': work,
        'wait': wait_key
    }

    # init the process
    work_field = workField()
    act_resp = ActResp()
    state = 'init'

    # try action dict to void mutiple if in work function
    # define action dictionary, also page print format info
    resp_dict = {
        'basic': (act_resp.basic,),
        'configmap': (act_resp.configmap,),
        'crd': (act_resp.crd,),
        'deployment': (act_resp.deploy, 5, 60, 10, 11, 10, 10),
        'daemonset': (act_resp.daemonset, 8, 60, 8, 8, 7, 11, 10, 30, 8),
        'describe': (act_resp.describe,),
        'exit': (act_resp.exit,),
        'hpa': (act_resp.hpa,),
        'log': (act_resp.log,),
        'node': (act_resp.node, 6, 30, 10, 25, 10, 20, 20),
        'pod': (act_resp.pod, 7, 60, 7, 10, 10, 5, 18, 38),
        'pvc': (act_resp.pvc, 7, 50, 8, 50, 10, 10, 14, 8),
        'restart': (act_resp.init,),
        'service': (act_resp.service, 5, 50, 13, 16, 16, 53),
        'secret': (act_resp.secret,),
        'statefulset': (act_resp.statefulset, 3, 60, 10, 10),
        'switch': (act_resp.switch_state,),
        'yaml': (act_resp.yaml,),
        'up': (act_resp.up_down,),
        'down': (act_resp.up_down,),
        'enter': (act_resp.enter,)
    }

    while state != 'exit':
        state = state_actions[state]()


# with open('record.log','w+') as f:
#     f.write('output\n')
#     for i in work_field.content: f.write(i + '\n')
#     f.write('output_e\n')
#     for i in output: f.write(i + '\n')
curses.wrapper(main)
