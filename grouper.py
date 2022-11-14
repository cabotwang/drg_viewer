import re, time
import numpy as np
import pandas as pd
import math


# 特殊分组规则组别
sp_dict = {'AC1-1,AC1-2': 'AC1', 'FB1-1,FB1-2': 'FB1', 'FE1-1,FE1-2': 'FE1', 'FF2-1,FF2-2': 'FF2',
           'IB1-1,IB1-2': 'IB1', 'JA1-1,JA1-2': 'JA1', 'JA1-1,JA1-3,JA1-4': 'JA1', 'JA2-1': 'JA2',
           'JA2-2,JA2-3': 'JA2', 'NA1-1': 'NA1', 'NA1-2,NA1-3': 'NA1'}
mdca = {'37.5100', '50.5100', '50.5100x001', '50.5900x001', '50.5900x004', '50.5900x005', '50.5901', '50.5902', '52.8000',
        '52.8200', '52.8300', '55.6100', '55.6901', '33.5000', '33.5100', '33.5200', '33.6x00', '41.0000', '41.0200',
        '41.0300', '41.0500', '41.0600', '41.0800x001', '41.0100', '41.0401', '41.0701', '41.0900', '37.5200x001', '39.6500',
        '96.7201'}

dn_group = pd.read_json('resource/dn_group.json')
dn_group.set_index(['主诊断编码'], inplace=True)
pr_group = pd.read_json('resource/pr_group.json')
pr_group.set_index(['手术操作编码'], inplace=True)
adrg = pd.read_json('resource/adrg.json')
neike = list(adrg['ADRG'])
DRG_df = pd.read_json('resource/DRG_df.json')
pr_ex = pd.read_json('resource/pr_ex.json')
pr_ex_set = set(pr_ex['手术操作编码'])
cc_list = pd.read_json('resource/cc_list.json')
cc_list.set_index(['ICD-10 code'], inplace=True)
MI = pd.read_json('resource/MI.json')
MI.set_index(['编码'], inplace=True)
pccl_adrg = pd.read_json('resource/pccl_adrg.json')
pccl_adrg = pccl_adrg.set_index('ADRG')
pccl_cc = pd.read_json('resource/pccl_cc.json')
pccl_cc = pccl_cc.set_index('并发症编码')
pccl_matrix = pd.read_json('resource/pccl_matrix.json')
pccl_matrix = pccl_matrix.set_index('序号')
print(pccl_matrix.columns)


