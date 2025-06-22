import streamlit as st
import pandas as pd


def handle_missing_values(df):
    """Обрабатывает пропущенные значения во фрейме данных"""
    st.write("Обрабатка пропущенных значений")
    missing_cols = df.columns[df.isnull().any()].tolist()
    if not missing_cols:
        st.info("Пропущенных значений не обнаружено")
        return df

    if st.button("Удалите все пропущенные значения"):
        df = df.dropna()

    selected_col = st.selectbox(
        "Выберите столбец с пропущенными значениями", missing_cols)
    
    action = st.pills(
         "Как обрабатывать?",
         ["Удаление строк", "Прямое заполнение", "Обратное заполнение",
"Среднее значение заполнения", "Режим заполнения"]
        
    )

    if action == "Продолжить заполнение":
        df[selected_col] = df[selected_col].fillna(method="ffill")
        st.success(
            f"Заполнены пропущенные значения в столбце {selected_col} предыдущим значением")
    elif action == "Заполнение в обратном порядке":
        df[selected_col] = df[selected_col].fillna(method="bfill")
        st.success(
            f"Заполнены пропущенные значения в солбце {selected_col} следующим допустимым значением.")
    elif action == "Удаление строк":
        df = df.dropna(subset=[selected_col])
        st.success(f"Удалены строки с пропущенными значениями в солбце {selected_col}")
    elif action == "Заполнение значения":
        if pd.api.types.is_numeric_dtype(df[selected_col]):
            df[selected_col] = df[selected_col].fillna(df[selected_col].mean())
            st.success(
                f"Заполнены пропущенные значения в столбце {selected_col} средним значением.")
        else:
            st.error("Среднее значение может использоваться только для числовых столбцов")

    elif action == "Режим заполнения":
        mode_value = df[selected_col].mode(
        ).iloc[0] if not df[selected_col].mode().empty else None
        df[selected_col] = df[selected_col].fillna(mode_value)
        st.success(
            f"Заполнены пропущенные значения в столбце {selected_col} значением режима.")

    st.session_state.transformed = True
    return df


def show_null_info(df):
    """Отображает информацию о нулевом значении и сведения о столбце."""
    null_counts = df.isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls > 0:
        st.warning(f"У вас {total_nulls} нулевых значений в наборе данных.")
    else:
        st.info(f"У вас нет нулевых значений в наборе данных.")

    st.dataframe(
        pd.DataFrame({
            "Название": df.columns,
            "Тип данных": df.dtypes,
            "Нулевые строки": null_counts
        }),
        hide_index=True
    )

def download_transformed_data(df):
    """Предоставляет кнопку загрузки для преобразованного фрейма данных."""
    if df.empty:
        st.warning("Данные для загрузки недоступны.")
        return
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Загрузка преобразованных данных в формате CSV",
        data=csv,
        file_name="transformed_data.csv",
        mime="text/csv"
    )


def transform_data(df):
    """Основная функция для преобразования данных."""
    #st.write(":blue-background[Преобразование данных]")
    st.subheader("Преобразование данных")
    if df.empty:
        st.warning("Нет данных для преобразования.")
        return

    df = handle_missing_values(df)
    st.session_state.df = df

    show_null_info(df)
    download_transformed_data(df)
