from cProfile import label
import time
import json
import streamlit as st
from st_aggrid import AgGrid, JsCode

import config


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def gen_js_snippet(metric, stats):
    table_rows = ''
    for stat in stats:
        table_rows += f'''
        '<tr>' + 
            '<td>' + '{stat}' + '</td>' + 
            '<td>' + col["{stat}"] + '</td>' + 
        '</tr>' + '''

    return '''
    function (params) {
        col = ''' + f"JSON.parse(params.data['{metric}']);" + '''
        return (
        '<table>' + 
        ''' + table_rows + '''
        '</table>'
        );
    }'''


def build_grid_options(cols, stats):
    columnDefs = []

    for metric in config.metrics_without_stats:
        columnDef = {
            "field": f"{metric}",
            "resizable": True,
        }
        if metric not in cols:
            columnDef["hide"] = True

        columnDefs.append(columnDef)

    for metric in config.metrics_with_stats:
        columnDef = {
            "field": f"{metric}",
            "cellRenderer": JsCode(gen_js_snippet(metric, stats)).js_code,
            "resizable": True,
        }
        if metric not in cols:
            columnDef["hide"] = True

        columnDefs.append(columnDef)

    return {
        "rowHeight": len(stats) * 30 if len(stats) > 0 else 30,
        "columnDefs": columnDefs,
        "defaultColDef": {
            "filter": True,
        }
    }


@st.cache
def df_to_csv(df):
    return df.to_csv().encode('utf-8')


def read_from_file(file_path):
    with open(file_path, 'r') as openfile:
        data = json.load(openfile)

    return data


def write_to_file(file_path, data):
    with open(file_path, "w") as outfile:
        outfile.write(json.dumps(data))

    return file_path


def date_filter_df(df, start, end, col_name="timestamp"):
    filtered_df = df[df[col_name] >= str(start)]
    filtered_df = filtered_df[filtered_df[col_name] <= str(end)]
    filtered_df = filtered_df.reset_index()

    return filtered_df


def create_stats_obj(count, mean, max, min, sum, variance, upper_quartile, lower_quartile, cumulative=None):
    return json.dumps({
        "count": count,
        "mean": mean,
        "max": max,
        "min": min,
        "sum": sum,
        "variance": variance,
        "upper_quartile": upper_quartile,
        "lower_quartile": lower_quartile,
        "cumulative": cumulative
    })


def data_grid(df, grid_height=300):
    return AgGrid(
        df,
        data_return_mode="filtered_and_sorted",
        update_mode="no_update",
        fit_columns_on_grid_load=True,
        theme="streamlit",
        key=time.time(),
        height=grid_height
    )


def data_download_button(df, file_name, label="Export as CSV"):
    return st.download_button(
        label=label,
        data=df_to_csv(df),
        file_name=f'{file_name}.csv',
        mime='text/csv',
        key=time.time()
    )
