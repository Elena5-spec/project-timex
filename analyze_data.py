import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from io import StringIO

def analyze_data(df):
    st.subheader("Настройка прогноза")
    
    col1, col2 = st.columns(2)
    
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_columns:
        st.error("В данных нет числовых столбцов. Нельзя построить прогноз.")
        return
    
    default_column = numeric_columns[-1]
    
    target_grade = col1.selectbox(
        "Столбец с текущим параметром (только числовые)", 
        numeric_columns,
        index=len(numeric_columns)-1 
    )
    
    if target_grade not in numeric_columns:
        st.error("Выбран нечисловой столбец. Пожалуйста, выберите числовой параметр.")
        return
    
    diploma_threshold = col2.slider("Порог для красного диплома", 3.5, 5.0, 4.75, 0.1)
    
    try:
        y_grade = pd.to_numeric(df[target_grade], errors='coerce')
        if y_grade.isnull().any():
            st.warning(f"Столбец '{target_grade}' содержит нечисловые значения. Они будут заменены на среднее.")
            y_grade = y_grade.fillna(y_grade.mean())
    except Exception as e:
        st.error(f"Ошибка обработки столбца '{target_grade}': {str(e)}")
        return
    
    X = df.drop(columns=[target_grade])
    
    st.subheader("Прогноз успеваемости")
    
    if st.button("Запуск модели"):
        try:
            with st.spinner("Строим прогнозы..."):
                # Преобразование категориальных признаков
                X_processed = pd.get_dummies(X)
                
                X_train, X_test, y_train, y_test = train_test_split(
                    X_processed, y_grade, test_size=0.2, random_state=42
                )
                
                # Модель регрессии для прогноза оценок
                model_grade = RandomForestRegressor(n_estimators=50, random_state=42)
                model_grade.fit(X_train, y_train)
                predictions = model_grade.predict(X_test)
                
                mse = mean_squared_error(y_test, predictions)
                st.info(f"Точность прогноза: RMSE = {np.sqrt(mse):.2f}")
                
                # Модель классификации для прогноза красного диплома
                y_diploma = (y_grade >= diploma_threshold * 20).astype(int)
                model_diploma = RandomForestClassifier(n_estimators=50, random_state=42)
                model_diploma.fit(X_train, y_diploma.loc[X_train.index])
                diploma_predictions = model_diploma.predict(X_test)
                accuracy = accuracy_score(y_diploma.loc[X_test.index], diploma_predictions)
                st.info(f"Точность прогноза красного диплома: {accuracy:.2f}")
                
                # Прогноз оценок для всех студентов
                df["Прогноз оценки"] = model_grade.predict(X_processed)
                
                # Определение групп по фиксированным порогам оценок
                def assign_group(score):
                    if score < 65:
                        return "Зона риска"
                    elif score < 80:
                        return "Зона повышенного риска"
                    else:
                        return "Зона благополучия"
                
                df["Группа"] = df["Прогноз оценки"].apply(assign_group)
                
                # Цвета для групп
                color_map = {"Зона риска": "red", "Зона повышенного риска": "yellow", "Зона благополучия": "green"}
                
                # Расчет процента студентов с прогнозом на красный диплом
                red_diploma_count = (df["Прогноз оценки"] >= diploma_threshold * 20).sum()
                total_students = len(df)
                red_diploma_percent = red_diploma_count / total_students * 100
                st.metric("Прогнозируемый % студентов с красным дипломом", f"{red_diploma_percent:.1f}%")
                
                st.warning("Прогнозная модель не учитывает непредвиденные обстоятельства и изменения в поведении студентов.")
                
                # Визуализация распределения студентов по группам с цветами
                fig = px.histogram(
                    df,
                    x="Прогноз оценки",
                    color="Группа",
                    color_discrete_map=color_map, 
                    title="Распределение студентов по группам"
                )
                st.plotly_chart(fig)
                
                # Рекомендации для групп
                groups_recommendations = {
                    "Зона благополучия": "Участие в научных конференциях; Углублённое изучение профильных предметов; Менторство для других студентов",
                    "Зона повышенного риска": "Дополнительные практические занятия; Фокус на слабых предметах; Работа над проектами в команде",
                    "Зона риска": "Для данной группы студентов рекомендуются индивидуальные консультации с преподавателем; повторение основных тем; регулярные дополнительные занятия"
                }
                
                # В таблице вместо группы выводим рекомендации
                df["Рекомендации"] = df["Группа"].map(groups_recommendations)
                
                # Отобразить таблицу с номером, прогнозом оценки и рекомендациями
                st.subheader("Детали прогноза и рекомендации")
                st.dataframe(df[[target_grade, "Прогноз оценки", "Рекомендации"]].sort_values("Прогноз оценки", ascending=False))
                
                # Подготовка текста рекомендаций для скачивания
                rec_text = ""
                for group, recs in groups_recommendations.items():
                    rec_text += f"{group}:\n"
                    for rec in recs.split("; "):
                        rec_text += f"- {rec}\n"
                    rec_text += "\n"
                
                st.download_button(
                    label="Скачать рекомендации по группам (txt)",
                    data=rec_text,
                    file_name="recommendations.txt",
                    mime="text/plain"
                )
                
                # Кнопка для скачивания полного прогноза в CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Скачать полные результаты (CSV)",
                    data=csv,
                    file_name="student_predictions.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            # Обработка любых ошибок в процессе выполнения
            st.error(f"Ошибка при построении модели: {str(e)}")
            st.info("Попробуйте выбрать другой столбец для прогноза или проверьте данные")
