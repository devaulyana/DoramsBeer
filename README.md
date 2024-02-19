Dictionary https://github.com/hundredblocks/concrete_NLP_tutorial/blob/master/NLP_notebook.ipynb


## Навигация по папкам:

### [base](base)

- **[beer_cosine.ipynb](base/beer_cosine.ipynb):**
  - Векторное представление слов с использованием Word2vec и расчет косинусного сходства для определения самой пивной дорамы.

- **[beer_rating_model_bert.ipynb](base/beer_rating_model_bert.ipynb):**
  - Векторное представление комментариев с использованием BERT и реализация задачи линейной регрессии для предсказания пивности комментария. Метод не достаточно точен (MSE: 8.13, R^2: 0.10).

- **[beer_rating_model_spacy_xgb.ipynb](base/beer_rating_model_spacy_xgb.ipynb):**
  - Векторное представление комментариев с использованием spaCy, предсказание рейтинга с использованием модели XGBoost. Отличные результаты! (MSE: 1.01, R^2: 0.99)
    - **[models_vector_xgb](base/models_vector_xgb):**
      - [spacy_vectorizer.pkl](base/models_vector_xgb/spacy_vectorizer.pkl): Модель для векторизации текста.
      - [xgboost_model.joblib](base/models_vector_xgb/xgboost_model.joblib): Модель для предсказания пивного рейтинга.

- **[comments_train.csv](base/comments_train.csv):**
  - Комментарии для обучения модели (комментарии и соответствующие пивные рейтинги).

- **[comments_correct.csv](base/comments_correct.csv):**
  - Комментарии, спарсенные в 2021 году для предсказания самой пивной дорамы. Данные о дорамах находятся в файле [block.csv](base/block.csv).

### [gan_comment](gan_comment)

- **[training_checkpoints](gan_comment/training_checkpoints):**
  - Чекпоинты модели.

- **[comments_train.csv](base/comments_train.csv):**
  - Комментарии для обучения модели (комментарии и соответствующие пивные рейтинги).

- **[gan_model.ipynb](gan_comment/gan_model.ipynb):**
  - Блокнот, в который внедрена генеративная модель GAN для генерации комментариев (тест).

- **[model_after_generation_0.h5](gan_comment/model_after_generation_0.h5):**
  - Модель после генерации.

- **[model_after_weights.h5](gan_comment/model_after_weights.h5):**
  - Веса модели после генерации.

### [pars_dorams](pars_dorams)

- **[pars_dorams_postsql.py](pars_dorams/pars_dorams_postsql.py):**
  - Скрипт для парсинга информации из сайтов в PostgreSQL.
