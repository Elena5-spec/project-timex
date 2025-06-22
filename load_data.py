import streamlit as st
import pandas as pd
import os

DTYPE_OPTIONS = ["int64", "float64", "object"]

def show_data_preview(df):
    st.write(":blue-background[Предварительный просмотр данных:]")
    st.write(df.head())
    st.write(
        f":blue-background[Вид:] :orange-background[Строки: {df.shape[0]}]  :orange-background[Столбцы: {df.shape[1]}]"
    )

def show_columns_info(df):
    st.write(":blue-background[Информация о столбцах:]")
    st.write("Здесь вы также можете изменить тип данных столбца/столбцов.")
    null_counts = df.isnull().sum()
    info_df = pd.DataFrame({
        "Название": df.columns,
        "Тип данных": df.dtypes.astype(str),
        "Нулевые строки": null_counts
    })
    edited_dtype_df = st.data_editor(
        info_df,
        column_config={
            "Тип данных": st.column_config.SelectboxColumn(
                "Тип данных",
                options=DTYPE_OPTIONS
            )
        },
        disabled=["Название", "Нулевые строки"],
        hide_index=True,
        key="dtype_editor"
    )
    return edited_dtype_df

def apply_dtype_changes(df, edited_dtype_df):
    for row in edited_dtype_df.itertuples(index=False):
        col, new_dtype = row[0], row[1]
        current_dtype = str(df[col].dtype)
        if new_dtype != current_dtype:
            try:
                df[col] = df[col].astype(new_dtype)
                st.success(f"Изменен столбец {col} на тип данных {new_dtype}")
            except Exception as e:
                st.error(f"Не удалось преобразовать столбец {col} в тип данных {new_dtype}: {e}")

def load_uploaded_file(uploaded_file):
    file_name = uploaded_file.name.lower()
    if file_name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif file_name.endswith(('.xlsx', '.xls')):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Пожалуйста, загрузите корректный файл в формате CSV или Excel.")
        return None

def load_sample_data():
    sample_data_dir = "sample_data"
    files = [f for f in os.listdir(
        sample_data_dir) if f.endswith(('.csv', '.xlsx', '.xls'))]
    if not files:
        st.warning("Файлы с данными не найдены.")
        return None

    info = """
    Данные из KAGGLE: \n
    enhanced_student_habits_performance_dataset.csv
    """
    
    selected_file = st.selectbox(
        "Выберите файл с данными", files, index=0, help=info,
        on_change=lambda: st.session_state.__setitem__('transformed', False))
    sample_path = os.path.join(sample_data_dir, selected_file)

    return sample_path

def load_data():
    #st.write(":blue-background[Загрузите данные:]")
    st.subheader("Загрузка данных")

    uploaded_file = st.file_uploader(
        "Выберите файл CSV или Excel",
        type=["csv", "xlsx", "xls"],
        on_change=lambda: st.session_state.__setitem__('transformed', False)
    )

    sample_data = load_sample_data()

    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()

    if st.session_state.get("transformed", False):
        df = st.session_state.df
        st.session_state.transformed = False
    elif uploaded_file is not None and not st.session_state.get("transformed", False):
        df = load_uploaded_file(uploaded_file)
        if df is not None:
            st.session_state.df = df
    else:
        df = pd.read_csv(sample_data)
        st.session_state.df = df

    df = st.session_state.df
    st.session_state.transformed = False

    if not df.empty:
        show_data_preview(df)
        edited_dtype_df = show_columns_info(df)
        apply_dtype_changes(df, edited_dtype_df)
        st.session_state.df = df
