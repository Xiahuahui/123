# -*- coding:utf-8 -*-
import pygraphviz as pgv
class Commitment:                        #定义承诺的结构
    def __init__(self, pre, res, tc):
        self.pre = pre
        self.res = res
        self.tc = tc
    def print_content(self):
        print(self.pre)
        print(self.res + ' ' + self.tc)
class Satement:                              # 定义了状态机中一个合理的状态
    def __init__(self,st_id,status):
        self.st_id = st_id               #系统自动分配的id好以及在转移矩阵中的角标
        self.status = status
    def print_content(self):
        print(self.st_id)
        print(self.status)
               
def create_state_transfers(commitments):   #生成状态机
    st_id = 0
    queue = []               #构造状态队列
    transfers = []           #构造状态转移队列            
    cs = commitments
    nums = len(cs)           # 承诺数量
    status = nums * [1]    # 初始状态 [1, 1, 1, ..., 1, 1]
    for i in range(len(cs)):               #初始下状态机的根节点
        connect = cs[i].pre[0]
        event = cs[i].pre[1]
        if connect == 0 and event == 0:
            status[i]=2
    st=Satement(st_id,status)                  #初始化状态机的节点
    st_id=st_id + 1
    st.print_content()
    queue.append(status)
    # 以bfs顺序建立图结构，图的每个结点是一个承诺状态列表
    while len(queue):
        stats = queue.pop(0)
        # 遍历当前状态中的所有承诺
        (a,b) = createChildrenNodes(cs,stats)  #遍历所有合理子状态
        queue.extend(a) 
        transfers.extend(b)                             
    return transfers
def createChildrenNodes(commitments,stats):#输入合理状态，返回所有子状态
    queue = []
    transfers = []
    cs = commitments
    for i in range(0, len(stats)):
        c_stat = stats[i]
        if c_stat == 1 :    #   如果状态是 1 激活 则可进行转移
            (a,b) = handel_act(cs,stats,i)     #返回的是当前状态的子状态以及转移矩阵
            queue.extend(a)                  #将子状态加入状态队列
            transfers.extend(b)             #将状态转移矩阵加入转移队列
        elif c_stat == 2:     #如果为就绪态可以分为两种情况（1）到达满足状态，（2）到达违约状态
            (a,b) = handel_bas(cs,stats,i)    #返回的是当前状态的子状态以及转移矩阵
            queue.extend(a)                    #将子状态加入状态队列
            transfers.extend(b)                  #将状态转移矩阵加入转移队列
    return (queue,transfers)                                       
def handel_act(commitments,stats,i): #输入合理状态，以及状态要转移的承诺的标号 返回该状态所有合理子状态，以及状态转移队列                  
    queue = []
    transfers = []
    cs = commitments
    connect = cs[i].pre[0]     #查看承诺i的前提与事件
    event = cs[i].pre[1]
    #我们把状态为1的承诺分成两类 
    #（1）前提中不依赖其他承诺的即承诺前提中不含有其他承诺
    #（2）前提中依赖其他承诺的即承诺中含有其他承诺的
    if connect == 0:        #在情况（1）中 承诺为激活态时必须是含有前提动作的  其实这种情况只适用于根节点
        new_stats1 = list(stats)
        new_stats2 = list(stats)
        new_stats1[i] = 2              # 当前提动作到达时则状态变为2
        new_stats2[i] = 5               # 当前提动作没有按时到达时则变为5
        transfers.append([stats, new_stats1, event])   # 将状态转化存入状态转移表
        queue.append(new_stats1)
        transfers.append([stats, new_stats2, 'exp-'+event])
        queue.append(new_stats2)
    elif connect :                  #如果前提中含有其他承诺 这种情况也可以分为两种情况即（1）条件满足 （2）条件不满足
        con_id = int(connect[0])
        con_stat = int(connect[1])
        stat = stats[con_id]
        if stat != con_stat :      #如果前提中承诺状态不满足 
            if con_stat == 3 or con_stat == 4:
                if stat != 1 and stat != 2:
                    new_stats1 = list(stats)
                    new_stats1[i] = 5
                    transfers.append([stats, new_stats1, 'what'])
                    queue.append(new_stats1)
            if con_stat == 5:
                if stat != 1:
                    new_stats1 = list(stats)
                    new_stats1[i] = 5
                    transfers.append([stats, new_stats1, 'what'])
                    queue.append(new_stats1)                              
        if stat == con_stat :  #当前提满足时则可置为2
            new_stats2 = list(stats)
            new_stats2[i] = 2
            transfers.append([stats, new_stats2, 'what'])
            queue.append(new_stats2)
    return (queue,transfers)
def handel_bas(commitments,stats,i):#输入合理状态，以及状态要转移的承诺的标号 返回该状态所有合理子状态，以及状态转移队列                  
    queue = []
    transfers = []
    cs = commitments
    new_stats1 = list(stats)
    new_stats2 = list(stats)
    new_stats1[i] = 3  	#[1]前提动作按时完成            
    new_stats2[i] =4   #[2]前提动作没有按时完成
    transfers.append([stats, new_stats1, cs[i].res])   
    queue.append(new_stats1)
    transfers.append([stats, new_stats2, 'vio-'+cs[i].res])
    queue.append(new_stats2)
    return (queue,transfers)
     
def painting(transfers):
    G = pgv.AGraph(directed=True, strict=True, encoding='UTF-8')
    G.graph_attr['epsilon']='0.001'
    s = set({})
    for transfer in transfers:
        s.add(str(transfer[0]))
        s.add(str(transfer[1]))

    for node in list(s):
        G.add_node(node)

    for transfer in transfers:
        G.add_edge(str(transfer[0]), str(transfer[1]))

    G.layout('dot')
    G.draw('a.png')
# /anaconda/bin/python 
if __name__ == '__main__':
    c0 = Commitment([0, 'buy'], 'res0', '2017')
    c1 = Commitment(['05', 0], 'res1', '2018')
    c2 = Commitment(['13', 0], 'res2', '2019')
    c3 = Commitment(['24', 0], 'res3', '2020')
    c4 = Commitment(['33', 0], 'res3', '2020')
    c5 = Commitment(['33', 0], 'res3', '2020')
    c6 = Commitment(['44', 0], 'res3', '2020')
    c7 = Commitment(['54', 0], 'res3', '2020')
    c8 = Commitment(['63', 0], 'res3', '2020')

    cs = [c0,c1]

    transfers = create_state_transfers(cs)
    
    for line in transfers:
        print(line)
    
    #print(len(transfers))
    painting(transfers)
    #create_fsm('134', '123')


    
