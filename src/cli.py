import time
import platform
from pathlib import Path
from components.utils import utils
from components.logger import logger
from components.db import db, Collection, Entity, Relation
from components.settings import settings
from components.file_manager import file_manager
from components.consts import consts
from plugins import load_plugins

args = utils.parse_args()

match args.get('act'):
    case None:
        print('"--act" not passed.')
    
    # FILES

    case 'files.get':
        if 'path' not in args:
            print('"--path" is not passed.')
        else:
            path = args.get('path')
            offset = args.get('offset')
            if args.get('offset') is None:
                offset = 0
            
            limit = args.get('limit')
            if args.get('limit') is None:
                limit = 10

            only_path = True
            if 'extended' not in args or args.get('extended') == "0":
                only_path = False

            try:
                files, total_count, return_count, has_more = file_manager.getFolderItems(path, offset=int(offset), limit=int(limit), extended=only_path)
                print('Offset: {0}'.format(offset))
                print('Limit: {0}'.format(limit))
                print('Total count: {0}'.format(total_count))
                print('Count: {0}'.format(return_count))
                print('Has more files: {0}'.format(has_more))
                print('Files:\n')
                for file in files:
                    print(file.takeInfo())
            except FileNotFoundError:
                print("Dir not found")
            except NotADirectoryError:
                print("Not a dir.")
    case 'files.getDrives':
        drives = file_manager.getPartitions()
        for drive in drives:
            print(drive.takeInfo())
        
    # SETTINGS

    case "settings.get":
        if 'param' in args:
            print(settings.get(args['param']))
        else:
            print('Pass \'--param\' arg.')
    case "settings.set":
        if 'param' in args and 'value' in args:
            settings.set(args.get('param'), args['value'])
            print('Setting "{0}" was changed to "{1}"'.format(args['param'], args['value']))
        else:
            print('Pass \'--param\' and \'--value\' to change setting.')
    case "settings.reset":
        settings.reset()
        print('Settings was reset.')

    # COLLECTIONS

    case "collections.get":
        for col in Collection.getAll():
            print(str(col.takeInfo()) + '\n---')
    case "collections.getCount":
        print(Collection.getAllCount())
    case 'collections.create':
        if 'name' not in args:
            print('Error: "--name" not passed')
            exit()

        col = Collection()
        col.name = args.get('name')
        col.description = args.get('description')

        if args.get('innertype') != None:
            col.innertype = args.get('innertype')

        if args.get('icon_hash') != None:
            col.icon_hash = args.get('icon_hash')
        
        col.order = Collection.getAllCount()
        if args.get('add_after') != None:
            col.hidden = 1
        
        col.save(force_insert=True)

        if args.get('add_after') != None:
            to_add = Collection.get(args.get('add_after'))
            to_add.addItem(col)
        
        print(col.takeInfo())
    case 'collections.getById':
        if 'id' not in args:
            print('Error: "--id" not passed')
        else:
            collection = Collection.get(args.get('id'))
            if collection != None:
                print(collection.takeInfo())
            else:
                print("Not found")
    case 'collections.edit':
        if 'id' not in args:
            print('Error: "--id" not passed')
        else:
            collection = Collection.get(args.get('id'))
            if collection != None:
                if 'name' in args:
                    collection.name = args.get('name')

                if 'description' in args:
                    collection.description = args.get('description')
                
                if 'order' in args:
                    collection.order = args.get('order')
                                    
                if 'innertype' in args:
                    collection.innertype = args.get('innertype')
                                                            
                if 'icon_hash' in args:
                    collection.icon_hash = args.get('icon_hash')

                collection.edited_at = time.time()
                collection.save()
                print(collection.takeInfo())
            else:
                print("Not found")
    case 'collections.delete':
        if 'id' not in args:
            print('Error: "--id" not passed')
        else:
            collection = Collection.get(args.get('id'))
            if collection != None:
                collection.delete_instance(recursive=True)
                print('Deleted')
            else:
                print("Not found")        
    case 'collections.switch':
        if 'id1' not in args and 'id2' not in args:
            print('Error: "--id1" and "--id2" are not passed')
        else:
            collection_1 = Collection.get(args.get('id1'))
            collection_2 = Collection.get(args.get('id2'))

            if collection_1 != None and collection_2 != None:
                collection_1.switch(collection_2)
                print('Switched')
            else:
                print("Not found")
    case 'collections.getItems':
        if 'id' not in args:
            print('Error: "--id" not passed')
        else:
            collection = Collection.get(args.get('id'))
            if collection != None:
                search_options = {
                    "query": args.get('query'),
                    "name_search": int(args.get('name_search') if args.get('name_search') else 0),
                    "description_search": int(args.get('description_search') if args.get('description_search') else 0)
                }

                for col in collection.getItems(page=args.get('page'), query_options=search_options):
                    print(str(col.takeInfo()) + '\n---')
            else:
                print("Not found")
    case 'collections.getItemsCount':
        if 'id' not in args:
            print('Error: "--id" not passed')
        else:
            collection = Collection.get(args.get('id'))
            if collection != None:
                search_options = {
                    "query": args.get('query'),
                    "name_search": int(args.get('name_search') if args.get('name_search') else 0),
                    "description_search": int(args.get('description_search') if args.get('description_search') else 0)
                }

                print(collection.getItemsCount(query_options=search_options))
            else:
                print("Not found")
    case 'collections.append':
        if 'collection_id' not in args and 'entity_id' not in args:
            print('Error: "--collection_id" and "--entity_id" are not passed')
        else:
            id = args.get('entity_id')
            collection = Collection.get(args.get('collection_id'))
            entity = Entity.get(id)

            if collection == None or entity == None:
                print("Not found")
                exit()

            try:
                collection.addItem(entity)
            except ValueError:
                print("Error: Entity does not belows to collection")
    
    # ENTITIES

    case 'entities.globalSearch':
        if 'query' not in args:
            print('Error: "--query" not passed')
        else:
            search_options = {
                "query": args.get('query'),
                "name_search": int(args.get('name_search') if args.get('name_search') else 0),
                "description_search": int(args.get('description_search') if args.get('description_search') else 0)
            }

            for col in Entity.search(page=args.get('page'), query_options=search_options):
                print(str(col.takeInfo()) + '\n---')
    case 'entities.remove':
        if 'collection_id' not in args or 'entity_id' not in args:
            print('Error: "--collection_id" and "--entity_id" are not passed')
        else:
            collection = Collection.get(args.get('collection_id'))
            entity = Entity.get(args.get('entity_id'))

            if collection != None and entity != None:
                try:
                    collection.removeItem(entity=entity,delete_entity=True)
                except ValueError as e:
                    print(e)
            else:
                print("Not found")

    case 'entities.create':
        if 'collection_id' not in args:
            print('Pass "collection_id" to upload')
            exit()

        collection = Collection.get(args.get('collection_id'))
        if 'method' not in args:
            print('"--method" not passed')
            exit()
        
        if 'input_data' not in args:
            print('"--input_data" not passed')
            exit()
        
        method = args.get('method')
        input_data = args.get('input_data')
        plugins = load_plugins('upload_plugins')
        instance = None
        try:
            instance = plugins[method]()
        except KeyError:
            print('Plugin not found')
            exit()
        
        entity = instance.run(input_data=input_data)
        if 'display_name' in args:
            entity.display_name = args.get('display_name')
        
        entity.save()

        # Renaming moved file
        entity_path = entity.getDirPath()

        file_final_path = Path(Entity.getTempPath() + '\\' + entity.original_name)
        file_final_path_replace = str(entity_path) + '\\' + str((str(entity.id) + '.' + entity.format))
        file_final_path.rename(file_final_path_replace)

        collection.addItem(entity)
        print(entity.takeInfo())
    case 'entities.edit':
        if 'id' not in args:
            print('"--id" was not passed')
            exit()

        entity = Entity.get(args.get('id'))
        if args.get('name') != None:
            entity.display_name = args.get('name')
        
        if args.get('description') != None:
            entity.description = args.get('description')
             
        if args.get('innertype') != None:
            entity.innertype = args.get('innertype')

        if args.get('icon_hash') != None:
            entity.icon_hash = args.get('icon_hash')

        entity.edited_at = time.time()
        entity.save()
    case 'entity.changeCollection':
        if 'new_collection_id' not in args or 'entity_id' not in args:
            print('"new_collection_id" and "entity_id" are not passed')
            exit()

        collection = Collection.get(args.get('new_collection_id'))
        if collection == None:
            print('Invalid collection')
        entity = Entity.get(args.get('entity_id'))
        if entity == None:
            print('Invalid entity')
        
        old_collection = Collection.get(entity.collection_id)
        old_collection.removeItem(entity=entity,delete_entity=False)
        collection.addItem(entity)

        entity.save()

    # PLUGINS

    case 'plugins.getActions':
        plugins = load_plugins('action_plugins')
        for plugin in plugins:
            plugin_class = plugins[plugin]
            print(plugin_class.name + '|' + plugin_class.action + '|' + str(plugin_class.allow_extensions))
    case 'plugins.getActionsForEntity':
        if 'mid' not in args:
            print('Pass "mid" like "[type]_[id]"')
            exit()
        
        type, id = tuple(args.get('mid').split('_'))
        plugins = load_plugins('action_plugins')
        entity = None
        if type == "collection":
            entity = Collection.get(id)
        elif type == 'entity':
            entity = Entity.get(id)

        if entity == None:
            print('No entity')
            exit()
        
        final_plugins = []
        for plug in plugins:
            plugin = plugins[plug]()
            if plugin.allow_type != type:
                continue

            if '*' in plugin.allow_extensions:
                final_plugins.append(plugin)
            else:
                if entity.format in plugin.allow_extensions:
                    final_plugins.append(plugin)

        for plugin in final_plugins: 
            print(plugin.name + '|' + str(plugin.allow_extensions) + '|' + plugin.allow_type + '|' + plugin.action)
    case 'plugins.runAction':
        if 'mid' not in args:
            print('Pass "mid" like "[type]_[id]"')
            exit()

        if 'plugin' not in args:
            print('"plugin" was not passed')
            exit()
        
        plugin = args.get('plugin')
        plugins = load_plugins('action_plugins')
        type, id = tuple(args.get('mid').split('_'))

        entity = None
        if type == "collection":
            entity = Collection.get(id)
        elif type == 'entity':
            entity = Entity.get(id)

        class_plugin = plugins.get(plugin)
        if class_plugin == None:
            print("Plugin was not found")
            exit()

        class_plugin_ex = class_plugin()
        print(class_plugin_ex.run(input_entity=entity,input_data=args.get('input_data')))
    case 'plugins.runService':
        if 'service' not in args:
            print('"service" was not passed')
            exit()

        service_name = args.get('service')
        input_data = args.get('input_data')
        plugins = load_plugins('services_plugins')
        service = plugins.get(service_name)
        if service == None:
            print("Service was not found")
            exit()

        service_ex = service()
        service_ex.start(input_data=input_data)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            service_ex.stop()
        pass
    case 'plugins.getServices':
        plugins = load_plugins('services_plugins')
        for plugin in plugins:
            plugin_class = plugins[plugin]
            print(plugin_class.name + '|' + str(plugin_class.interval))
    case 'plugins.getUpload':
        plugins = load_plugins('upload_plugins')
        for plugin in plugins:
            plugin_class = plugins[plugin]
            print(plugin_class.name + '|' + plugin_class.format)
    case 'log':
        logger.log(args.get('section'), args.get('name'), args.get('message'))
    case _:
        print('Unknown "--act" passed')