#### files.get, files.getDrives

Не помню, зачем это добавил, но тут про файлы.

#### settings.get

|`param`|Название настройки|

Возвращает настройку.

#### settings.set

|`param`|Название настройки|
|`value`|Новое значение настройки|

Изменяет настройку.

#### settings.reset

Сбрасывает настройки.

#### collections.get

Возвращает объекты всех коллекций.

#### collections.getById

Возвращает коллекцию по `--id`

#### collections.getCount

Возвращает количество всех коллекций.

#### collections.create

|`name`|Название коллекции|
|`description`|Описание коллекции|
|`innertype`|Тип коллекции|
|`icon_hash`|Название иконки коллекции|
|`add_after`|В какую коллекцию добавить данную коллекцию после создания.|

Создаёт коллекцию и возвращает её объект.

#### collections.edit

|`name`|Новое название коллекции|
|`description`|Новое описание коллекции|
|`innertype`|Новый тип коллекции|
|`icon_hash`|Новое название иконки коллекции|

Редактирует коллекцию и возвращает её объект.

#### collections.delete

|`id`|ID коллекции|

Удаляет коллекцию по ID.

#### collections.switch

|`id1`|ID коллекции, которую нужно переместить|
|`id2`|ID коллекции, на место которой нужно переместить коллекцию 1|

Меняет коллекции местами.

#### collections.getItems

|`id`|ID коллекции|
|`query`|Запрос поиска|
|`page`|Страница пагинации. Для справки, возвращается 10 объектов на страницу.|

Возвращает объекты из коллекции.

#### collections.getItemsCount

|`id`|ID коллекции|
|`query`|Запрос поиска|

Возвращает количество объектов в коллекции.

#### collections.append

|`collection_id`|ID коллекции|
|`entity_id`|ID энтити, которую нужно добавить|

Добавляет entity в коллекцию.

#### entities.globalSearch

|`query`|Запрос поиска|

Поиск по всем entity в базе данных.

#### entities.remove

|`collection_id`|ID коллекции|
|`entity_id`|ID энтити|

Удаляет энтити из коллекции.

#### entities.create

|`collection_id`|ID коллекции, в которую нужно добавить entity после создания.|
|`method`|Название плагина загрузки|
|`display_name`|Необязательно. Имя, которое будет присвоено entity после загрузки|
|`description`|Необязательно. Описание, которое будет присвоено entity после загрузки|

Создаёт энтити по плагину. Список плагинов читай в PLUGINS_RU.md

#### entities.edit

#### entities.changeCollection

#### plugins.get

#### plugins.getActionsForEntity

#### plugins.runAction

#### plugins.runBase

#### plugins.runService

#### log