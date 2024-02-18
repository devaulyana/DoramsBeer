Dictionary https://github.com/hundredblocks/concrete_NLP_tutorial/blob/master/NLP_notebook.ipynb


Навигация по папкам:

- [base](base) 
  - Эта папка содержит
    - [beer_cosine.ipynb](base/beer_cosine.ipynb) - этот блокнот содержит векторное представление слов с помощью Word2vec и рассчитывается косинусное сходство между векторами для определения самой пивной дорамы.
    - [beer_rating_model_bert](base/beer_rating_model_bert.ipynb) - данный блокнот содержит векторное представление комментариев с помощью BERT и реализацию задачи линейной регрессии для предсказания пивности комментария. Данный метод оказался не достаточно точным MSE: 8.13 R^2: 0.10.
    - [beer_rating_model_spacy_xgb](base/beer_rating_model_spacy_xgb.ipynb) - в этом блокноте реализовано векторное представление комментариев с помощью spaCy, а предсказание рейтинга было осуществлено с помощью модели XGBoost, которая показала отличные результаты! (MSE: 1.01 R^2: 0.99)
      - В папке [models_vector_xgb](base/models_vector_xgb) лежат 2 модели:
        - [spacy_vectorizer](base/models_vector_xgb/spacy_vectorizer.pkl) для векторизации текста.
        - [xgboost_model](base/models_vector_xgb/xgboost_model.joblib) для предсказания пивного рейтинга.
  - [comments_train](base/comments_train.csv) - комментарии для обучения модели. (комментарии и соответственно привные рейтинги)
  - [comments_correct](base/comments_correct.csv) - комментарии спарсенные с в 2021 году для предсказания самой пивной дорамы, данные о дорамах находятся в файле [block](block.csv).
