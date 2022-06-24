import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from Widget import modal

st.set_page_config(layout="wide", initial_sidebar_state='collapsed')

st.header('DRG结果展示平台')


@st.cache(allow_output_mutation=True)
def get_data():
    return {}


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


c1, ce, c2 = st.columns([1, 0.07, 3])
icd10 = pd.read_csv('resource/icd10.csv', usecols=['诊断代码', '诊断名称'])
icd9 = pd.read_csv('resource/icd9.csv', usecols=['手术操作代码', '手术操作名称'])
drg = pd.read_csv('resource/drg.csv', usecols=['ADRG', 'ADRG名称'])
result = pd.read_csv('resource/utl_rate.csv',
                     usecols=['主要诊断编码', '主要诊断名称', '手术编码', '手术名称', 'ADRG', '病案数'])

c1.subheader('搜索信息')
icd10_empty = c1.empty()
try:
    icd_code = icd10_empty.text_input('诊断编码', value=get_data()['icd10'])
except KeyError:
    icd_code = icd10_empty.text_input('诊断编码')
if c1.button("搜索", key='icd10'):
    modal.open('icd10_modal')

icd9_empty = c1.empty()
try:
    icd9_code = icd9_empty.text_input('手术编码', value=get_data()['icd9'])
except KeyError:
    icd9_code = icd9_empty.text_input('手术编码')
if c1.button("搜索", key='icd9'):
    modal.open('icd9_modal')

drg_empty = c1.empty()
try:
    drg_code = drg_empty.text_input('DRG编码', value=get_data()['drg'])
except KeyError:
    drg_code = drg_empty.text_input('DRG编码')
if c1.button("搜索", key='drg'):
    modal.open('drg_modal')

if modal.is_open('icd10_modal'):
    with modal.container('icd10_modal'):
        st.write('请选择icd编码')
        icd10 = icd10[icd10['诊断代码'].str.contains(icd_code)]
        selected = show_table(icd10, 300)
        submit = st.button('确认')
        if submit:
            get_data().update({'icd10': selected["selected_rows"][0]['诊断代码']})
            modal.close('icd10_modal')

if modal.is_open('icd9_modal'):
    with modal.container('icd9_modal'):
        st.write('请选择icd编码')
        icd9 = icd9[icd9['手术操作代码'].str.contains(icd_code)]
        selected = show_table(icd9, 300)
        submit = st.button('确认')
        if submit:
            get_data().update({'icd9': selected["selected_rows"][0]['手术操作代码']})
            modal.close('icd9_modal')

if modal.is_open('drg_modal'):
    with modal.container('drg_modal'):
        st.write('请选择drg编码')
        drg = drg[drg['ADRG'].str.contains(drg_code)]
        selected = show_table(drg, 300)
        submit = st.button('确认')
        if submit:
            get_data().update({'drg': selected["selected_rows"][0]['ADRG']})
            modal.close('drg_modal')

# search_result = c1.button('结果展示')
c2.subheader('结果展示')

if drg_code:
    result = result[result['ADRG'] == drg_code]
if icd_code:
    result = result[result['主要诊断编码'] == icd_code]
if icd9_code:
    result = result[result['手术编码'] == icd9_code]
with c2:
if drg_code or icd_code or icd9_code:
    # st.write(icd_code, icd9_code, drg_code)
    result['使用率'] = result['病案数']/result['病案数'].sum()
    result['使用率'] = result['使用率'].apply(lambda x: r'{:.2%}'.format(x))
    show_table(result, 500)
