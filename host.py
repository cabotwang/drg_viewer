import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from Widget import modal
import datetime

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')
icd10 = pd.read_csv('resource/icd10.csv', usecols=['诊断代码', '诊断名称'])
icd9 = pd.read_csv('resource/icd9.csv', usecols=['手术操作代码', '手术操作名称'])
result = pd.read_csv('resource/utl_rate.csv',
                     usecols=['主要诊断编码', '主要诊断名称', '推荐手术编码', '推荐手术名称', 'ADRG编码'])


def show_table(df: pd.DataFrame, height):
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_selection("single")
    selection = AgGrid(
        df,
        # enable_enterprise_modules=True,
        gridOptions=builder.build(),
        fit_columns_on_grid_load=True,
        height=height,
        theme='light',
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )
    return selection


@st.cache(allow_output_mutation=True)
def get_data():
    return []


@st.cache(allow_output_mutation=True)
def get_data_pr():
    return []


with st.sidebar:
    mode = st.radio('可能的编码提示模式', ('模式1', '模式2'))
if mode == '模式1':
    st.subheader('模式1')
    st.markdown('<p class="label-font">诊断信息</p>', unsafe_allow_html=True)
    c1, c2, c3, ce = st.columns([1, 1, 1, 7])
    add_dn = c1.button('新增诊断编码', key='dn_add')
    delete = c2.button('删除所选信息', key='dn_delete')
    clear = c3.button('清除列表', key='dn_clear')
    if add_dn:
        modal.open('icd10_modal')
    if modal.is_open('icd10_modal'):
        with modal.container('icd10_modal'):
            st.write('请选择icd编码')
            c1, c2, c3, ce = st.columns([1, 1, 1, 2])
            search_c1 = c1.text_input('请输入icd编码')
            search_c2 = c2.text_input('请输入icd名称')
            search_c3 = c3.selectbox('是否为入院病情', ('是', '否'))
            if search_c1 != '':
                icd10 = icd10[icd10['诊断代码'].str.contains(search_c1)]
            elif search_c2 != '':
                search_list = search_c2.split(' ')
                for i in search_list:
                    print(i)
                    icd10 = icd10[icd10['诊断名称'].str.contains(i)]
            selected = show_table(icd10, 300)
            submit = st.button('确认')
            if submit:
                get_data().append({'诊断编码': selected["selected_rows"][0]['诊断代码'],
                                   '诊断名称': selected["selected_rows"][0]['诊断名称'],
                                   '入院病情': search_c3})
                modal.close('icd10_modal')

    df = pd.DataFrame(get_data(), columns=['诊断编码', '诊断名称', '入院病情'])
    df.index = df.index + 1
    df = df.where(df.notnull(), '')
    selected = show_table(df, 200)
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
                icd9 = icd9[icd9['手术操作代码'].str.contains(search_c1)]
            elif search_c2 != '':
                search_list = search_c2.split(' ')
                for i in search_list:
                    icd9 = icd9[icd9['手术操作名称'].str.contains(i)]
            selected = show_table(icd9, 300)
            submit = st.button('确认')
            if submit:
                get_data_pr().append({'手术操作编码': selected["selected_rows"][0]['手术操作代码'],
                                      '手术操作名称': selected["selected_rows"][0]['手术操作名称'],
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
                result = result[result['手术操作名称'].str.contains(get_data_pr()[0]['手术操作编码'])]
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
