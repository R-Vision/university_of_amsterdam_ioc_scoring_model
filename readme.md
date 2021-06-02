# О репозитории

Этот репозиторий содержит реализацию алгоритма скоринга индикаторов компрометации, предложенную в исследовании [«Scoring model for IoCs by combining open intelligence feeds to reduce false positives»](https://homepages.staff.os3.nl/~delaat/rp/2019-2020/p55/report.pdf) университета Амстердама на языке Python.

## Термины

* Индикатор компрометации (IoC) — любой технический артефакт, замеченный во вредоносной деятельности (IPv4/v6 адрес, хэш, domain, url, ключ реестра, etc).
* Фид — набор данных с индикаторами компрометации.

## Как это можно использовать?

На ваше усмотрение :)

Время от времени, наша команда в процессе исследований различных продуктовых идей и гипотез разрабатывает прототипы, которые, по нашему мнению, могли бы быть полезными сообществу специалистов по информационной безопасности. Эту модель можно рассматривать как академический проект, а можно прикрутить к собственной системе управления TI для того, чтобы рассчитывать репутацию индикаторов компрометации в ней и на основании оценок принимать решения о дальнейших действиях с IoC.

## Как работает модель?

Модель работает либо с синтетически сгенерированными фидами, либо в фидами, приведенными в формат `csv` следующего вида:  
```| id | value | first_seen | last_seen | relationship_count | detections_count |```  

```none
* id — уникальный id IoC
* value — значение IoС
* first_seen — дата первого появления IoC
* last_seen — дата последнего появления IoC
* relationship_count — количество взаимосвязей (это поле используется для эмуляции показателя количества взаимосвязей текущего IoC с другими IoC или иным контекстом)
* detections_count — количество обнаружений IoC (сколько раз IoC был обнаружен in the wild / в инфраструктуре)
```

Предусловие: для работы модели нужен один или более фид, сгенерированный или приведенный к формату, описанному выше.

При запуске модели, модель проверяет, есть ли уже рассчитанные статистики для фидов, которые были поданы на вход. Если статистик нет, то они рассчитываются. После расчета, записывается хэш всех фидов в директории для того, чтобы пересчитывать статистики каждый раз, когда содержимое фидов изменяется. Статистики необходимы для дальнейших вычислений. Они высчитываются для всех фидов находящихся по пути из переменной `FEED_PATH` расположенной в `calculate.py`: отдельно для индикаторов компрометации (`.iocs-statistics`), отдельно — для фидов (`.feeds-statistics`).

Далее, для каждого индикатора компрометации (каждого фида в директории), начинает расчитываться рейтинг и выдается в виде массива с именами фидов и парами «значений IoC, рейтинг IoC».

Механика расчета отлично описана в исходном исследовании [«Scoring model for IoCs by combining open intelligence feeds to reduce false positives»](https://homepages.staff.os3.nl/~delaat/rp/2019-2020/p55/report.pdf), пересказывать ее нам кажется излишне здесь. В коде, математика расчетов находится в `functions.py`, механика — в `scoring_engine.py`.  

## Ограничения и костыли

* Метрика количества IoC из фидов, входящих в whitelists, генерируется рандомом, так как фиды использованы синтетические — для реальных фидов нужна доработка функции для расчета реальных вхождений фида в whitelists `scoring_engine.py::get_whitelist_overlap_coef()`
* Динамический расчет лямбды для параметра timeliness `funtions.py::calculate_timeliness_sigma()`
* Функция `functions.py::single_feed_ioc_score` отличается от оригинальной из исследования — она в любом случае применяет коэффициент устаревания: `ioc_score * decay_coef if ioc_score else 1 * decay_coef`. Исследование предлагает иной вариант: `ioc_score * decay_coef if ioc_score else 1`
* Есть некоторое количество TODO по коду — они связаны с возможными улучшениями, но мы не стали ими заниматься в виду ограниченности времени, однако будем рады вашим PR.
* Финальный рейтинг в этой модели — int(0..100), тогда как в исследовании — float(0..1). Шкала 0..100 выбрана исключительно для удобства и из-за привычки. Умножение на 100 оригинального рейтинга происходит в `scoring_engine.py::_calculate_iocs_score`: `round(r * 100) for r in feeds_scores]`

## Структура репозитория

* `src/feed_generator` — генератор синтетических фидов для тестирования модели
* `src/feed_generator/data` — тестовые фиды для оценки работы модели
* `src/functions.py` — функции, содержащие формулы, используемые для расчета показателей
* `src/scoring_engine.py` — ядро, занимающееся вычислением скоринга индикаторов для приведенного фида
* `src/calculate_score.py` — точка входа с модель, запускает вычисление скоринга индикаторов компрометации для приведенного фида
* `src/visualization` — тут можно найти python notebooks для визуализации некоторых функций модели, для наглядности

## Как запустить модель?

Из директории /src:

```bash
    Установить все зависимости: `pip install -r requirements.txt`
    Запустить скрипт: `python calculate_score.py <путь до директориии с фидами>`
```

## Благодарности

Огромное спасибо [Чулковой Лере](https://github.com/valeleriee) за интерпретацию формул из исследования, [Саше Зинину](https://github.com/pinkiesky) — за помощь в оптимизации кода по производительности.
