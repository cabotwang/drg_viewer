import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from Widget import modal
import datetime

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')
for line in open('style.css', encoding='utf-8'):
    st.markdown(f'<style>{line}</style>', unsafe_allow_html=True)


def show_table(df: pd.DataFrame, height):
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_default_column(editable=True)
    if '入院病情' in df.columns:
        print('a')
        builder.configure_column('入院病情',
                                 cellEditor='agRichSelectCellEditor',
                                 cellEditorParams={'values': ['有', '临床未确定', '情况不明', '无']}
                                 )
        builder.configure_grid_options(enableRangeSelection=True)
    builder.configure_selection("single")
    selection = AgGrid(
        df,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        gridOptions=builder.build(),
        fit_columns_on_grid_load=True,
        height=height,
        theme='light',
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
    )
    return selection


@st.cache()
def base_data_icd10():
    icd_10 = pd.read_csv('resource/icd10.csv', usecols=['诊断编码', '诊断名称'])
    return icd_10


@st.cache()
def base_data_icd9():
    icd_9 = pd.read_csv('resource/icd9.csv', usecols=['手术操作编码', '手术操作名称'])
    return icd_9


@st.cache()
def base_data_drg():
    drg_result = pd.read_csv('resource/utl_rate.csv',
                             usecols=['主要诊断编码', '主要诊断名称', '推荐手术编码', '推荐手术名称', 'ADRG编码', 'ADRG名称', '支付标准'])
    return drg_result


@st.cache()
def base_cc_list():
    cc_result = pd.read_csv('resource/cc_rate.csv',
                             usecols=['主要诊断编码', '主要诊断名称', '其他诊断编码', '其他诊断名称', '并发症评级'])
    return cc_result


@st.cache(allow_output_mutation=True)
def get_data():
    return []


@st.cache(allow_output_mutation=True)
def get_data_pr():
    return []


icd10 = base_data_icd10()
icd9 = base_data_icd9()
result = base_data_drg()
cc = base_cc_list()
with st.sidebar:
    mode = st.radio('可能的编码提示模式', ('模式1', '模式2'))
