import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from Widget import modal
from grouper import DRG_grouper
import datetime
import altair as alt
from Widget.Hydralit import HydraHeadApp


class codingApp(HydraHeadApp):
    def run(self):
        def show_table(df: pd.DataFrame, height):
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_default_column(editable=True)
            if '入院病情' in df.columns:
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

        def show_table_tree(df: pd.DataFrame, height):
            gridOptions = {
                "rowSelection": "single",
                'columnDefs': [
                    {'field': df.columns[2], 'rowGroup': True, 'hide': True},
                    {'field': df.columns[3], 'rowGroup': True, 'hide': True},
                    {'field': df.columns[4], 'rowGroup': True, 'hide': True},
                    {'field': df.columns[5], 'rowGroup': True, 'hide': True},
                    {'field': df.columns[0]},
                ],
                'autoGroupColumnDef': {
                    'headerName': '诊断编码',
                    'field': df.columns[1],
                    'minWidth': 400,
                },
                'groupDisplayType': 'singleColumn'
            }

            selection = AgGrid(
                df,
                gridOptions=gridOptions,
                height=height,
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED
            )
            return selection

        def show_table_dptree(df: pd.DataFrame, height):
            gridOptions = {
                "rowSelection": "single",
                'columnDefs': [
                    {'field': df.columns[2], 'rowGroup': True, 'hide': True},
                    {'field': df.columns[3]},
                ],
                'autoGroupColumnDef': {
                    'headerName': '推荐手术大类',
                    'field': df.columns[4],
                    'minWidth': 400,
                },
                'groupDisplayType': 'singleColumn'
            }

            selection = AgGrid(
                df,
                gridOptions=gridOptions,
                height=height,
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED
            )
            return selection

        @st.cache()
        def base_data_icd10():
            icd_10 = pd.read_csv('resource/icd10.csv', usecols=['诊断编码', '诊断名称', '章的名称', '节名称', '类目名称', '亚目名称'])
            return icd_10

        @st.cache()
        def base_data_icd9():
            icd_9 = pd.read_csv('resource/icd9.csv', usecols=['手术操作编码', '手术操作名称', '章的名称', '节名称', '类目名称', '亚目代码'])
            return icd_9

        @st.cache()
        def base_dn_pr():
            drg_result = pd.read_csv('resource/dn_pr.csv',
                                     usecols=['主要诊断编码', '主要诊断名称', '推荐手术大类', '推荐手术编码', '推荐手术名称', ])
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
        result = base_dn_pr()
        cc = base_cc_list()

        print(result)
        st.subheader('编码辅助工具')
        st.markdown('<p class="label-font">增加症状信息</p>', unsafe_allow_html=True)
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
                selected_icd10 = show_table_tree(icd10, 300)
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
                cc_df = cc[cc['主要诊断编码'] == df['诊断编码'].tolist()[0]]
                cc_df = cc_df[['其他诊断编码', '其他诊断名称', '并发症评级']]
                if len(cc_df) > 0:
                    selected_cc = show_table(cc_df, 300)
                    submit = st.button('确认')
                    if submit:
                        get_data().append({'诊断编码': selected_cc["selected_rows"][0]['其他诊断编码'],
                                           '诊断名称': selected_cc["selected_rows"][0]['其他诊断名称'],
                                           '入院病情': '有'})
                        modal.close('cc_modal')
                        st.experimental_rerun()
                else:
                    st.warning('暂时没有推荐的并发症')
                    cancel = st.button('确认', key='cancel')
                    if cancel:
                        modal.close('cc_modal')

        if delete:
            for i in get_data():
                if set(i.items()).issubset(selected["selected_rows"][0].items()):
                    get_data().remove(i)
            st.experimental_rerun()
        if clear:
            get_data().clear()
            st.experimental_rerun()
        st.subheader('手术信息')
        c1, c2, c3, c4, ce = st.columns([1, 1, 0.8, 1.5, 5.7])
        pr_add = c1.button('新增手术编码', key='pr_add')
        pr_delete = c2.button('删除所选信息', key='pr_delete')
        pr_clear = c3.button('清除列表', key='pr_clear')
        group_search = c4.button('查找常见手术诊断组合', key='search')
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
                selected_icd9 = show_table_tree(icd9, 300)
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

        grouper = st.button('DRG预分组')

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
                print(result)
                if len(result) > 0:
                    selected_combo = show_table_dptree(result, 500)
                    submit = st.button('确认')
                else:
                    st.warning('暂时没有对应手术/诊断推荐的编码组合')
                    cancel = st.button('确认', key='cancel')
                    if cancel:
                        modal.close('group_search')
                if submit:
                    get_data_pr().clear()
                    re_pr_list = selected_combo["selected_rows"][0]['推荐手术编码'].split(',')
                    re_pr_name_list = selected_combo["selected_rows"][0]['推荐手术名称'].split(',')
                    counter = 0
                    for i in re_pr_list:
                        get_data_pr().append({'手术操作编码': re_pr_list[counter],
                                              '手术操作名称': re_pr_name_list[counter]})
                        counter += 1
                    modal.close('group_search')
        if grouper:
            if len(df) < 1:
                st.error('请输入诊疗信息')
            else:
                pr_list_1 = []
                DRG, drg_name, final_ccl, drg_dz, Pccl = DRG_grouper(20, 70, df['诊断编码'].tolist(), df_pr['手术操作编码'].tolist())
                with st.expander('模拟分组结果', expanded=True):
                    st.write('DRG：%s %s' % (DRG, drg_name))
                    st.write('并发症评级：%s' % final_ccl)
                    st.write('权重：%s' % drg_dz)
                    st.write('支付标准：%s' % int(drg_dz * 90.85753))
                    st.write('PCCL：%s' % Pccl)
                    data = [{'类型': '低倍率', '实际医疗费用': 0, '支付标准': 0},
                            {'类型': '低倍率', '实际医疗费用': int(drg_dz * 90.85753 * 0.3), '支付标准': int(drg_dz * 90.85753 * 0.3)},
                            {'类型': '正常倍率', '实际医疗费用': int(drg_dz * 90.85753 * 0.3), '支付标准': int(drg_dz * 90.85753)},
                            {'类型': '正常倍率', '实际医疗费用': int(drg_dz * 90.85753 * 3), '支付标准': int(drg_dz * 90.85753)},
                            {'类型': '高倍率', '实际医疗费用': int(drg_dz * 90.85753 * 3), '支付标准': int(drg_dz * 90.85753)},
                            {'类型': '高倍率', '实际医疗费用': int(drg_dz * 90.85753 * 4), '支付标准': int(drg_dz * 90.85753 * 2)}]
                    df_data = pd.DataFrame(data)

                    lines = alt.Chart(df_data).mark_line().encode(
                        x='实际医疗费用',
                        y='支付标准',
                        color=alt.Color('类型', scale=alt.Scale(scheme='tableau10'))
                    )

                    hover = alt.selection_single(
                        fields=["实际医疗费用"],
                        nearest=True,
                        on="mouseover",
                        empty="none",
                    )

                    points = lines.transform_filter(hover).mark_circle(size=65)

                    tooltips = (
                        alt.Chart(df_data)
                        .mark_rule()
                        .encode(
                            x='实际医疗费用',
                            y='支付标准',
                            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                            tooltip=[
                                alt.Tooltip("实际医疗费用", title="实际医疗费用"),
                                alt.Tooltip("支付标准", title="支付标准"),
                            ],
                        )
                        .add_selection(hover)
                    )

                    st.altair_chart((lines + points + tooltips).interactive(), use_container_width=True)

            for line in open('style.css', encoding='utf-8'):
                st.markdown(f'<style>{line}</style>', unsafe_allow_html=True)
