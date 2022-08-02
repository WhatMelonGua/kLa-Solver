# -*- coding: UTF-8 -*-
import numpy as np

#调用基本函数
def str2num_arr(arr):
    res = []
    for index in range(len(arr)):
        res.append(float(arr[index]))
    return res
def timeSet(arr,num1):
    res = []
    num2 = len(arr)
    if num2 == 2:
        tFrom = float(arr[0])
        tBy = float(arr[1])
        res = np.arange(tFrom,tBy*num1+tFrom,tBy)
    elif num2 == num1:
        for index in range(len(arr)):
            res.append(float(arr[index]))
    else:
        res = None
        print("请检查您的时间输入，与DO数据个数不匹配\nDO数据个数：", num1, "   时间数据个数:", num2)
    return res

# 基本公式 dDO/dt = V_transform = kLa(C_from - C_to)

# 核心求解器
def kLaSolver(DO_r,t,kLa_probe,step,kLa_set,C_abs):
    DO_r = [0.08, 0.14, 0.20, 0.26, 0.32, 0.38, 0.43, 0.49, 0.53, 0.58, 0.62, 0.66, 0.69, 0.72, 0.75, 0.78, 0.80, 0.82,
            0.84, 0.85, 0.86, 0.88, 0.89, 0.91, 0.91, 0.92, 0.93, 0.94, 0.94, 0.95]
    t = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135,
         140, 145, 150, 155]
    tlength = t[-1] - t[0]
    srcData = {}

    for i in range(len(t)):  # 纯入字典一对一，可更改
        srcData[t[i]] = DO_r[i]

    polyFormula = np.polyfit(list(srcData.keys()), list(srcData.values()), 3)  # 对测量数据拟合，以满足 时间布长求解需求

    simData = {t[0]: DO_r[0]}  # 拟合二阶响应 DO-t 数据集

    for i in range(int(tlength / step)):  # 创建 拟合 虚拟对比数据点
        t_v = list(simData.keys())[i] + step
        simData[t_v] = polyFormula[0] * t_v ** 3 + polyFormula[1] * t_v ** 2 + polyFormula[2] * t_v + polyFormula[3]

    # 核心求解代码
    n = 0  # 迭代次数
    simNum = 0.9  # 满足相似阈值的 数据占比（最大为1），在迭代过多时自行下降
    core = [5, 2, 1]  # 虚拟步进倍数,代表的不是时间，是simData间隔 4 单位的时间差，慢慢精细
    perSet = [0.5, 0.2, 0.1]  # 与虚拟步进对应的阈值，求解进此范围表示足够精确，可以进入下一更小的步进量
    kLaCag = [0.0001, 0.00001, 0.000005]  # 对应的kLa调节幅度 s-1
    coreNum = 0  # 虚拟步进取值 索引
    out_step = [1000, 10000, 20000]  # 设置值，最大迭代次数，防止模拟较差无法导出结果
    diff = 1000
    kLa_rem = []
    # while True:                            # 当所有对应值都较好收敛结束求解
    vir_Cp = {t[0]: DO_r[0]}  # 虚拟电极读数DO-t
    vir_Cb = {t[0]: DO_r[0]}  # 虚拟料液DO-t
    diff = {}  # 每步进数据 与 实验数据 差异值
    gap = core[coreNum]  # 步进量
    v_step = list(simData.keys())[gap] - list(simData.keys())[0]  # 虚拟时间步进量 s

    while True:
        up = 0
        down = 0
        passNum = 0
        for i in range(int(len(simData) / gap)):
            vir_Cb[list(vir_Cb.keys())[i] + gap] = list(vir_Cb.values())[i] + kLa_set * (
                        C_abs - list(vir_Cb.values())[i]) * v_step
            vir_Cp[list(vir_Cp.keys())[i] + gap] = list(vir_Cp.values())[i] + kLa_probe * (
                        list(vir_Cb.values())[i] - list(vir_Cp.values())[i]) * v_step
        for i in range(len(vir_Cp)):  # 公式 difs = (模拟值-实际拟合值)/实际拟合值
            difs = (list(vir_Cp.values())[i] - simData[list(vir_Cp.keys())[i]]) / simData[list(vir_Cp.keys())[i]]
            if difs > 0:
                up += 1
            elif difs < 0:
                down += 1
            if abs(difs) <= perSet[coreNum]:
                passNum += 1
            diff[list(vir_Cp.keys())[i]] = abs(difs)
        if passNum / len(vir_Cp) > simNum:  # 整体相似度判断
            if coreNum == 1:
                print("2阶段 步进结果已有一些精确参考价值，在总数据的", round(simNum*100,4), "% 数据点中，满足了差异小于 ", 0.2)
                print("kLa：", kLa_set, "\n——————————————")
            if coreNum < 2:
                simNum = 0.9  # 重置simNum 以得到最好结果
                coreNum += 1
            else:
                print('_____________________')
                print('结果出现，kLa较好值为：', kLa_set)
                print('本次迭代满足整体差异值小于 ', perSet[coreNum], ' 的数据点 占总数据的 ', round(simNum*100,4),"%")
                break
        if up >= down:  # 整体上下调判断
            kLa_set -= kLaCag[coreNum]
        elif up < down:
            kLa_set += kLaCag[coreNum]
        if n > out_step[coreNum]:
            print("模拟步进 ", coreNum + 1, " 阶段因 数据点误差 或 程序设置精密度问题，无法达到 ", round(simNum*100,4), "% 数据占比满足阈值，自动下调2.5%")
            n = 0
            simNum -= 0.025
        n += 1
