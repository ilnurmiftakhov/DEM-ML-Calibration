# DEM-ML-Calibration

Репозиторий пилотного исследования по **калибровке DEM-модели угла естественного откоса** с использованием методов **машинного обучения** на малой локальной выборке почвенных образцов.

## Что находится в репозитории

Здесь собраны:
- исходные локальные данные проекта;
- воспроизводимые Python-скрипты для базовых и расширенных экспериментов;
- обученные пилотные модели;
- таблицы метрик, графики и служебные артефакты для анализа;
- краткие рабочие заметки по плану исследования.

**Не включено в репозиторий:** статьи, черновики публикаций и текстовые отчёты для подачи/редакции. Они исключены из Git по отдельному правилу.

---

## Цель проекта

Проверить, можно ли на небольшой объединённой таблице, содержащей:
- свойства почвы,
- параметры DEM,
- экспериментальный угол естественного откоса,
- DEM-оценку угла откоса,

построить пилотный DEM/ML-контур для трёх задач:
1. прогноз `phi_exp` по свойствам почвы;
2. surrogate-модель для `phi_DEM`;
3. прямой прогноз калибровочной ошибки `delta_phi = phi_DEM - phi_exp`.

---

## Ключевые ограничения

- выборка очень мала: **n = 12**;
- результаты следует трактовать как **pilot / proof-of-concept**;
- хорошие метрики LOOCV не означают подтверждённую переносимость на новый тип почвы;
- по `delta_phi` на текущем этапе рабочая прогностическая модель не подтверждена.

---

## Краткие результаты

### Лучшие модели по LOOCV

| Задача | Лучшая модель | RMSE | MAE | R² |
|---|---|---:|---:|---:|
| `phi_exp_soil` | GPR | 1.083 | 0.892 | 0.994 |
| `phi_dem_surrogate` | XGBoost | 3.532 | 2.328 | 0.933 |
| `delta_phi_calibration` | Dummy Mean | 0.648 | 0.567 | -0.190 |

### Главный стресс-тест: перенос на новый тип почвы

| Задача | Лучшая модель | LOOCV MAE | LOGO MAE |
|---|---|---:|---:|
| `phi_exp_soil` | GPR | 0.892 | 8.017 |
| `phi_dem_surrogate` | XGBoost | 2.328 | 9.329 |
| `delta_phi_calibration` | Dummy Mean | 0.567 | 0.553 |

**Вывод:** текущие модели работают прежде всего как локальные интерполяторы внутри уже представленных типов почв. Устойчивая генерализация на новый тип почвы пока не показана.

---

## Структура репозитория

```text
DEM-ML-Calibration/
├── README.md
├── README.en.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── Структура данных.xlsx                  # исходная master-таблица проекта
├── Задачи по DEM модели.docx             # постановка задач и рабочие требования
├── experiments/
│   ├── dem_ml_experiment.py              # базовый воспроизводимый ML-пайплайн
│   ├── dem_ml_article_experiments.py     # расширенные эксперименты для статьи
│   ├── predict_dem_ml.py                 # inference по сохранённым моделям
│   ├── models/                           # обученные пилотные модели
│   ├── templates/                        # шаблоны CSV для инференса
│   ├── results/                          # базовые результаты, графики и метрики
│   └── article_results/                  # bootstrap, ablation, LOGO-аналитика
├── notes/
│   └── plan_DEM_ML.md                    # краткий рабочий план исследования
├── docs/
│   └── summary_for_grant.md              # краткий one-page brief для гранта/демо
├── outputs/                              # исключено из Git: текстовые отчёты
└── papers/                               # исключено из Git: статьи и черновики
```

---

## Быстрый старт

### 1. Клонирование

```bash
git clone git@github.com:ilnurmiftakhov/DEM-ML-Calibration.git
cd DEM-ML-Calibration
```

### 2. Установка зависимостей