def DRG_grouper(age, weight, dn_list, pr_list):
    # PCCL模型
    def PCCL(a_drg, DN_list):
        adrg_pcc_gr = pccl_adrg.loc[a_drg, 'ADRG组别']
        pccl_list = []
        for n in DN_list:
            try:
                cc_pccl_gr = pccl_cc.loc[n[0:5], 'CcRow']
                print(pccl_matrix.loc[cc_pccl_gr, str(adrg_pcc_gr)])
                pccl_list.append(pccl_matrix.loc[cc_pccl_gr, str(adrg_pcc_gr)])
            except KeyError:
                pass
        pccl_list.sort(reverse=True)
        pccl_sum = 0
        for i in range(0, len(pccl_list)):
            pccl_sum += pccl_list[i] * math.exp(-0.4 * (i - 2 + 1))
        if pccl_sum > 5.83:
            pccl_level = 1.25 * 4 / math.log(3 / 0.4) * (pccl_sum / 5.83 - 1) + 3.5
        elif pccl_sum <= 0:
            return 0
        else:
            pccl_level = 4 / math.log(3 / 0.4) * math.log(pccl_sum)
        print(pccl_level)
        return pccl_level

    t1 = time.time()
    print(age, weight, dn_list, pr_list)
    try:
        dn_adrg = str(dn_group.loc[dn_list[0], '修正后诊断组别']).split(',')
        MDC = dn_adrg[10][0]
    except KeyError:
        print('主诊断编码错误')
        return '960', '诊断编码错误', None, 0

    # 多发性创伤判定
    MI_pdl = []
    for i in dn_list:
        try:
            MI_pdl.append(MI.loc[i, '组别'])
        except KeyError:
            pass
    # if 'Y' in MI_pdl:
    #     dn_adrg.extend(['YC1', 'YR1', 'YR2'])
    if len(set(MI_pdl)) >= 2:
        dn_adrg = ['ZB1', 'ZC1', 'ZD1', 'ZJ1', 'ZZ1', 'AH1_1', 'AD1', 'AH1', 'AB1', 'AG2', 'AC1', 'AF1', 'AE1', 'AG1', 'AA1']
        MDC = 'Z'
    elif float(age) < 29/365:
        MDC = 'P'
        for i in dn_list:
            try:
                dn_adrg.extend(dn_group.loc[i, '修正后诊断组别'].split(','))
            except KeyError:
                pass
        dn_adrg = [each for each in dn_adrg if (each[0] == 'P' or each[0] == 'A')]
        weight = float(weight)
        if (weight >= 2500) or (weight < 500):
            dn_adrg = set(dn_adrg) - {'PS1', 'PS2', 'PS3'}
        elif weight >= 2000:
            dn_adrg = set(dn_adrg) - {'PS1', 'PS2'}
        elif weight >= 1500:
            dn_adrg = set(dn_adrg) - {'PS1'}
    elif float(age) <= 1:
        dn_adrg = set(dn_adrg) - {'PB1', 'PC1', 'PJ1', 'PK1', 'PS1', 'PS2', 'PS3', 'PS4', 'PU1'}

    # 形成手术DRG组别
    pr_list_rank = pr_list + ['']
    print(pr_list_rank)
    pr_list = list(set(pr_list) & set(pr_group.index) | {''})
    pr_list.sort(key=pr_list_rank.index)
    if pr_list[0] == '':
        pr_adrg = neike
    elif list(set(pr_list) & set(mdca)):
        pr_adrg = str(pr_group.loc[list(set(pr_list) & set(mdca))[0], '对应ADRG组']).split(',')
    else:
        try:
            pr_adrg = str(pr_group.loc[pr_list[0], '对应ADRG组']).split(',')
        except KeyError:
            print('手术编码错误')
            return '961', '手术编码错误', None, 0
        if '-' in ','.join(pr_adrg):
            try:
                for i in pr_list[1:]:
                    add_adrg = str(pr_group.loc[i, '对应ADRG组']).split(',')
                    add_adrg = [each for each in add_adrg if '-' in each]
                    pr_adrg.extend(add_adrg)
            except KeyError:
                pass
            for key in sp_dict:
                if set(key.split(',')) < set(pr_adrg):
                    pr_adrg.append(sp_dict[key])
            for n in pr_adrg:
                if re.search(r'-', n):
                    pr_adrg.remove(n)

    def ADRG_rank(list_a):
        try:
            new_list = []
            for n in list_a:
                if n[0] in ['A', 'Z']:
                    new_list.append(n)
            if new_list:
                print(new_list)
                return min(new_list)
            else:
                print(list_a)
                return min(list_a)
        except ValueError:
            return 'QY'

    adrg = ADRG_rank(set(dn_adrg) & set(pr_adrg))
    if adrg == 'QY':
        return '%sQY' % MDC, '诊断手术不匹配', None, 0

    # 并发症判定
    dn1_cpt = cc_list.loc[dn_list[0], 'ICD chapter']
    ccl = [0]
    for i in dn_list[1:]:
        try:
            i_cpt = cc_list.loc[i, 'ICD chapter']
            if i_cpt != dn1_cpt:
                ccl.append(cc_list.loc[i, 'CC_list'])
        except KeyError:
            pass
    final_ccl = max(ccl)
    slide_DRG = DRG_df[DRG_df['ADRG'] == adrg]
    if final_ccl == 2:
        DRG = min(list(slide_DRG['DRG']))
    elif final_ccl == 1:
        slide_DRG = slide_DRG[slide_DRG['cc'] > 2]
        DRG = min(list(slide_DRG['DRG']))
    else:
        slide_DRG = slide_DRG[slide_DRG['cc'] > 4]
        DRG = min(list(slide_DRG['DRG']))
    slide_DRG.set_index(['DRG'], inplace=True)
    drg_name = slide_DRG.loc[DRG, 'DRG名称']
    drg_dz = slide_DRG.loc[DRG, '基础点数']
    print(DRG, drg_name, final_ccl, drg_dz)

    pccl = PCCL(adrg, dn_list[1:])
    return DRG, drg_name, final_ccl, drg_dz, pccl


def PCCL(a_drg, DN_list):
    adrg_pcc_gr = pccl_adrg.loc[a_drg, 'ADRG组别']
    pccl_list = []
    for n in DN_list:
        try:
            cc_pccl_gr = pccl_cc.loc[n[0:5], 'CcRow']
            print(pccl_matrix.loc[cc_pccl_gr, str(adrg_pcc_gr)])
            pccl_list.append(pccl_matrix.loc[cc_pccl_gr, str(adrg_pcc_gr)])
        except KeyError:
            pass
    pccl_list.sort(reverse=True)
    pccl_sum = 0
    for i in range(0, len(pccl_list)):
        pccl_sum += pccl_list[i]*math.exp(-0.4*(i-2+1))
    if pccl_sum > 5.83:
        pccl_level = 1.25*4/math.log(3/0.4)*(pccl_sum/5.83-1)+3.5
    elif pccl_sum <= 0:
        return 0
    else:
        pccl_level = 4 / math.log(3 / 0.4) * math.log(pccl_sum)
    print(pccl_level)
    return pccl_level


if __name__ == '__main__':
    # DRG_grouper(20, 70, ['D06.900', 'A49.809'], [])
    PCCL('HT1', ['D36.714',	'A03.900x009', 'N17.900x002', 'J96.000'])