if mode == '模式1':
    st.subheader('编码辅助工具')
    st.markdown('<p class="label-font">诊断信息</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, ce = st.columns([1, 1, 0.8, 1.5, 5.7])
    add_dn = c1.button('新增诊断编码', key='dn_add')
    delete = c2.button('删除所选信息', key='dn_delete')
    clear = c3.button('清除列表', key='dn_clear')
    cc_add = c4.button('查找常见并发症', key='cc')
    if add_dn:
        modal.open('icd10_modal')
    if modal.is_open('icd10_modal'):
        with modal.container('icd10_modal'):
            st.write('请选择icd编码')
            c1, c2, c3, ce = st.columns([1, 1, 1, 2])
            search_c1 = c1.text_input('请输入icd编码')
            search_c2 = c2.text_input('请输入icd名称')
            search_c3 = c3.selectbox('入院病情', ('有', '临床未确定', '情况不明', '无'))
            if search_c1 != '':
                icd10 = icd10[icd10['诊断编码'].str.contains(search_c1)]
            elif search_c2 != '':
                search_list = search_c2.split(' ')
                for i in search_list:
                    print(i)
                    icd10 = icd10[icd10['诊断名称'].str.contains(i)]
            selected_icd10 = show_table(icd10, 300)
            submit = st.button('确认')
            if submit:
                get_data().append({'诊断编码': selected_icd10["selected_rows"][0]['诊断编码'],
                                   '诊断名称': selected_icd10["selected_rows"][0]['诊断名称'],
                                   '入院病情': search_c3})
                modal.close('icd10_modal')
    df = pd.DataFrame(get_data(), columns=['诊断编码', '诊断名称', '入院病情'])
    df.index = df.index + 1
    df = df.where(df.notnull(), '')
    selected = show_table(df, 250)

    if cc_add:
        if len(df) < 1:
            st.warning('请输入主诊断编码')
        else:
            modal.open('cc_modal')
    if modal.is_open('cc_modal'):
        with modal.container('cc_modal'):
            st.write('是否有以下常见并发症')
            print(df['诊断编码'].tolist()[0])
            cc_df = cc[cc['主要诊断编码'] == df['诊断编码'].tolist()[0]]
            if len(cc_df) > 0:
                selected_cc = show_table(cc_df, 300)
                submit = st.button('确认')
            else:
                st.warning('暂时没有推荐的并发症')
                cancel = st.button('确认', key='cancel')
                if cancel:
                    modal.close('cc_modal')
            if submit:
                get_data().append({'诊断编码': selected_cc["selected_rows"][0]['其他诊断编码'],
                                   '诊断名称': selected_cc["selected_rows"][0]['其他诊断名称'],
                                   '入院病情': '有'})
                modal.close('cc_modal')
                st.experimental_rerun()

    if delete:
        print(get_data())
        print(selected["selected_rows"][0])
        for i in get_data():
            if set(i.items()).issubset(selected["selected_rows"][0].items()):
                get_data().remove(i)
        st.experimental_rerun()
    if clear:
        get_data().clear()
        st.experimental_rerun()

    st.markdown('<p class="label-font">手术信息</p>', unsafe_allow_html=True)
    c1, c2, c3, ce = st.columns([1, 1, 1, 7])
    pr_add = c1.button('新增手术编码', key='pr_add')
    pr_delete = c2.button('删除所选信息', key='pr_delete')
    pr_clear = c3.button('清除列表', key='pr_clear')
    if pr_add:
        modal.open('icd9_modal')
    if modal.is_open('icd9_modal'):
        with modal.container('icd9_modal'):
            st.write('请选择icd编码')
            c1, c2, c3, ce = st.columns([1, 1, 1, 2])
            search_c1 = c1.text_input('请输入icd编码')
            search_c2 = c2.text_input('请输入icd名称')
            search_c3 = c3.date_input('手术时间', datetime.date(2022, 7, 16), key='pr_time')
            if search_c1 != '':
                icd9 = icd9[icd9['手术操作编码'].str.contains(search_c1)]
            elif search_c2 != '':
                search_list = search_c2.split(' ')
                for i in search_list:
                    icd9 = icd9[icd9['手术操作名称'].str.contains(i)]
            selected_icd9 = show_table(icd9, 300)
            submit = st.button('确认')
            if submit:
                get_data_pr().append({'手术操作编码': selected_icd9["selected_rows"][0]['手术操作编码'],
                                      '手术操作名称': selected_icd9["selected_rows"][0]['手术操作名称'],
                                      '手术时间': search_c3.strftime("%Y-%m-%d")})
                modal.close('icd9_modal')

    df_pr = pd.DataFrame(get_data_pr(), columns=['手术操作编码', '手术操作名称', '手术时间'])
    df_pr.index = df_pr.index + 1
    df_pr = df_pr.where(df_pr.notnull(), '')
    selected_pr = show_table(df_pr, 200)
    if pr_delete:
        print(get_data_pr())
        for i in get_data_pr():
            print(selected_pr["selected_rows"][0].items())
            if set(i.items()).issubset(selected_pr["selected_rows"][0].items()):
                get_data_pr().remove(i)
        st.experimental_rerun()
    if pr_clear:
        get_data_pr().clear()
        st.experimental_rerun()

    group_search = st.button('查找常见编码组合')
    # drg_grouper = st.button('模拟分组')
    if group_search:
        if (len(df) == 0) and (len(df_pr)) == 0:
            st.error('请先输入诊断或手术信息')
        else:
            modal.open('group_search')
    if modal.is_open('group_search'):
        with modal.container('group_search'):
            st.write('常见icd编码组合')
            if len(df) > 0:
                result = result[result['主要诊断编码'] == get_data()[0]['诊断编码']]
            if len(df_pr) > 0:
                result = result[result['推荐手术编码'].str.contains(get_data_pr()[0]['手术操作编码'])]
            if len(result) > 0:
                selected_combo = show_table(result, 300)
                submit = st.button('确认')
            else:
                st.warning('暂时没有对应手术/诊断推荐的编码组合')
                cancel = st.button('确认', key='cancel')
                if cancel:
                    modal.close('group_search')
            if submit:
                get_data().clear()
                get_data_pr().clear()
                get_data().append({'诊断编码': selected_combo["selected_rows"][0]['主要诊断编码'],
                                   '诊断名称': selected_combo["selected_rows"][0]['主要诊断名称'],
                                   '入院病情': '是'})
                re_pr_list = selected_combo["selected_rows"][0]['推荐手术编码'].split(',')
                re_pr_name_list = selected_combo["selected_rows"][0]['推荐手术名称'].split(',')
                counter = 0
                for i in re_pr_list:
                    get_data_pr().append({'手术操作编码': re_pr_list[counter],
                                          '手术操作名称': re_pr_name_list[counter]})
                    counter += 1
                modal.close('group_search')



else:
    st.subheader('模式2')
    c1, c2, c3, c4 = st.columns(4)
    dn1_code = c1.text_input('主要诊断编码')
    dn1_name = c2.text_input('主要诊断名称')
    dn2_code = c3.text_input('其他诊断编码')
    dn2_name = c4.text_input('其他诊断名称')
    pr1_code = c1.text_input('主要手术编码')
    pr1_name = c2.text_input('主要手术名称')
    pr2_code = c3.text_input('主要手术编码-1')
    pr2_name = c4.text_input('主要手术名称-1')