Рекомендуемая версия Python: **3.10+**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows PowerShell / cmd
pip install -r requirements.txt
```

### 3. Запуск базового эксперимента

```bash
python experiments/dem_ml_experiment.py
```

### 4. Запуск расширенного набора экспериментов

```bash
python experiments/dem_ml_article_experiments.py
```

### 5. Инференс по сохранённой модели

Пример:

```bash
python experiments/predict_dem_ml.py \
  --task phi_dem_surrogate \
  --input experiments/templates/phi_dem_surrogate_input_template.csv
```

---

## Что генерируют скрипты

### `experiments/dem_ml_experiment.py`
Создаёт:
- sanity-check датасета;
- сравнение моделей по LOOCV;
- holdout-метрики;
- leave-one-soil-type-out метрики;
- permutation importance;
- графики `fact vs prediction`;
- сохранённые `joblib`-модели.

### `experiments/dem_ml_article_experiments.py`
Дополнительно создаёт:
- bootstrap-распределения метрик;
- ablation-анализ признаков;
- сравнение прямого и непрямого прогноза `delta_phi`;
- анализ ошибок surrogate-модели по типам почв;
- агрегированные CSV/PNG для включения в статью и презентацию.

---

## Основные артефакты

### Базовые результаты
- `experiments/results/cv_results.csv`
- `experiments/results/best_models.json`
- `experiments/results/sanity_checks.json`
- `experiments/results/summary.json`

### Расширенные результаты
- `experiments/article_results/bootstrap_summary.csv`
- `experiments/article_results/phi_dem_ablation.csv`
- `experiments/article_results/delta_indirect_vs_direct.csv`
- `experiments/article_results/phi_dem_error_by_soil.csv`
- `experiments/article_results/loocv_vs_logo_mae.png`

### Сохранённые модели
- `experiments/models/phi_exp_soil__gpr.joblib`
- `experiments/models/phi_dem_surrogate__xgboost.joblib`
- `experiments/models/delta_phi_calibration__dummy_mean.joblib`

---

## Репозиторий в формате демонстрации / гранта

Текущая структура уже пригодна для показа в заявке, отчёте по этапу или демонстрации результатов, потому что отделяет:
- **данные проекта** — в корне;
- **воспроизводимый код** — в `experiments/`;
- **машинные артефакты** — в `experiments/models/`;
- **численные результаты и графики** — в `experiments/results/` и `experiments/article_results/`;
- **рабочий план** — в `notes/plan_DEM_ML.md`.

Для формальной подачи или передачи внешним экспертам рекомендуется использовать эту структуру как минимальный release-пакет:
1. `README.md`
2. `README.en.md`
3. `LICENSE`
4. `requirements.txt`
5. `Структура данных.xlsx`
6. `Задачи по DEM модели.docx`
7. папка `experiments/`
8. `notes/plan_DEM_ML.md`
9. `docs/summary_for_grant.md`

---

## Что стоит сделать дальше

1. Расширить выборку до 50–100+ наблюдений.
2. Системно варьировать DEM-параметры по плану эксперимента.
3. Добавить nested CV и bootstrap CI как стандартный этап повторной оценки.
4. Сформировать отдельный master-dataset для следующих циклов DEM-калибровки.
5. После расширения данных повторить попытку моделирования `delta_phi`.

---

## Замечание по интерпретации

Этот репозиторий фиксирует **реальные пилотные результаты**, включая отрицательные:
- отсутствие рабочей модели для `delta_phi`;
- сильное падение качества при leave-one-soil-type-out;
- высокую чувствительность метрик к размеру выборки.

Это сделано намеренно: репозиторий ориентирован не на «косметически красивые» цифры, а на честную воспроизводимую исследовательскую базу для следующего этапа проекта.

---

## Лицензия

См. файл `LICENSE`.

Коротко:
- **код** репозитория распространяется по MIT-лицензии;
- **данные и manuscript-материалы** не считаются автоматически открытыми, если иное не оговорено отдельно.

## Контакты и использование

Если репозиторий используется для гранта, статьи или внутренней демонстрации, рекомендуется ссылаться на конкретные CSV/PNG-артефакты из `experiments/results/` и `experiments/article_results/`, а не только на текстовые выводы.