# 主程序
if __name__ == '__main__':
    # 默认设置求解首选项
    C_abs = 1                                  #溶氧最大(饱和)浓度，一般都是1
    timeStep = 0.2                             # 求解器时间步长，指对 1s 间隔 的 kLa状态进行一次假设、求解
    kLa_set = 0.03                           # 假设kLa（单位 s-1），推荐给出一个近似值，帮助快速收敛，程序将在此值附近逐渐扩大搜寻
    kLa_probe = 0.0245                       # 探头的kLa传氧能力，不同的探头特性不同，求解结果也对此依赖！请实验测得后填入（测量0% 阶跃 100% DO的响应曲线，动态法求得）

    # 存在配置文件读取首选项
    try:
        with open('Set.txt', mode='r') as setFile:
            settings = setFile.read().split('\n')
            for i in range(len(settings)):
                settings[i] = settings[i].split('#')[0]
            timeStep = float(settings[0].split('<timeStep>')[1])
            kLa_probe = float(settings[1].split('<kLa_probe>')[1])
            C_abs = float(settings[1].split('<C_abs>')[1])
        print("配置载入完毕，求解器的\n时间步长 ",timeStep,"s\n电极响应k值 ",kLa_probe,"s-1")
    except:
        print("未检测到正确格式的Set.txt文件，求解器的时间步长(1s)、电极响应k值(0.0245s-1)将按默认值求解")

    # 输入实验数据
    print("制表符隔开的数据，即Excel行内数据直接复制进入软件粘贴即可\n若是竖列排布的数据，请转置为行数据，或自行键入，空格隔开")
    Tab = input("请选择数据分割方式，输入 [0] 为行数据（制表符分割），[1] 为自输入数据（空格分割）：\n")
    DO = input("请输入实验实际测量DO数据组，以 制表符 或 空格 隔开单个数据：\n")
    if Tab == '0':
        DO = DO.split("\t")
    else:
        DO = DO.split(" ")
    DO = str2num_arr(DO)
    time = input("请输入实验设置读数时间，以 制表符 或 空格 隔开单个时间点：\n "
                 "（若您设置了间隔相同时间读数，请输入[开始时间s] [间隔步长s]两个数字即可）\n")
    if Tab == '0':
        time = time.split("\t")
    else:
        time = time.split(" ")
    kLa_set = input("请输入您猜测的kLa值大致范围(单位s-1，不影响最终结果，好的猜测可以使程序求解快速收敛):\n")
    kLa_set = float(kLa_set)
    print("求解开始。。。")
    time = timeSet(time,len(DO))
    result = kLaSolver(DO,time,kLa_probe,timeStep,kLa_set,C_abs)
